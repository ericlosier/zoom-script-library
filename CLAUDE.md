# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A collection of independent, standalone Python scripts that extend Zoom's admin portal via the Zoom REST API v2. It is a personal open-source project, not an official Zoom sample. There is no build system, test suite, or linter. The only dependency is `requests` (see `requirements.txt`). `myenv/` is a gitignored local virtualenv.

## Running scripts

```bash
pip install -r requirements.txt
python <script>/<script>.py              # no args: list_users, zoom_user_export, zprec, download_transcripts
python zp_charges/zp_charges.py [--start ... --end ... [--yes]]   # UTC range; prompts if omitted
python <script>/<script>.py users.csv    # CSV-driven: add_sso, add_user_to_group, update_zoom_timezone
```

- `zprec` prompts interactively for start/end dates (`YYYY-MM-DD`).
- `download_transcripts` reads `meeting_ids.txt` from the current working directory.
- The CSV-driven scripts require exactly one CSV argument. Sample inputs are in each script's `examples/` folder.
- Credentials are hardcoded placeholders (the exception is `zp_charges`, which also honors `ZOOM_CLIENT_ID`/`ZOOM_CLIENT_SECRET`/`ZOOM_ACCOUNT_ID` env vars). Edit the hardcoded placeholders at the top of each script (`CLIENT_ID`, `CLIENT_SECRET`, `ACCOUNT_ID`; `zprec` uses `ZOOM_*` names). Never commit real values.
- `.vscode/launch.json` runs the current file with a prompt for arguments.

## Architecture

- One folder per script: `<name>/<name>.py`, `<name>/README.md`, and an optional `examples/` folder. Scripts share no code and do not import each other.
- Every script duplicates (copy-pasted, not shared) the same pattern: Server-to-Server OAuth `account_credentials` grant against `https://zoom.us/oauth/token`, then bearer-token calls to `https://api.zoom.us/v2`. A fix to token handling, pagination (`next_page_token` / `page_size`), or CSV output has to be applied in each script separately.
- Output CSVs are timestamped, e.g. `zoom_active_users_YYYYMMDD_HHMMSS.csv`.
- Each script's README lists the granular OAuth scopes the Zoom app needs (e.g. `user:read:user:admin`). Update it when a script gains new API calls.
- `add_sso` quirk: login method `101` is SSO. Creating it overwrites the user's department, so the script restores the department afterward.

## Adding a script

Create a new folder following the layout above (script, README with scopes/usage, optional `examples/`), and add it to the numbered list in the root `README.md`.
