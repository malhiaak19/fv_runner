from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any


def load_metadata_files(metadata_dir: Path) -> list[Path]:
    return sorted(metadata_dir.glob("*.json"))


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def read_text(path: Path) -> str:
    with path.open("r", encoding="utf-8", errors="replace") as f:
        return f.read()


def parse_result(log_text: str) -> str:
    if "The designs are equivalent." in log_text:
        return "equivalent"
    if "Design equivalence inconclusive" in log_text:
        return "inconclusive"
    if "FAIL (unsolved)" in log_text:
        return "fail_unsolved"
    return "unknown"


def parse_compare_summary(log_text: str) -> tuple[int | None, int | None, int | None]:
    m = re.search(r"-- COMPARE-SUMMARY:\s*HOLD=(\d+)\s+FAIL=(\d+)\s+OPEN=(\d+)", log_text)
    if m:
        return int(m.group(1)), int(m.group(2)), int(m.group(3))

    m = re.search(r"-R-\s+Outputs:\s+HOLD=(\d+)\s+OPEN=(\d+)", log_text)
    if m:
        return int(m.group(1)), 0, int(m.group(2))

    m = re.search(r"-R-\s+Outputs:\s+HOLD=(\d+)", log_text)
    if m:
        return int(m.group(1)), 0, 0

    return None, None, None

def parse_design_contains(log_text: str) -> dict[str, int | None]:
    pattern = re.compile(
        r"Design contains:\s+(\d+)\s+inputs,\s+(\d+)\s+states,\s+(\d+)\s+outputs,\s+(\d+)\s+clock inputs,\s+(\d+)\s+generated clocks\."
    )
    matches = pattern.findall(log_text)

    result = {
        "golden_inputs": None,
        "golden_states": None,
        "golden_outputs": None,
        "golden_clock_inputs": None,
        "golden_generated_clocks": None,
        "revised_inputs": None,
        "revised_states": None,
        "revised_outputs": None,
        "revised_clock_inputs": None,
        "revised_generated_clocks": None,
    }

    if len(matches) >= 1:
        g = list(map(int, matches[0]))
        result.update({
            "golden_inputs": g[0],
            "golden_states": g[1],
            "golden_outputs": g[2],
            "golden_clock_inputs": g[3],
            "golden_generated_clocks": g[4],
        })

    if len(matches) >= 2:
        r = list(map(int, matches[1]))
        result.update({
            "revised_inputs": r[0],
            "revised_states": r[1],
            "revised_outputs": r[2],
            "revised_clock_inputs": r[3],
            "revised_generated_clocks": r[4],
        })

    return result

def parse_mapped_targeting(log_text: str) -> dict[str, int | None]:
    inputs_match = re.search(r"Mapped targeting phase inputs:\s+(\d+)\.", log_text)
    outputs_match = re.search(r"Mapped targeting phase outputs:\s+(\d+)\.", log_text)

    return {
        "mapped_target_inputs": int(inputs_match.group(1)) if inputs_match else None,
        "mapped_target_outputs": int(outputs_match.group(1)) if outputs_match else None,
    }

def parse_compare_setup(log_text: str) -> dict[str, str | int | None]:
    compare_style = None

    if "Running 'basic' combinational compare." in log_text:
        compare_style = "basic_combinational_compare"
    elif "Use computed compare point complexity for scheduling compare points." in log_text:
        compare_style = "compare_point_complexity"

    solved_match = re.search(r"(\d+)\s+compare points already solved\.", log_text)

    return {
        "compare_style": compare_style,
        "pre_solved_compare_points": int(solved_match.group(1)) if solved_match else 0,
    }

def parse_output_complexity(log_text: str) -> dict[str, int | None]:
    pattern = re.compile(
        r"Outputs\s*:\s*"
        r"(\d+)\s+total\s+\((\d+)\s+hard,\s+(\d+)\s+non-hard\),\s*"
        r"(\d+)\s+hold\s+\((\d+)\s+hard,\s+(\d+)\s+non-hard\),\s*"
        r"(\d+)\s+fail\s+\((\d+)\s+hard,\s+(\d+)\s+non-hard\),\s*"
        r"(\d+)\s+open\s+\((\d+)\s+hard,\s+(\d+)\s+non-hard\)"
    )

    matches = pattern.findall(log_text)

    result = {
        "complexity_total": None,
        "complexity_hard": None,
        "complexity_non_hard": None,
        "complexity_hold": None,
        "complexity_hold_hard": None,
        "complexity_hold_non_hard": None,
        "complexity_open": None,
        "complexity_open_hard": None,
        "complexity_open_non_hard": None,
    }

    if matches:
        vals = list(map(int, matches[-1]))  # use last/final occurrence
        result.update({
            "complexity_total": vals[0],
            "complexity_hard": vals[1],
            "complexity_non_hard": vals[2],
            "complexity_hold": vals[3],
            "complexity_hold_hard": vals[4],
            "complexity_hold_non_hard": vals[5],
            "complexity_open": vals[9],
            "complexity_open_hard": vals[10],
            "complexity_open_non_hard": vals[11],
        })

    return result


def parse_engines_comb(log_text: str, metadata_engines: Any) -> str:
    m = re.search(r"EXPERIMENT_ENGINES_COMB_AFTER=(.+)", log_text)
    if m:
        return m.group(1).strip()

    if metadata_engines is None:
        return "unknown"

    if isinstance(metadata_engines, list):
        return "{" + " ".join(str(x) for x in metadata_engines) + "}"

    return str(metadata_engines)

def parse_runtime(log_text: str) -> str | None:
    real_matches = re.findall(r"System - .*?total REAL time used\.", log_text)
    cpu_matches = re.findall(r"System - .*?total CPU time.*", log_text)
    orch_matches = re.findall(r"Total time taken by Orchestrator - .*?sec", log_text)

    if real_matches:
        return real_matches[-1].strip()
    if cpu_matches:
        return cpu_matches[-1].strip()
    if orch_matches:
        return orch_matches[-1].strip()
    return None

def parse_timeout(log_text: str) -> bool:
    return "Time limit exceeded!" in log_text


def parse_used_orchestration(log_text: str) -> bool | None:
    if "using orchestrator flow" in log_text:
        return True
    if "Disabling Orchestrator flow due to env 'DONT_USE_ORCHESTRATOR_FLOW'" in log_text:
        return False
    return None


def parse_behavior_tag(log_text: str, result: str, timed_out: bool, open_count: int | None, tool_runtime_sec: int | None) -> str:
    if timed_out and (open_count or 0) > 0:
        return "timeout_stall"
    if "Still verifying" in log_text and result == "equivalent":
        return "completed"
    return "normal"

def build_row(metadata: dict[str, Any], metadata_path: Path) -> dict[str, Any]:
    log_path = Path(metadata["log_path"])
    log_text = read_text(log_path)

    result = parse_result(log_text)
    hold, fail, open_count = parse_compare_summary(log_text)
    timed_out = parse_timeout(log_text)
    runtime = parse_runtime(log_text)
    engines_comb = parse_engines_comb(log_text, metadata.get("engines_comb"))

    design_info = parse_design_contains(log_text)
    mapped_info = parse_mapped_targeting(log_text)
    compare_info = parse_compare_setup(log_text)
    complexity_info = parse_output_complexity(log_text)

    return {
        "run_id": metadata.get("run_id"),
        "design_name": metadata.get("design_name"),
        "mode": metadata.get("variant_name"),
        "engines_comb": engines_comb,
        "runtime": runtime,
        "result": result,
        "hold": hold,
        "fail": fail,
        "open": open_count,
        "timed_out": timed_out,
        **design_info,
        **mapped_info,
        **compare_info,
        **complexity_info,
        "log_path": str(log_path),
    }


def write_csv(rows: list[dict[str, Any]], out_path: Path) -> None:
    if not rows:
        return

    fieldnames = list(rows[0].keys())
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    metadata_dir = project_root / "results" / "metadata"
    output_dir = project_root / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for metadata_path in load_metadata_files(metadata_dir):
        metadata = read_json(metadata_path)
        rows.append(build_row(metadata, metadata_path))

    write_csv(rows, output_dir / "summary.csv")
    print(f"[INFO] Wrote {len(rows)} rows to {output_dir / 'summary.csv'}")


if __name__ == "__main__":
    main()