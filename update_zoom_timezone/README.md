# Zoom User Timezone Update Script `(update_zoom_timezone.py)`

This Python script updates the **timezone** of Zoom users based on data from a **CSV file**. It uses the **Zoom REST API (v2)** and authenticates via **OAuth account-level credentials**. The script checks each user’s current timezone and updates it only if a change is required.

## 📋 Features

- Authenticates with Zoom using **OAuth (Account Credentials flow)**  
- Reads user email and target timezone from a **CSV file**  
- Retrieves each user’s current timezone from Zoom  
- Updates the user’s timezone only if it differs from the desired value  
- Provides detailed console output for each processed user  

## 🧩 Requirements

- Python 3.7 or higher  
- Zoom account with **OAuth App (Server-to-Server)** credentials  
- Required Python packages:
  - `requests`
  - `csv` (default)
  - `json` (default)
  - `datetime` (default)

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

These values come from your **Zoom App Credentials** in the Zoom Developer Portal.

### 🔐 Zoom Server-to-Server OAuth App Scopes
The following granular scopes should be added to the Zoom Server-to-Server OAuth app used by this script:

- user:read:user:admin
- user:update:user:admin

## 🚀 Usage
Run the script directly from the command line with a CSV file containing user data:

```python update_zoom_timezone.py users.csv```

## 🧠 How It Works
**1. Obtain OAuth Token**

The script calls the Zoom OAuth token endpoint (`https://zoom.us/oauth/token`) using the **account_credentials** grant type to retrieve an access token.

**2. Read CSV File**

It reads each row from the provided CSV file, extracting the user’s email and desired timezone.

**3. Retrieve Current Timezone**

For each user, the script calls the `/users/{email}` endpoint to get the current timezone.

**4. Update Timezone (if needed)**

If the user’s current timezone differs from the target timezone, the script sends a PATCH request to update it.

**5. Log Results**

Each operation is logged to the console, showing whether the timezone was updated or already correct.

## 🧰 Functions Overview
| Function | Description |
|---|---|
| `refresh_oauth_token()` | Retrieves a new OAuth access token using account credentials. |
| `update_user_timezone(token, email, new_timezone)` | Checks and updates a user’s timezone if necessary. |
| `main(csv_file)` | Main entry point that orchestrates token retrieval and timezone updates. |

## ⚠️ Error Handling
- If the OAuth token request fails, the script prints an error message and exits.
- If a user is not found or the API returns an error, it logs the issue to the console.
- The script validates CSV input and handles network or API exceptions gracefully.

## 🧾 Example CSV File
| email | timezone |
|---|---|
| user1@example.com | America/Toronto |
| user2@example.com | Europe/Rome |

Timezones should be defined using the `TZ Identifier` from the [IANA time zone database](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List)

## 🧑‍💻 Example Console Output
```
  ____                              
 |_  /___  ___ _ __                 
  / // _ \/ _ \ '  \                
 /___\___/\___/_|_|_|               
 |_   _(_)_ __  ___ ______ _ _  ___ 
   | | | | '  \/ -_)_ / _ \ ' \/ -_)
  _|_|_|_|_|_|_\___/__\___/_||_\___|
 | | | |_ __  __| |__ _| |_ ___     
 | |_| | '_ \/ _` / _` |  _/ -_)    
  \___/| .__/\__,_\__,_|\__\___|    
       |_|                          

OAuth token refreshed successfully!

Cycling through users from CSV...

1 - Processing user1@example.com: America/Toronto
Current timezone for John Doe: UTC
New timezone: success!
--------------------------------------------------
2 - Processing user2@example.com: Europe/London
Current timezone for Jane Smith: Europe/London
New timezone: already set.
--------------------------------------------------

All 2 users from CSV processed. Exiting!
```

## 📚 References
- [Creating a Zoom Server‐to‐Server OAuth App](https://github.com/ericlosier/zoom-script-library/wiki/Creating-a-Zoom-Server%E2%80%90to%E2%80%90Server-OAuth-App)
- Zoom API Documentation:
	- [GET /users/{userId}](https://developers.zoom.us/docs/api/users/#tag/users/get/users/{userId})
	- [PATCH /users/{userId}](https://developers.zoom.us/docs/api/users/#tag/users/patch/users/{userId})
