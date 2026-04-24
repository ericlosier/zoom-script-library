import os
import sys
import requests

# Configuration — get these from environment or config
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
ACCOUNT_ID = "YOUR_ACCOUNT_ID"

INPUT_FILE = "meeting_ids.txt"
OUTPUT_DIR = "transcripts"

OAUTH_TOKEN_URL = (
    "https://zoom.us/oauth/token"
    + f"?grant_type=account_credentials&account_id={ACCOUNT_ID}"
)
MEETING_ENDPOINT = "https://api.zoom.us/v2/past_meetings/{meetingId}"
TRANSCRIPT_ENDPOINT = "https://api.zoom.us/v2/meetings/{meetingId}/transcript"

def get_access_token():
    resp = requests.post(
        OAUTH_TOKEN_URL,
        auth=(CLIENT_ID, CLIENT_SECRET)
    )
    if resp.status_code != 200:
        print("❌ Could not get access token:", resp.status_code, resp.text)
        sys.exit(1)
    return resp.json()["access_token"]

def download_transcript_for_meeting(meeting_id, token):
    meeting_id = meeting_id.replace(" ", "")  # Strip spaces

    headers = {"Authorization": f"Bearer {token}"}
    
    # Get the meeting UUID
    meeting_url = MEETING_ENDPOINT.format(meetingId=meeting_id)
    meeting_resp = requests.get(meeting_url, headers=headers)
    if meeting_resp.status_code != 200:
        print(f"⚠️ Failed to fetch meeting UUID for {meeting_id}:",
              meeting_resp.status_code, meeting_resp.text)
        print(f"URL was {meeting_url}")
        return

    meeting = meeting_resp.json()
    meeting_uuid = meeting.get("uuid")
    if not meeting_uuid:
        print(f"ℹ️ No UUID in meeting response for {meeting_id}")
        return
    
    
    url = TRANSCRIPT_ENDPOINT.format(meetingId=meeting_uuid)
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"⚠️ Failed to fetch transcript metadata for {meeting_id}:",
              resp.status_code, resp.text)
        print(f"URL was {url}")
        return

    info = resp.json()
    download_url = info.get("download_url")
    if not download_url:
        print(f"ℹ️ No download_url in transcript response for {meeting_id}")
        return

    # Fetch the transcript file
    dl_resp = requests.get(download_url, headers=headers)
    if dl_resp.status_code != 200:
        print(f"⚠️ Failed to download transcript for {meeting_id}:",
              dl_resp.status_code, dl_resp.text)
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # Use generic extension since we don't know exact type — e.g. .vtt or .txt
    filename = os.path.join(OUTPUT_DIR, f"{meeting_id}_transcript")
    # Try to detect encoding / extension from headers
    content_type = dl_resp.headers.get("Content-Type", "")
    if "vtt" in content_type.lower() or dl_resp.content.startswith(b"WEBVTT"):
        filename += ".vtt"
    else:
        filename += ".txt"
    with open(filename, "wb") as f:
        f.write(dl_resp.content)
    print(f"✅ Saved transcript for {meeting_id} → {filename}")

def main():
    if not all([CLIENT_ID, CLIENT_SECRET, ACCOUNT_ID]):
        print("❌ Missing one of ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET, ZOOM_ACCOUNT_ID")
        sys.exit(1)
    if not os.path.exists(INPUT_FILE):
        print("❌ Input file not found:", INPUT_FILE)
        sys.exit(1)

    token = get_access_token()
    with open(INPUT_FILE, "r") as f:
        meeting_ids = [line.strip() for line in f if line.strip()]

    for mid in meeting_ids:
        download_transcript_for_meeting(mid, token)

if __name__ == "__main__":
    main()