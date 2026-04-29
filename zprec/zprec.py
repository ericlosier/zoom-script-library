import requests
import csv
import datetime
import os
import json

# ============================================
# Zoom Phone Call Recordings Export Script
# ============================================

# This script:
# 1. Authenticates with Zoom API using Server-to-Server OAuth.
# 2. Prompts the user for a start and end date.
# 3. Retrieves Zoom Phone call recordings within that date range.
# 4. Exports metadata (including filename) to a CSV file.
# 5. Downloads the recordings to a local folder.

# -----------------------------
# Configuration
# -----------------------------
ZOOM_ACCOUNT_ID = "ACCOUNT_ID"
ZOOM_CLIENT_ID = "CLIENT_ID"
ZOOM_CLIENT_SECRET = "CLIENT_SECRET"

TOKEN_URL = "https://zoom.us/oauth/token"
CALL_RECORDINGS_URL = "https://api.zoom.us/v2/phone/recordings"

# -----------------------------
# Step 1: Get OAuth Access Token
# -----------------------------
def get_access_token():
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "grant_type": "account_credentials",
        "account_id": ZOOM_ACCOUNT_ID
    }
    response = requests.post(
        TOKEN_URL,
        headers=headers,
        auth=(ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET),
        data=payload
    )
    response.raise_for_status()
    return response.json()["access_token"]

# -----------------------------
# Step 2: Fetch Call Recordings
# -----------------------------
def fetch_call_recordings(access_token, start_date, end_date):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "from": start_date,
        "to": end_date,
        "page_size": 50
    }

    all_recordings = []
    next_page_token = None

    while True:
        if next_page_token:
            params["next_page_token"] = next_page_token

        response = requests.get(CALL_RECORDINGS_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        recordings = data.get("recordings", [])
        all_recordings.extend(recordings)

        next_page_token = data.get("next_page_token")
        if not next_page_token:
            break

    return all_recordings

# -----------------------------
# Step 3: Export Metadata to CSV
# -----------------------------
def export_metadata_to_csv(recordings, csv_filename="zoom_phone_recordings.csv"):
    fieldnames = [
        "call_id", "caller_number", "callee_number", "direction",
        "start_time", "end_time", "duration", "recording_file_name", "download_url"
    ]
    print(json.dumps(recordings, indent=4))

    with open(csv_filename, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for rec in recordings:
            writer.writerow({
                "call_id": rec.get("id"),
                "caller_number": rec.get("caller_number"),
                "callee_number": rec.get("callee_number"),
                "direction": rec.get("direction"),
                "start_time": rec.get("date_time"),
                "end_time": rec.get("end_time"),
                "duration": rec.get("duration"),
                "recording_file_name": f"{rec.get('id')}.mp3",
                "download_url": rec.get("download_url")
            })

    print(f"✅ Metadata exported to {csv_filename}")

# -----------------------------
# Step 4: Download Recordings
# -----------------------------
def download_recordings(recordings, access_token, output_dir="recordings"):
    os.makedirs(output_dir, exist_ok=True)
    headers = {"Authorization": f"Bearer {access_token}"}

    for rec in recordings:
        file_url = rec.get("download_url")
        file_name = rec.get("recording_file_name", f"{rec.get('id')}.mp3")

        if not file_url:
            continue

        response = requests.get(file_url, headers=headers, stream=True)
        if response.status_code == 200:
            file_path = os.path.join(output_dir, file_name)
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded: {file_name}")
        else:
            print(f"Failed to download {file_name}: {response.status_code}")

# -----------------------------
# Main Execution
# -----------------------------
if __name__ == "__main__":
    print("=== Zoom Phone Call Recordings Export ===")
    start_date = input("Enter start date (YYYY-MM-DD): ").strip()
    end_date = input("Enter end date (YYYY-MM-DD): ").strip()

    try:
        datetime.datetime.strptime(start_date, "%Y-%m-%d")
        datetime.datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        print("❌ Invalid date format. Please use YYYY-MM-DD.")
        exit(1)

    print("Authenticating with Zoom API...")
    token = get_access_token()

    print("Fetching call recordings...")
    recordings = fetch_call_recordings(token, start_date, end_date)

    if not recordings:
        print("No recordings found for the given date range.")
        exit(0)

    print(f"Found {len(recordings)} recordings.")
    export_metadata_to_csv(recordings)
    download_recordings(recordings, token)

    print("✅ Export completed successfully.")