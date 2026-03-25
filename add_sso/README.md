# Zoom Add SSO Login Method Script `(add_sso.py)`

This Python script adds the **SSO login method** to Zoom users based on data from a **CSV file**. It uses the **Zoom REST API (v2)** and authenticates via **OAuth account-level credentials**. The script checks each user’s current login methods and adds SSO only if it is not already configured.

## 📋 Features

- Authenticates with Zoom using **OAuth (Account Credentials flow)**  
- Reads user email from a **CSV file**  
- Retrieves each user’s current login methods from Zoom  
- Adds the **SSO login method (101)** if it is not already present  
- Provides detailed console output for each processed user  

## 🧩 Requirements

- Python 3.7 or higher  
- Zoom account with **Server-to-Server OAuth App** credentials  
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
- user:write:user:admin  

## 🚀 Usage
Run the script directly from the command line with a CSV file containing user data:

```bash
python add_sso.py users.csv
```

## 🧠 How It Works
1. **Obtain OAuth Token**

   The script calls the Zoom OAuth token endpoint (`https://zoom.us/oauth/token`) using the **account_credentials** grant type to retrieve an access token.

2. **Read CSV File**

   It reads each row from the provided CSV file, extracting the user’s email.

3. **Retrieve Current Login Methods**

   For each user, the script calls the `/users/{email}` endpoint to get the current login methods.

4. **Add SSO Login Method (if needed)**

   If the user’s login methods do not include SSO (code `101`), the script sends a POST request to create the SSO login method and then restores the user’s department field (this field is overwritten by the SSO login method creation process).

5. **Validate Update**

   The script rechecks the user’s login methods to confirm that SSO was successfully added.

6. **Log Results**

   Each operation is logged to the console, showing whether the SSO login method was added or already set.

## 🧰 Functions Overview
| Function | Description |
|---|---|
| `refresh_oauth_token()` | Retrieves a new OAuth access token using account credentials. |
| `add_sso(token, email)` | Checks and adds the SSO login method for a user if not already present. |
| `main(csv_file)` | Main entry point that orchestrates token retrieval and SSO updates. |

## ⚠️ Error Handling
- If the OAuth token request fails, the script prints an error message and exits.  
- If a user is not found or the API returns an error, it logs the issue to the console.  
- The script validates CSV input and handles network or API exceptions gracefully.  

## 🧾 Example CSV File
| email |
|---|
| user1@example.com |
| user2@example.com |

## 🧑‍💻 Example Console Output
```
  ____                          
 |_  /___  ___ _ __             
  / // _ \/ _ \ '  \            
 /___\___/\___/_|_|_|           
 / __/ __|/ _ \                 
 \__ \__ \ (_) |                
 |___/___/\___/  _      _       
 | | | |_ __  __| |__ _| |_ ___ 
 | |_| | '_ \/ _` / _` |  _/ -_)
  \___/| .__/\__,_\__,_|\__\___|
       |_|                      

OAuth token refreshed successfully!

Cycling through users from CSV...

1 - Processing user1@example.com...
Current login methods for John Doe: [0]
Added new SSO Login Method: success!
--------------------------------------------------
2 - Processing user2@example.com...
Current login methods for Jane Smith: [0, 101]
SSO Login Method: already set.
--------------------------------------------------

All 2 users from CSV processed. Exiting!
```

## 📚 References
- [Creating a Zoom Server‐to‐Server OAuth App](https://github.com/ericlosier/zoom-script-library/wiki/Creating-a-Zoom-Server%E2%80%90to%E2%80%90Server-OAuth-App)
- Zoom API Documentation:
  - [GET /users/{userId}](https://developers.zoom.us/docs/api/users/#tag/users/get/users/{userId})
  - [PATCH /users/{userId}](https://developers.zoom.us/docs/api/users/#tag/users/patch/users/{userId})
  - [POST /users](https://developers.zoom.us/docs/api/users/#tag/users/post/users)
  