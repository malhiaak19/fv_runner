# ARCHITECTURE

High-level map of `fv_runner`.

This project is a small experiment runner for formal verification comparisons. Its main job is to run the same benchmark TCL flow in two modes, collect logs and metadata, and parse those artifacts into CSV summaries.

## Data Flow

1. Benchmark selection
   - Source: `configs/benchmarks.py`
   - Data: list of benchmark dictionaries with `name`, `script_path`, optional `engines_comb`, and `modes`.

2. Run planning
   - Script: `scripts/run_experiments.py`
   - Function: `build_run_specs`
   - Output: one `RunSpec` per benchmark mode.
   - Modes:
     - `orch`: normal orchestrator flow.
     - `no_orch`: runs with `DONT_USE_ORCHESTRATOR_FLOW=1`.

3. TCL generation
   - Script: `scripts/run_experiments.py`
   - The original benchmark TCL is read from the external `script_path`.
   - `start_message_log -force ...` is patched to write into this project under `logs/<design>/<mode>/`.
   - Engine reporting/injection is inserted after the `set_mode ec` setup anchor.
   - For `orch`, QIP protocol preservation is enabled and pointed at `logs/<design>/orch/qip_protocols/`.
   - Generated TCL is written beside the original benchmark TCL as `<original_stem>__<mode>__generated.tcl`.

4. Experiment execution
   - Script: `scripts/run_experiments.py`
   - External setup:
     - setup directory: `/usr/local/misc/qed_qos`
     - setup script: `/usr/local/misc/qed_qos/SETUP_ONESPIN.bash`
     - command: `onespin --gui=shell <generated_tcl_path>`
   - Outputs per run:
     - main tool log: `logs/<design>/<mode>/<run_id>.log`
     - stdout: `logs/<design>/<mode>/<run_id>.stdout.txt`
     - stderr: `logs/<design>/<mode>/<run_id>.stderr.txt`
     - metadata: `results/metadata/<run_id>.json`

5. Summary parsing
   - Script: `scripts/parse_logs.py`
   - Reads JSON metadata from `results/metadata/`.
   - Opens each `log_path`.
   - Extracts result, HOLD/FAIL/OPEN counts, timeout status, runtime text, design sizes, mapped targets, compare setup, complexity, and engine settings.
   - Writes `results/summary.csv`.

6. QIP event formatting
   - Script: `scripts/parse_qip_events.py`
   - Finds preserved QIP event logs under `logs/<design>/orch/qip_protocols/qip_protocols-*/.qverify/PROC/EVENT/`.
   - Runs external `qverify_event`.
   - Writes readable event logs under `results/qip_event_logs/<design>/orch/<protocol_dir>/`.

## Main Modules

- `configs/benchmarks.py`
  - Manual benchmark registry.
  - Most entries are commented out; uncomment entries to activate them.

- `scripts/run_experiments.py`
  - Builds run specs.
  - Patches/generates TCL.
  - Runs OneSpin.
  - Writes per-run metadata.

- `scripts/parse_logs.py`
  - Converts run metadata plus logs into `results/summary.csv`.

- `scripts/parse_qip_events.py`
  - Converts preserved QIP event logs into readable text via `qverify_event`.

## Important Assumptions

- The experiment environment is Linux-like and has access to `/usr/local/misc/qed_qos`.
- Benchmark TCL scripts exist outside this repo under `/home/aakasha/arithmeticASICSuite/...`.
- Original TCL scripts contain:
  - a `start_message_log -force ...` line
  - the expected `set_mode ec` / `resource_usage_after_ec_mode_setup` anchor
- Log parsing depends on known OneSpin/QVerify message text.

## Decision Log

### 2026-05-06: Keep Memory Docs at Project Root

Decision:
- Store `SESSION.md`, `PLAN.md`, `CONVENTIONS.md`, and `ARCHITECTURE.md` at the root of `fv_runner`.

Reason:
- These files are easy for humans and AI sessions to discover before editing or running experiments.

Consequences:
- Future sessions should read these files first.
- These files should be kept short and updated as decisions change.

### 2026-05-06: Document Current Generated TCL Behavior

Decision:
- Document that generated TCL files are currently written beside the original external benchmark TCL files.

Reason:
- This is the behavior in `scripts/run_experiments.py` today.

Open Question:
- Decide later whether generated TCL should move into this project folder for easier cleanup and reproducibility.

## Open Architecture Questions

- Should `parse_qip_events.py` compute `PROJECT_ROOT` dynamically?
- Should the project have a single command entry point for run, parse logs, and parse QIP events?
- Should generated TCL files be stored inside `fv_runner` instead of external benchmark directories?
- Should `results/runs.csv` and `results/run_metadata.json` be removed, regenerated, or documented as legacy placeholders?

