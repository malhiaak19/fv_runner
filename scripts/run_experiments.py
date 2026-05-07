from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from configs.benchmarks import BENCHMARKS


ONESPIN_SETUP_DIR = Path("/usr/local/misc/qed_qos")
ONESPIN_SETUP_SCRIPT = ONESPIN_SETUP_DIR / "SETUP_ONESPIN.bash"
ONESPIN_GUI_MODE = "shell"


MODE_MAP = {
    "orch": False,
    "no_orch": True,
}


@dataclass
class RunSpec:
    design_name: str
    script_path: Path
    qea_dir: Path
    variant_name: str
    dont_use_orchestrator: bool
    engines_comb: list[int] | None
    run_id: str
    generated_tcl_path: Path
    log_path: Path
    stdout_path: Path
    stderr_path: Path
    metadata_path: Path
    qip_protocol_dir: None


def now_str() -> str:
    return datetime.now().isoformat(timespec="seconds")


def mkdir_p(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_benchmarks() -> List[Dict[str, str]]:
    if not BENCHMARKS:
        raise ValueError("BENCHMARKS is empty.")

    for bench in BENCHMARKS:
        if "name" not in bench or "script_path" not in bench:
            raise ValueError(f"Invalid benchmark entry: {bench}")

    return BENCHMARKS


def build_run_specs(project_root: Path) -> List[RunSpec]:
    specs: List[RunSpec] = []

    logs_root = project_root / "logs"
    metadata_root = project_root / "results" / "metadata"

    mkdir_p(logs_root)
    mkdir_p(metadata_root)

    for bench in load_benchmarks():
        design_name = bench["name"]
        script_path = Path(bench["script_path"]).resolve()
        engines_comb = bench.get("engines_comb")
        modes = bench.get("modes", ["orch", "no_orch"])

        if not script_path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")

        for mode in modes:
            if mode not in MODE_MAP:
                raise ValueError(f"Unsupported mode '{mode}' in benchmark '{design_name}'")

        qea_dir = script_path.parent

        for mode in modes:
            dont_use_orchestrator = MODE_MAP[mode]
            run_id = f"{design_name}__{mode}"

            log_dir = logs_root / design_name / mode
            mkdir_p(log_dir)

            # Only orchestration runs need preserved QIP protocol directories.
            qip_protocol_dir = None
            if mode == "orch":
                qip_protocol_dir = log_dir / "qip_protocols"
                mkdir_p(qip_protocol_dir)

            generated_tcl_name = f"{script_path.stem}__{mode}__generated.tcl"
            generated_tcl_path = qea_dir / generated_tcl_name

            log_path = log_dir / f"{run_id}.log"
            stdout_path = log_dir / f"{run_id}.stdout.txt"
            stderr_path = log_dir / f"{run_id}.stderr.txt"
            metadata_path = metadata_root / f"{run_id}.json"

            specs.append(
                RunSpec(
                    design_name=design_name,
                    script_path=script_path,
                    qea_dir=qea_dir,
                    variant_name=mode,
                    dont_use_orchestrator=dont_use_orchestrator,
                    engines_comb=engines_comb,
                    run_id=run_id,
                    generated_tcl_path=generated_tcl_path,
                    log_path=log_path,
                    stdout_path=stdout_path,
                    stderr_path=stderr_path,
                    metadata_path=metadata_path,
                    qip_protocol_dir=qip_protocol_dir,
                )
            )

    return specs

def make_engine_injection(engines_comb: list[int] | None) -> str:
    lines = []
    lines.append('puts "-I- EXPERIMENT_ENGINES_COMB_BEFORE=[get_compare_option -engines_comb]"')

    if engines_comb:
        engine_str = " ".join(str(e) for e in engines_comb)
        lines.append(f"set_compare_option -engines_comb {{{engine_str}}}")

    lines.append('puts "-I- EXPERIMENT_ENGINES_COMB_AFTER=[get_compare_option -engines_comb]"')
    return "\n".join(lines) + "\n"

def inject_after_ec_mode_setup(
    tcl_text: str,
    engine_injection: str,
    qip_protocol_injection: str = "",
) -> str:
    pattern = re.compile(
        r'(set_mode\s+ec\s*\nputs\s+"resource_usage_after_ec_mode_setup"\s*\nreport_resource_usage\s*\n)',
        re.MULTILINE,
    )

    match = pattern.search(tcl_text)
    if not match:
        raise ValueError("Could not find ec mode setup anchor in TCL script.")

    combined_injection = engine_injection + "\n" + qip_protocol_injection

    return tcl_text[:match.end()] + combined_injection + tcl_text[match.end():]

def patch_start_message_log(tcl_text: str, new_log_path: Path) -> str:
    pattern = re.compile(r"^\s*start_message_log\s+-force\s+.*$", re.MULTILINE)
    replacement = f"start_message_log -force {new_log_path}"

    if not pattern.search(tcl_text):
        raise ValueError("Could not find 'start_message_log -force ...' in TCL script.")

    return pattern.sub(replacement, tcl_text, count=1)

def make_qip_protocol_injection(spec: RunSpec) -> str:
    if spec.variant_name != "orch" or spec.qip_protocol_dir is None:
        return ""

    lines = []
    lines.append('puts "-I- EXPERIMENT_QIP_PROTOCOL_PRESERVE=true"')
    lines.append("onespin::set_parameter ec_preserve_qverify_dir true")
    lines.append(f'onespin::set_parameter ec_qverify_dir "{spec.qip_protocol_dir}"')
    lines.append(f'puts "-I- EXPERIMENT_QIP_PROTOCOL_DIR={spec.qip_protocol_dir}"')

    return "\n".join(lines) + "\n"



def generate_run_tcl(spec: RunSpec) -> None:
    original_text = spec.script_path.read_text(encoding="utf-8")
    patched_text = patch_start_message_log(original_text, spec.log_path)

    engine_injection = make_engine_injection(spec.engines_comb)
    qip_protocol_injection = make_qip_protocol_injection(spec)

    patched_text = inject_after_ec_mode_setup(
        patched_text,
        engine_injection,
        qip_protocol_injection,
    )
    

    header = (
        "# Auto-generated by run_experiments.py\n"
        f"# Original script: {spec.script_path}\n"
        f"# Run ID: {spec.run_id}\n"
        f"# Generated at: {now_str()}\n\n"
    )

    spec.generated_tcl_path.write_text(header + patched_text, encoding="utf-8")


def write_metadata(spec: RunSpec, extra: Dict[str, object]) -> None:
    payload = {
        "run_id": spec.run_id,
        "design_name": spec.design_name,
        "variant_name": spec.variant_name,
        "dont_use_orchestrator": spec.dont_use_orchestrator,
        "engines_comb": spec.engines_comb,
        "script_path": str(spec.script_path),
        "qea_dir": str(spec.qea_dir),
        "generated_tcl_path": str(spec.generated_tcl_path),
        "log_path": str(spec.log_path),
        "stdout_path": str(spec.stdout_path),
        "stderr_path": str(spec.stderr_path),
    }
    payload.update(extra)
    spec.metadata_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def build_shell_command(spec: RunSpec) -> str:
    env_prefix = "DONT_USE_ORCHESTRATOR_FLOW=1 " if spec.dont_use_orchestrator else ""
    return (
        f"cd {ONESPIN_SETUP_DIR} && "
        f"source {ONESPIN_SETUP_SCRIPT} && "
        f"{env_prefix}onespin --gui={ONESPIN_GUI_MODE} {spec.generated_tcl_path}"
    )


def run_single_experiment(spec: RunSpec) -> int:
    generate_run_tcl(spec)

    write_metadata(
        spec,
        {
            "status": "running",
            "start_time": now_str(),
        },
    )

    shell_cmd = build_shell_command(spec)
    start_wall = time.time()

    with spec.stdout_path.open("w", encoding="utf-8") as stdout_f, \
         spec.stderr_path.open("w", encoding="utf-8") as stderr_f:
        try:
            process = subprocess.run(
                ["bash", "-lc", shell_cmd],
                cwd=spec.qea_dir,
                env=os.environ.copy(),
                stdout=stdout_f,
                stderr=stderr_f,
                text=True,
                check=False,
            )

            end_wall = time.time()

            write_metadata(
                spec,
                {
                    "status": "completed" if process.returncode == 0 else "failed",
                    "start_time": datetime.fromtimestamp(start_wall).isoformat(),
                    "end_time": datetime.fromtimestamp(end_wall).isoformat(),
                    "wall_time_sec": round(end_wall - start_wall, 3),
                    "return_code": process.returncode,
                    "shell_command": shell_cmd,
                },
            )

            return process.returncode

        except Exception as exc:
            end_wall = time.time()
            write_metadata(
                spec,
                {
                    "status": "error",
                    "start_time": datetime.fromtimestamp(start_wall).isoformat(),
                    "end_time": datetime.fromtimestamp(end_wall).isoformat(),
                    "wall_time_sec": round(end_wall - start_wall, 3),
                    "shell_command": shell_cmd,
                    "error": repr(exc),
                },
            )
            raise


def main() -> int:
    project_root = Path(__file__).resolve().parent.parent
    specs = build_run_specs(project_root)

    print(f"[INFO] Planned runs: {len(specs)}")

    overall_rc = 0

    for idx, spec in enumerate(specs, start=1):
        print(f"\n[INFO] ({idx}/{len(specs)}) Starting {spec.run_id}")
        print(f"[INFO] Original TCL : {spec.script_path}")
        print(f"[INFO] Generated TCL: {spec.generated_tcl_path}")
        print(f"[INFO] Log path     : {spec.log_path}")
        print(f"[INFO] Mode         : {spec.variant_name}")

        rc = run_single_experiment(spec)

        if rc != 0:
            print(f"[WARN] {spec.run_id} returned code {rc}")
            overall_rc = rc
        else:
            print(f"[INFO] {spec.run_id} completed")

    print("\n[INFO] All runs finished.")
    return overall_rc


if __name__ == "__main__":
    sys.exit(main())