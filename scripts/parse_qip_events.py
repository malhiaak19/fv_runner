from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path("/home/aakasha/fv_runner")
LOGS_ROOT = PROJECT_ROOT / "logs"

QIP_EVENT_FILENAMES = [
    "events_qip_orc.log",
    "events_pm_mgr.log",
    "events_qip_engine_1.log",
    "events_qip_engine_2.log",
    "events_qip_engine_3.log",
    "events_qip_engine_4.log",
    "events_qip_engine_5.log",
    "events_qip_engine_6.log",
    "events_qip_engine_7.log",
    "events_qip_engine_8.log",
    "events_pm_eng_mon_1.log",
    "events_pm_eng_mon_2.log",
    "events_pm_eng_mon_3.log",
    "events_pm_eng_mon_4.log",
    "events_pm_eng_mon_5.log",
    "events_pm_eng_mon_6.log",
    "events_pm_eng_mon_7.log",
    "events_pm_eng_mon_8.log",
    "events_pm_orc_mon.log",
]

# Keep qverify_event default terminal-style formatting.
QVERIFY_EVENT_OPTIONS = []

QVERIFY_EVENT = Path(
    "/usr/local/misc/qed_qos/questa_static_formal/linux_x86_64/bin/qverify_event"
)

OUTPUT_ROOT = PROJECT_ROOT / "results" / "qip_event_logs"

# Useful default formatting options.
QVERIFY_EVENT_OPTIONS = []


def mkdir_p(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def find_qip_event_logs(design_name: str) -> list[Path]:
    """
    Finds all expected QIP event logs for one design.

    Expected structure:
    logs/<design>/orch/qip_protocols/qip_protocols-*/.qverify/PROC/EVENT/<event_file>.log
    """

    qip_root = LOGS_ROOT / design_name / "orch" / "qip_protocols"

    if not qip_root.exists():
        print(f"[WARN] No qip_protocols directory found for {design_name}: {qip_root}")
        return []

    protocol_dirs = sorted(qip_root.glob("qip_protocols-*"))

    if not protocol_dirs:
        print(f"[WARN] No qip_protocols-* directories found for {design_name}: {qip_root}")
        return []

    event_logs: list[Path] = []

    for protocol_dir in protocol_dirs:
        event_dir = protocol_dir / ".qverify" / "PROC" / "EVENT"

        if not event_dir.exists():
            print(f"[WARN] EVENT directory not found: {event_dir}")
            continue

        for filename in QIP_EVENT_FILENAMES:
            event_log = event_dir / filename

            if event_log.exists():
                event_logs.append(event_log)
            else:
                print(f"[WARN] Missing event log: {event_log}")

    return event_logs


def run_qverify_event(event_log: Path, output_path: Path) -> bool:
    mkdir_p(output_path.parent)

    cmd = [
        str(QVERIFY_EVENT),
        *QVERIFY_EVENT_OPTIONS,
        str(event_log),
    ]

    print(f"[INFO] Processing:")
    print(f"       input : {event_log}")
    print(f"       output: {output_path}")

    with output_path.open("w", encoding="utf-8") as out:
        result = subprocess.run(
            cmd,
            stdout=out,
            stderr=subprocess.PIPE,
            text=True,
        )

    if result.returncode != 0:
        print(f"[ERROR] qverify_event failed for {event_log}")
        print(result.stderr.strip())
        return False

    return True


def process_design(design_name: str) -> None:
    event_logs = find_qip_event_logs(design_name)

    if not event_logs:
        print(f"[WARN] No QIP event logs found for {design_name}")
        return

    print(f"[INFO] Found {len(event_logs)} QIP event log(s) for {design_name}")

    for event_log in event_logs:
        protocol_dir_name = event_log.parents[4].name
        event_log_stem = event_log.stem

        output_path = (
            OUTPUT_ROOT
            / design_name
            / "orch"
            / protocol_dir_name
            / f"{event_log_stem}__pretty.txt"
        )

        ok = run_qverify_event(event_log, output_path)

        if ok:
            print(f"[OK] Saved readable QIP events: {output_path}")


def discover_designs() -> list[str]:
    """
    Auto-discovers designs that have logs/<design>/orch/qip_protocols.
    """
    if not LOGS_ROOT.exists():
        return []

    designs = []

    for design_dir in sorted(LOGS_ROOT.iterdir()):
        if not design_dir.is_dir():
            continue

        qip_dir = design_dir / "orch" / "qip_protocols"
        if qip_dir.exists():
            designs.append(design_dir.name)

    return designs


def main() -> int:
    if not QVERIFY_EVENT.exists():
        print(f"[ERROR] qverify_event binary not found: {QVERIFY_EVENT}")
        return 1

    mkdir_p(OUTPUT_ROOT)

    if len(sys.argv) > 1:
        designs = sys.argv[1:]
    else:
        designs = discover_designs()

    if not designs:
        print("[WARN] No designs provided or discovered.")
        print("Usage:")
        print("  python3 -m scripts.parse_qip_events add_256 mod_32")
        print("or run without arguments to auto-discover designs.")
        return 0

    print(f"[INFO] Designs to process: {len(designs)}")

    for design_name in designs:
        process_design(design_name)

    print("[INFO] Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())