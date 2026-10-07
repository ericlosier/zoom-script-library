import argparse
import csv
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import requests

# Zoom API base URL
BASE_URL = "https://api.zoom.us/v2"

# Zoom OAuth endpoint
TOKEN_URL = "https://zoom.us/oauth/token"

# Your Zoom API credentials (can also be supplied via the ZOOM_CLIENT_ID,
# ZOOM_CLIENT_SECRET and ZOOM_ACCOUNT_ID environment variables)
CLIENT_ID = os.environ.get("ZOOM_CLIENT_ID", "YOUR_CLIENT_ID")
CLIENT_SECRET = os.environ.get("ZOOM_CLIENT_SECRET", "YOUR_CLIENT_SECRET")
ACCOUNT_ID = os.environ.get("ZOOM_ACCOUNT_ID", "YOUR_ACCOUNT_ID")

# The three Zoom Phone charge reports:
# label -> (endpoint, response array key, unique ID fields, record time field)
REPORTS = {
    "call": ("/phone/reports/call_charges", "call_charges", ("charge_id", "call_id"), "start_time"),
    "fax": ("/phone/reports/fax_charges", "fax_charges", ("fax_id",), "end_time"),
    "sms": ("/phone/reports/sms_charges", "sms_charges", ("message_id",), "sent_time"),
}

# API limits: one month of data per request, no further back than 13 months
WINDOW = timedelta(days=30)
MAX_MONTHS_BACK = 13
PAGE_SIZE = 300

API_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
API_DATE_FORMAT = "%Y-%m-%d"
INPUT_FORMATS = (
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d",
)


class ReportError(Exception):
    """Raised when a charge report cannot be retrieved."""


# Get OAuth access token
def refresh_oauth_token():
    try:
        auth_response = requests.post(
            TOKEN_URL,
            auth=(CLIENT_ID, CLIENT_SECRET),
            data={
                'grant_type': 'account_credentials',
                'account_id': ACCOUNT_ID
            }
        )
        auth_response.raise_for_status()
        access_token = auth_response.json()['access_token']

        print("OAuth token refreshed successfully!")

        return access_token

    except requests.exceptions.RequestException as e:
        print(f"Error refreshing OAuth token: {e}")
        return None


# Parse a UTC date/time string such as "2026-09-01" or "2026-09-01 13:30:00"
def parse_utc(value):
    value = value.strip().rstrip("Zz")
    for fmt in INPUT_FORMATS:
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    raise ValueError(f"'{value}' is not a valid date/time. Use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS (UTC).")


# Earliest start the reports accept (13 months back)
def earliest_allowed_start():
    now = datetime.now(timezone.utc)
    month_index = now.year * 12 + (now.month - 1) - MAX_MONTHS_BACK
    year, month = divmod(month_index, 12)
    day = min(now.day, 28)
    return now.replace(year=year, month=month + 1, day=day)


# Ask for a date/time until a valid one is entered
def prompt_utc_datetime(label):
    while True:
        value = input(f"Enter {label} date/time in UTC (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS): ")
        try:
            return parse_utc(value)
        except ValueError as e:
            print(e)


# Validate the requested range, returning an error message or None
def validate_range(start, end):
    if end <= start:
        return "The end date/time must be after the start date/time."
    if start < earliest_allowed_start():
        return f"The start date/time cannot be more than {MAX_MONTHS_BACK} months ago (Zoom report limit)."
    return None


# Split the range into consecutive windows of at most 30 days
def build_windows(start, end):
    windows = []
    current = start
    while current < end:
        window_end = min(current + WINDOW - timedelta(seconds=1), end)
        windows.append((current, window_end))
        current = window_end + timedelta(seconds=1)
    return windows


# Request one page; retries on rate limiting. Returns the response
def request_page(url, headers, params):
    # These reports are HEAVY rate limited
    for attempt in range(4):
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 429:
            break
        wait = int(response.headers.get('Retry-After', 5)) if attempt < 3 else 0
        if wait:
            print(f"  Rate limited, retrying in {wait}s...")
            time.sleep(wait)
    return response


def error_message(response):
    try:
        return response.json().get('message', response.text)
    except ValueError:
        return response.text


# Parse a report timestamp such as "2026-10-01T12:34:56Z"
def parse_record_time(value):
    try:
        return datetime.strptime(value[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


# Retrieve every page of one report for one window
def fetch_report(token, label, start, end):
    path, array_key, _, time_field = REPORTS[label]
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }

    # Prefer exact date/times. Some reports reject them (HTTP 400), so fall back
    # to whole UTC days and trim the records to the requested window afterwards.
    for time_format in (API_TIME_FORMAT, API_DATE_FORMAT):
        params = {
            'from': start.strftime(time_format),
            'to': end.strftime(time_format),
            'page_size': PAGE_SIZE
        }
        records = []
        next_page_token = ''
        retry_with_dates = False

        while True:
            if next_page_token:
                params['next_page_token'] = next_page_token

            response = request_page(f"{BASE_URL}{path}", headers, params)

            if response.status_code == 400 and time_format == API_TIME_FORMAT:
                retry_with_dates = True
                break
            if not response.ok:
                raise ReportError(f"HTTP {response.status_code}: {error_message(response)}")

            data = response.json()
            records.extend(data.get(array_key, []))

            next_page_token = data.get('next_page_token', '')
            if not next_page_token:
                break

        if retry_with_dates:
            continue

        if time_format == API_DATE_FORMAT:
            trimmed = []
            for record in records:
                t = parse_record_time(record.get(time_field))
                if t is None or start <= t <= end:
                    trimmed.append(record)
            records = trimmed
        return records


# Retrieve a report across all windows, removing duplicates at window boundaries
def fetch_all(token, label, windows):
    id_fields = REPORTS[label][2]
    seen = set()
    records = []
    for window_start, window_end in windows:
        for record in fetch_report(token, label, window_start, window_end):
            key = next((record[f] for f in id_fields if record.get(f)), None)
            if key is not None:
                if key in seen:
                    continue
                seen.add(key)
            records.append(record)
    return records


# Write records to a CSV file. With a label (combined file) the first column is charge_type
def write_csv(records_by_label, filename, include_type):
    columns = []
    for records in records_by_label.values():
        for record in records:
            for key in record:
                if key not in columns:
                    columns.append(key)

    fieldnames = (["charge_type"] if include_type else []) + columns
    with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for label, records in records_by_label.items():
            for record in records:
                writer.writerow({"charge_type": label, **record} if include_type else record)


# Main function
def main():
    parser = argparse.ArgumentParser(description="Export Zoom Phone call, fax and SMS/MMS charges to separate CSV files plus one combined CSV.")
    parser.add_argument("--start", help="Start date/time in UTC (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)")
    parser.add_argument("--end", help="End date/time in UTC (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)")
    parser.add_argument("--yes", action="store_true", help="Skip the confirmation prompt")
    args = parser.parse_args()

    print("")
    print("Zoom Phone Charges Export")
    print("")

    # Resolve the date range: command-line values first, prompts for anything missing
    try:
        start = parse_utc(args.start) if args.start else None
        end = parse_utc(args.end) if args.end else None
    except ValueError as e:
        print(e)
        sys.exit(1)

    from_command_line = start is not None and end is not None

    if from_command_line:
        error = validate_range(start, end)
        if error:
            print(error)
            sys.exit(1)
    else:
        while True:
            if args.start is None or start is None:
                start = prompt_utc_datetime("start")
            if args.end is None or end is None:
                end = prompt_utc_datetime("end")
            error = validate_range(start, end)
            if not error:
                break
            print(error)
            start = end = None

    windows = build_windows(start, end)
    print(f"Date range (UTC): {start.strftime(API_TIME_FORMAT)} to {end.strftime(API_TIME_FORMAT)}"
          f" ({len(windows)} request window{'s' if len(windows) != 1 else ''} per report)")

    # Only confirm when the range was supplied on the command line
    if from_command_line and not args.yes:
        if input("Proceed? [y/N]: ").strip().lower() not in ("y", "yes"):
            print("Cancelled.")
            sys.exit(0)

    # Get OAuth access token
    access_token = refresh_oauth_token()
    if not access_token:
        sys.exit(1)

    print("")
    results = {}
    failed = []
    for label in REPORTS:
        print(f"Retrieving {label} charges...")
        try:
            results[label] = fetch_all(access_token, label, windows)
            print(f"  {len(results[label])} {label} charge records.")
        except (ReportError, requests.exceptions.RequestException) as e:
            print(f"  Error retrieving {label} charges: {e}")
            failed.append(label)

    total = sum(len(records) for records in results.values())
    print("")
    if not total:
        print("No charge records found, no CSV files created.")
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filenames = []

        # One CSV per report (only for reports that returned records)
        for label, records in results.items():
            if records:
                filename = f"zoom_phone_{label}_charges_{timestamp}.csv"
                write_csv({label: records}, filename, include_type=False)
                filenames.append((filename, len(records)))

        # One combined CSV with a leading charge_type column
        filename = f"zoom_phone_charges_{timestamp}.csv"
        write_csv(results, filename, include_type=True)
        filenames.append((filename, total))

        for name, count in filenames:
            print(f"{count} records written to '{name}'.")

    if failed:
        print(f"WARNING: the following reports could not be retrieved and are missing: {', '.join(failed)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
