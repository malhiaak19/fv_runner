# CONVENTIONS

Rules and preferences for working in `fv_runner`.

Future AI sessions should read this before changing code.

## Python Style

- Use Python 3 with `from __future__ import annotations` in new or heavily edited scripts, matching `scripts/run_experiments.py` and `scripts/parse_logs.py`.
- Prefer `pathlib.Path` for filesystem paths.
- Keep functions small and named around one action, for example `build_run_specs`, `generate_run_tcl`, `parse_runtime`.
- Use type hints for function inputs and outputs.
- Use UTF-8 when reading or writing text files.
- Keep log parsing tolerant: return `None`, `"unknown"`, or a clear fallback instead of crashing when optional patterns are absent.
- Use structured data (`dict`, dataclass, JSON, CSV) for run metadata and summaries.

## Project Paths

- Treat the project root as the parent of `scripts/` when possible:
  - `Path(__file__).resolve().parent.parent`
- Avoid new hardcoded project-root paths. Existing exception: `scripts/parse_qip_events.py` currently uses `/home/aakasha/fv_runner`.
- Benchmark `script_path` values may remain absolute because they point to external arithmetic benchmark directories.
- Generated run artifacts currently go to:
  - logs: `logs/<design>/<mode>/`
  - metadata: `results/metadata/<run_id>.json`
  - summary CSV: `results/summary.csv`
  - QIP readable logs: `results/qip_event_logs/`

## Experiment Naming

- Use `orch` for orchestrator-enabled runs.
- Use `no_orch` for runs with `DONT_USE_ORCHESTRATOR_FLOW=1`.
- Run IDs should stay stable as `<design_name>__<mode>`.
- Preserve the benchmark names from `configs/benchmarks.py` so logs, metadata, and summaries line up.

## Editing Rules

- Do not overwrite original TCL benchmark scripts directly.
- Generated TCL scripts must include enough header metadata to trace them back to the original script and run ID.
- Keep parser column names stable unless there is a deliberate migration plan.
- If adding a new result field, add it to metadata or summary output in a predictable place and document it in `ARCHITECTURE.md`.
- Do not delete logs/results unless explicitly requested.

## Documentation Rules

- Update `SESSION.md` after experiment runs, failed attempts, or meaningful decisions.
- Draft non-trivial code changes in `PLAN.md` before implementation.
- Add durable design choices to the decision log in `ARCHITECTURE.md`.
- Add recurring coding preferences to this file instead of burying them in chat.

