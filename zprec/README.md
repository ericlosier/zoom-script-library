# Zoom Phone Call Recordings Export Script `(zprec.py)`

This Python script exports **Zoom Phone call recordings** for a specified date range. It uses the **Zoom REST API (v2)** and authenticates via **OAuth account-level credentials**. The script retrieves all call recordings, exports metadata to a CSV file, and downloads the recording files locally.

## 📋 Features

- Authenticates with Zoom using **OAuth (Account Credentials flow)**  
- Prompts for a **start and end date** to define the export range  
- Retrieves all Zoom Phone **call recordings** with automatic pagination  
- Exports recording metadata (caller, callee, direction, duration, etc.) to a **CSV file**  
- Downloads all recording files (`.mp3`) to a local **recordings** folder  

## 🧩 Requirements

- Python 3.7 or higher  
- Zoom account with **Server-to-Server OAuth App** credentials  [(instructions)](https://github.com/ericlosier/zoom-script-library/wiki/Creating-a-Zoom-Server%E2%80%90to%E2%80%90Server-OAuth-App)
- Required Python packages:
  - `requests`
  - `csv` (default)
  - `json` (default)
  - `datetime` (default)
  - `os` (default)

Install dependencies (if not already available):

```bash
pip install requests
```

## ⚙️ Configuration
Before running the script, update the following variables in the file:

```
ZOOM_ACCOUNT_ID = "ACCOUNT_ID"
ZOOM_CLIENT_ID = "CLIENT_ID"
ZOOM_CLIENT_SECRET = "CLIENT_SECRET"
```

These values come from your **Zoom Server-to-Server OAuth App Credentials** [(instructions)](https://github.com/ericlosier/zoom-script-library/wiki/Creating-a-Zoom-Server%E2%80%90to%E2%80%90Server-OAuth-App).

### 🔐 Zoom Server-to-Server OAuth App Scopes
The following granular scopes should be added to the Zoom Server-to-Server OAuth app used by this script:

- phone:read:list_call_logs:admin  
- phone:read:list_recordings:admin  

## 🚀 Usage
Run the script directly from the command line:

```bash
python zprec.py
```

When prompted, enter the desired start and end dates in `YYYY-MM-DD` format.

## 🧠 How It Works
1. **Obtain OAuth Token**

	The script calls the Zoom OAuth token endpoint (`https://zoom.us/oauth/token`) using the **account_credentials** grant type to retrieve an access token.

2. **Prompt for Date Range**

	The user provides a start date and end date. The script validates both are in `YYYY-MM-DD` format before proceeding.

3. **Fetch Call Recordings**

	It calls the `/phone/recordings` endpoint with the specified date range and automatically paginates through all results using `next_page_token`.

4. **Export Metadata to CSV**

	Recording metadata (call ID, caller/callee numbers, direction, start/end time, duration, filename, and download URL) is written to `zoom_phone_recordings.csv`.

5. **Download Recordings**

	Each recording file is downloaded via its `download_url` and saved as an `.mp3` file in a local `recordings/` directory.

## 🧰 Functions Overview
| Function | Description |
|---|---|
| `get_access_token()` | Retrieves a new OAuth access token using account credentials. |
| `fetch_call_recordings(access_token, start_date, end_date)` | Fetches all Zoom Phone call recordings for the given date range with pagination. |
| `export_metadata_to_csv(recordings, csv_filename)` | Writes recording metadata to a CSV file. |
| `download_recordings(recordings, access_token, output_dir)` | Downloads each recording file to a local directory. |

## ⚠️ Error Handling
- If the OAuth token request fails, the script raises an HTTP error and exits.  

- If the date format is invalid, the script prints an error message and exits.  

- If no recordings are found for the given date range, the script notifies the user and exits gracefully.  

- If a recording has no download URL, it is skipped during the download phase.  

- Failed downloads are logged to the console with the corresponding HTTP status code.

## 🧾 Example CSV Output
| call_id | caller_number | callee_number | direction | start_time | end_time | duration | recording_file_name | download_url |
|---|---|---|---|---|---|---|---|---|
| abc123 | +15145551234 | +14165559876 | outbound | 2026-04-05T14:30:00Z | 2026-04-05T14:35:00Z | 300 | abc123.mp3 | https://api.zoom.us/v2/phone/recordings/abc123/download |

## 🧑‍💻 Example Console Output
```
=== Zoom Phone Call Recordings Export ===
Enter start date (YYYY-MM-DD): 2026-04-01
Enter end date (YYYY-MM-DD): 2026-04-30
Authenticating with Zoom API...
Fetching call recordings...
Found 12 recordings.
✅ Metadata exported to zoom_phone_recordings.csv
Downloaded: abc123.mp3
Downloaded: def456.mp3
Downloaded: ghi789.mp3
[...]
✅ Export completed successfully.
```

## 📚 References
- [Creating a Zoom Server‐to‐Server OAuth App](https://github.com/ericlosier/zoom-script-library/wiki/Creating-a-Zoom-Server%E2%80%90to%E2%80%90Server-OAuth-App)
- Zoom API Documentation:
  - [GET /phone/recordings](https://developers.zoom.us/docs/api/phone/#tag/recordings/get/phone/recordings)
