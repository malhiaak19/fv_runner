# COMMANDS

Copy-paste command memory for `fv_runner`.

Use this file for commands that are easy to forget, especially SSH/SCP transfers, WSL/Linux setup, experiment parsing, and result packaging.

## Hosts And Paths

Windows project/results paths:

```powershell
E:\_Germany\_University_of_Freiburg\Internship\_Sven\fv_runner
E:\_Germany\_University_of_Freiburg\Internship\_Sven\Results\
```

Linux project path:

```bash
~/fv_runner
/home/aakasha/fv_runner
```

Remote host via jump server:

```bash
aakasha@login.informatik.uni-freiburg.de
aakasha@vdclab03.informatik.intra.uni-freiburg.de
```

## SSH Login

Connect to the lab machine through the jump server:

```bash
ssh -J aakasha@login.informatik.uni-freiburg.de aakasha@vdclab03.informatik.intra.uni-freiburg.de
```

Connect with X forwarding:

```bash
ssh -X -J aakasha@login.informatik.uni-freiburg.de aakasha@vdclab03.informatik.intra.uni-freiburg.de
```

## Copy Files From Windows To Lab Machine

Copy `open_designs.tgz` to the lab home directory:

```powershell
scp -J aakasha@login.informatik.uni-freiburg.de "E:\_Germany\_University_of_Freiburg\Internship\Sven\Received\open_designs.tgz" aakasha@vdclab03.informatik.intra.uni-freiburg.de:~/
```

Copy `arithmeticASICSuite.tgz` to the lab home directory:

```powershell
scp -J aakasha@login.informatik.uni-freiburg.de "E:\_Germany\_University_of_Freiburg\Internship\Sven\Received\arithmeticASICSuite.tgz" aakasha@vdclab03.informatik.intra.uni-freiburg.de:~/
```

## Copy Files From Lab Machine To Windows

Copy zipped QIP event logs back to Windows:

```powershell
scp -J aakasha@login.informatik.uni-freiburg.de aakasha@vdclab03.informatik.intra.uni-freiburg.de:~/fv_runner/results/qip_event_logs.zip "E:\_Germany\_University_of_Freiburg\Internship\_Sven\Results\"
```

## Extract Archives On Lab Machine

Extract open designs:

```bash
tar -xzvf open_designs.tar.gz
```

Extract arithmetic ASIC suite:

```bash
tar -xzvf arithmeticASICSuite.tar.gz
```

If the files are named `.tgz`, use the same command style:

```bash
tar -xzvf open_designs.tgz
tar -xzvf arithmeticASICSuite.tgz
```

## fv_runner Workflow

Go to the project:

```bash
cd ~/fv_runner
```

Parse QIP event logs for one design:

```bash
python3 -m scripts.parse_qip_events add_256
```

Parse QIP event logs for multiple designs:

```bash
python3 -m scripts.parse_qip_events add_256 add_512 div_16 div_32 madd_16 madd_32 madd_64 madd_8 mod_16 mod_32 mult_16 mult_32 mult_64 mult_256 signedDiv_16 signedDiv_32 sub_256 sub_512
```

Parse experiment logs into summary CSV:

```bash
python3 -m scripts.parse_logs
```

## QIP Event Tool

Run `qverify_event` manually on one event log:

```bash
./qverify_event /home/aakasha/fv_runner/logs/add_512/orch/qip_protocols/qip_protocols-1777538346985492566/.qverify/PROC/EVENT/events_qip_orc.log
```

## Package Results

Zip readable QIP event logs:

```bash
cd ~/fv_runner/results
zip -r qip_event_logs.zip qip_event_logs
```

## Edit Files On Lab Machine

Open `parse_qip_events.py` in nano:

```bash
nano ~/fv_runner/scripts/parse_qip_events.py
```

## Active Design List

Useful list from previous QIP event parsing:

```text
add_256 add_512 div_16 div_32 madd_16 madd_32 madd_64 madd_8 mod_16 mod_32 mult_16 mult_32 mult_64 mult_256 signedDiv_16 signedDiv_32 sub_256 sub_512
```

## Prompt To Ask Codex For Commands

Use this when you want a ready-to-copy command:

```text
Read COMMANDS.md first. I want to <task>. Give me the exact command to copy-paste, and mention whether it should be run in PowerShell, WSL, or the lab Linux shell.
```

## Command Entry Template

### Task Name

Run in: PowerShell / WSL / lab Linux shell

Purpose:
- 

Command:

```bash

```

Notes:
- 

