# Zoom Phone Charges Export Script `(zp_charges.py)`

This Python script generates a combined **Zoom Phone charges log** covering **call**, **fax** and **SMS/MMS** charges for a date/time range. It uses the **Zoom REST API (v2)** and authenticates via **OAuth account-level credentials**. The output is **four CSV files**: one per report plus one combined file with a `charge_type` column (`call`, `fax` or `sms`) as its first column.

## 📋 Features

- Authenticates with Zoom using **OAuth (Account Credentials flow)**
- Retrieves the three Zoom Phone charge reports with automatic pagination
- Accepts the start/end date and time (**UTC**) as command-line arguments, or prompts for them
- Automatically splits ranges longer than 30 days into multiple requests and removes duplicates
- Writes one **CSV per report** (call, fax, SMS/MMS) plus one **combined CSV** with `charge_type` as the first column
- If one report fails (e.g. a missing scope), the other reports are still exported and the failure is reported

## 🧩 Requirements

- Python 3.7 or higher
- Zoom account with **Server-to-Server OAuth App** credentials [(instructions)](https://github.com/ericlosier/zoom-script-library/wiki/Creating-a-Zoom-Server%E2%80%90to%E2%80%90Server-OAuth-App)
- Required Python packages:
  - `requests`
  - `argparse`, `csv`, `datetime`, `os`, `time` (default)

Install dependencies (if not already available):

```bash
pip install requests
```

## ⚙️ Configuration
Before running the script, update the following variables in the file:

```
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
ACCOUNT_ID = "YOUR_ACCOUNT_ID"
```

Alternatively, set the `ZOOM_CLIENT_ID`, `ZOOM_CLIENT_SECRET` and `ZOOM_ACCOUNT_ID` environment variables, which take precedence over the values in the file.

These values come from your **Zoom Server-to-Server OAuth App Credentials** [(instructions)](https://github.com/ericlosier/zoom-script-library/wiki/Creating-a-Zoom-Server%E2%80%90to%E2%80%90Server-OAuth-App).

### 🔐 Zoom Server-to-Server OAuth App Scopes
The following granular scopes should be added to the Zoom Server-to-Server OAuth app used by this script:

- phone:read:call_charges:admin
- phone:read:fax_charges:admin
- phone:read:sms_charges:admin

## 🚀 Usage
Run the script with no arguments to be prompted for the start and end date/time:

```bash
python zp_charges.py
```

Or supply them on the command line (you will be asked to confirm the range before anything is retrieved):

```bash
python zp_charges.py --start "2026-09-01 00:00:00" --end "2026-09-30 23:59:59"
```

| Argument | Description |
|---|---|
| `--start` | Start date/time in UTC: `YYYY-MM-DD` or `YYYY-MM-DD HH:MM:SS` |
| `--end` | End date/time in UTC, same format |
| `--yes` | Skip the confirmation prompt (for unattended runs) |

A date without a time means `00:00:00`. If only one of `--start`/`--end` is given, the script prompts for the other.

## 🕒 Time Zone and Range Limits
- All date/times are **UTC**. Zoom documents the timestamps in all three reports (`start_time`/`answer_time`/`end_time` for calls, `end_time` for faxes, `sent_time` for SMS/MMS) as GMT/UTC, and the `from`/`to` parameters are sent as UTC (`yyyy-MM-ddTHH:mm:ssZ`).
- Zoom returns at most about one month of data per request, so longer ranges are split into windows of up to 30 days.
- The start of the range cannot be more than **13 months** ago.
- Some report endpoints reject exact date/times with an HTTP 400 (observed with the fax report). In that case the script automatically retries with whole UTC days and trims the records to your exact start/end on the client side, using each record's own timestamp.

## 🧠 How It Works
1. **Obtain OAuth Token**

   The script calls the Zoom OAuth token endpoint (`https://zoom.us/oauth/token`) using the **account_credentials** grant type to retrieve an access token.

2. **Determine the Date Range**

   The range comes from `--start`/`--end` or the prompts, and is validated.

3. **Retrieve the Reports**

   For each window, it pages through `/phone/reports/call_charges`, `/phone/reports/fax_charges` and `/phone/reports/sms_charges` (300 records per page) and de-duplicates records on their unique IDs.

4. **Write the Combined CSV**

   Each report that returned records is written to its own file, with only that report's fields: `zoom_phone_call_charges_<timestamp>.csv`, `zoom_phone_fax_charges_<timestamp>.csv` and `zoom_phone_sms_charges_<timestamp>.csv`. All records are also written to the combined `zoom_phone_charges_<timestamp>.csv`. The combined file's columns are `charge_type` followed by the combined set of fields from the three reports. Fields shared between reports (e.g. `billing_number`, `rate`, `currency`, `total_charge`, `end_time`) share a column; fields that do not apply to a charge type are left blank.

## 🧑‍💻 Example Console Output
```
Zoom Phone Charges Export

Date range (UTC): 2026-09-01T00:00:00Z to 2026-09-30T23:59:59Z (1 request window per report)
Proceed? [y/N]: y
OAuth token refreshed successfully!

Retrieving call charges...
  1250 call charge records.
Retrieving fax charges...
  12 fax charge records.
Retrieving sms charges...
  348 sms charge records.

1250 records written to 'zoom_phone_call_charges_20261007_164716.csv'.
12 records written to 'zoom_phone_fax_charges_20261007_164716.csv'.
348 records written to 'zoom_phone_sms_charges_20261007_164716.csv'.
1610 records written to 'zoom_phone_charges_20261007_164716.csv'.
```

## 📚 References
- [Creating a Zoom Server‐to‐Server OAuth App](https://github.com/ericlosier/zoom-script-library/wiki/Creating-a-Zoom-Server%E2%80%90to%E2%80%90Server-OAuth-App)
- Zoom API Documentation:
  - [Get call charges usage report](https://developers.zoom.us/docs/api/phone/#tag/reports/GET/phone/reports/call_charges)
  - [Get fax charges usage report](https://developers.zoom.us/docs/api/phone/#tag/reports/GET/phone/reports/fax_charges)
  - [Get SMS/MMS charges usage report](https://developers.zoom.us/docs/api/phone/#tag/reports/GET/phone/reports/sms_charges)
