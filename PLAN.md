# PLAN

Planning workspace for `fv_runner`.

Use this file before coding or running a major experiment. Keep the active plan near the top, then move completed plans into the history section.

## Active Plan

### 2026-05-06: Project Memory Docs

Goal:
- Add lightweight decision-memory files that help future sessions understand this project quickly.

Steps:
- [x] Inspect project structure.
- [x] Read main scripts and benchmark configuration.
- [x] Create `SESSION.md`, `PLAN.md`, `CONVENTIONS.md`, and `ARCHITECTURE.md`.
- [ ] Review these files after the next experiment and refine terminology.

Validation:
- Confirm files exist at project root.
- Confirm architecture and conventions match the current scripts.

## Backlog

- Make `parse_qip_events.py` use a dynamic project root instead of `/home/aakasha/fv_runner`.
- Add command examples for:
  - running experiments
  - parsing summary CSV
  - parsing QIP event logs
- Add focused parser checks for representative log snippets.
- Decide how to handle empty or missing `results/metadata/`.
- Decide whether `results/runs.csv` and `results/run_metadata.json` are still needed.

## Plan Template

### YYYY-MM-DD: Short Feature / Task Name

Goal:
- 

Context:
- 

Steps:
- [ ] 
- [ ] 
- [ ] 

Risks:
- 

Validation:
- 

Decision Points:
- 

Outcome:
- 

