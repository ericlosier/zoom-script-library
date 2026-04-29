# Zoom Download Meeting Transcripts Script `(download_transcripts.py)`

This Python script **downloads meeting transcripts** from Zoom based on a list of **meeting IDs** stored in a text file. It uses the **Zoom REST API (v2)** and authenticates via **OAuth account-level credentials**. The script retrieves the meeting UUID, fetches the transcript metadata, and downloads the transcript file for each meeting.

## 📋 Features

- Authenticates with Zoom using **OAuth (Account Credentials flow)**  
- Reads meeting IDs from a **text file** (`meeting_ids.txt`)  
- Retrieves the meeting UUID via the **Past Meetings API**  
- Fetches transcript metadata and download URL for each meeting  
- Automatically detects transcript format (**VTT** or **TXT**) based on content type  
- Saves transcripts to a local `transcripts/` output directory  
- Provides detailed console output with status icons for each processed meeting  

## 🧩 Requirements

- Python 3.7 or higher  
- Zoom account with **Server-to-Server OAuth App** credentials  [(instructions)](https://github.com/ericlosier/zoom-script-library/wiki/Creating-a-Zoom-Server%E2%80%90to%E2%80%90Server-OAuth-App)
- Required Python packages:
  - `requests`
  - `os` (default)
  - `sys` (default)

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

These values come from your **Zoom Server-to-Server OAuth App Credentials** [(instructions)](https://github.com/ericlosier/zoom-script-library/wiki/Creating-a-Zoom-Server%E2%80%90to%E2%80%90Server-OAuth-App).

### 🔐 Zoom Server-to-Server OAuth App Scopes
The following granular scopes should be added to the Zoom Server-to-Server OAuth app used by this script:

- meeting:read:past_meeting:admin  
- meeting:read:transcript:admin  

## 🚀 Usage
Run the script directly from the command line with a `meeting_ids.txt` file in the same directory:

```bash
python download_transcripts.py
```

## 🧠 How It Works
1. **Obtain OAuth Token**

	The script calls the Zoom OAuth token endpoint (`https://zoom.us/oauth/token`) using the **account_credentials** grant type to retrieve an access token.

2. **Read Meeting IDs File**

	It reads each line from the `meeting_ids.txt` input file, collecting all meeting IDs to process.

3. **Retrieve Meeting UUID**

	For each meeting ID, the script calls the `/past_meetings/{meetingId}` endpoint to retrieve the meeting's UUID.

4. **Fetch Transcript Metadata**

	Using the meeting UUID, the script calls the `/meetings/{meetingId}/transcript` endpoint to obtain the transcript download URL.

5. **Download and Save Transcript**

	The script downloads the transcript file from the provided URL, detects the file format (VTT or TXT) based on the response content type, and saves it to the `transcripts/` directory.

## 🧰 Functions Overview
| Function | Description |
|---|---|
| `get_access_token()` | Retrieves a new OAuth access token using account credentials. |
| `download_transcript_for_meeting(meeting_id, token)` | Retrieves the meeting UUID, fetches transcript metadata, downloads the transcript file, and saves it locally. |
| `main()` | Main entry point that validates configuration, reads meeting IDs from file, and orchestrates transcript downloads. |

## ⚠️ Error Handling
- If the OAuth token request fails, the script prints an error message and exits.  

- If a meeting ID cannot be resolved to a UUID, the script logs a warning and skips that meeting.  

- If no transcript is available for a meeting, the script logs the issue and continues to the next meeting.  

- If the transcript download fails, the script logs the HTTP status and response details.  

- The script strips whitespace from meeting IDs to handle formatting inconsistencies in the input file.

## 🧾 Example Input File (`meeting_ids.txt`)
```
81234567890
89876543210
85551234567
```

## 🧑‍💻 Example Console Output
```
✅ Saved transcript for 81234567890 → transcripts/81234567890_transcript.vtt
⚠️ Failed to fetch transcript metadata for 89876543210: 404 {"code":3001,"message":"Meeting does not exist."}
ℹ️ No download_url in transcript response for 85551234567
```

## 📚 References
- [Creating a Zoom Server‐to‐Server OAuth App](https://github.com/ericlosier/zoom-script-library/wiki/Creating-a-Zoom-Server%E2%80%90to%E2%80%90Server-OAuth-App)
- Zoom API Documentation:
  - [GET /past_meetings/{meetingId}](https://developers.zoom.us/docs/api/meetings/#tag/meetings/get/past_meetings/{meetingId})
  - [GET /meetings/{meetingId}/transcript](https://developers.zoom.us/docs/api/meetings/#tag/cloud-recording/get/meetings/{meetingId}/transcript)
