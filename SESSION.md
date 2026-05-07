# SESSION

Running project memory for `fv_runner`.

Update this file at the end of each work session. Put newest entries first so the current state is easy to find.

## Current State

- Date: 2026-05-06
- Project purpose: run and compare OneSpin/QVerify formal verification experiments with orchestrator enabled (`orch`) and disabled (`no_orch`).
- Active benchmark configuration lives in `configs/benchmarks.py`.
- Current active benchmark entries include `mult_256`, `signedDiv_16`, `signedDiv_32`, `sub_256`, and `sub_512`.
- `results/runs.csv` and `results/run_metadata.json` currently exist as empty legacy/result placeholders.
- `results/metadata/` and `results/summary.csv` are produced by the current scripts when experiments and parsing are run.

## Latest Session Notes

### 2026-05-07

Attempted:
- Initialized this folder as a Git repository on branch `main`.
- Connected Git remote `origin` to `git@github.com:malhiaak19/fv_runner.git`.
- Added `.gitignore` rules for generated experiment logs/results and local runtime noise.
- Added push/pull helper scripts:
  - `PushToGitHub.bat`
  - `PullFromGitHub.bat`
  - `scripts/git_push.ps1`
  - `scripts/git_pull.ps1`

Learned:
- Git initially blocked the folder with a dubious ownership warning, so this exact project path was added to Git's global `safe.directory` list.

Next To-Do:
- Use `PushToGitHub.bat` to commit and push local changes with a prompt for the commit message.
- Use `PullFromGitHub.bat` to fetch and rebase from GitHub before continuing work on another machine.

### 2026-05-06

Attempted:
- Commented out non-selected benchmark entries in `configs/benchmarks.py`.
- Kept the selected interesting benchmark set active: `add_256`, `add_512`, `div_16`, `div_32`, `madd_8`, `madd_16`, `madd_32`, `madd_64`, `mod_16`, `mod_32`, `mult_16`, `mult_32`, `mult_64`, `mult_256`, `signedDiv_16`, `signedDiv_32`, `sub_256`, and `sub_512`.

Learned:
- The benchmark config now contains 18 active benchmark entries.

Failed / Blocked:
- Python syntax validation was not run in this Windows shell.

Next To-Do:
- Run `python3 -m py_compile configs/benchmarks.py` or import `configs.benchmarks` on the Linux experiment machine before launching experiments.

### 2026-05-06

Attempted:
- Added `COMMANDS.md` as a copy-paste command cookbook for SSH/SCP transfers, archive extraction, QIP parsing, log parsing, and result zipping.

Learned:
- Frequently used commands span PowerShell on Windows and Bash on the lab Linux machine.

Failed / Blocked:
- No command execution was attempted.

Next To-Do:
- Add future known-good run commands to `COMMANDS.md` after they are used successfully.

### 2026-05-06

Attempted:
- Un-commented all benchmark entries in `configs/benchmarks.py`.

Learned:
- The benchmark config now contains 85 active benchmark entries.
- Section comments such as `#Add`, `#Div`, and `#mult` were left as labels.

Failed / Blocked:
- Python syntax validation could not be run from this Windows shell because `python.exe` and `python3.exe` point to unavailable WindowsApps launchers, and `py` is not installed.

Next To-Do:
- Run `python -m py_compile configs/benchmarks.py` or import `configs.benchmarks` in the Linux experiment environment before launching the full batch.
- Consider whether running all 85 entries at once is intended, since most use both `no_orch` and `orch` modes.

### 2026-05-06

Attempted:
- Created project memory Markdown files: `SESSION.md`, `PLAN.md`, `CONVENTIONS.md`, and `ARCHITECTURE.md`.
- Inspected the existing runner scripts and benchmark config to document the real workflow.

Learned:
- This folder is not currently a git repository.
- The runner expects Linux-style benchmark paths such as `/home/aakasha/arithmeticASICSuite/...`.
- `run_experiments.py` generates patched TCL files beside each source TCL script, not inside this project folder.
- `parse_qip_events.py` currently hardcodes `PROJECT_ROOT = Path("/home/aakasha/fv_runner")`.

Failed / Blocked:
- No experiment execution was attempted in this documentation session.
- No test suite is present in the project.

Next To-Do:
- Decide whether `parse_qip_events.py` should compute `PROJECT_ROOT` dynamically like the other scripts.
- Decide whether generated TCL files should continue to be written beside benchmark TCL files or into a local generated-artifacts folder.
- Add a short README or usage section if this folder will be shared with other users.
- After the next real run, capture run command, benchmark list, status, and notable failures here.

## Session Entry Template

### YYYY-MM-DD

Attempted:
- 

Learned:
- 

Failed / Blocked:
- 

Decisions Made:
- 

Next To-Do:
- 
