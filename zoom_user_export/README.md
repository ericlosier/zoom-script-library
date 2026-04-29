# Zoom Users Export Script `(zoom_user_export.py)`

This Python script exports **all users from a Zoom account** to a **timestamped CSV file**. It uses the **Zoom REST API (v2)** and authenticates via **OAuth account-level credentials**. The script retrieves every user in the account, fetches detailed profile information including login types, and writes the results to a CSV file.

## 📋 Features

- Authenticates with Zoom using **OAuth (Account Credentials flow)**  
- Retrieves **all users** in the Zoom account with automatic pagination  
- Fetches **detailed user profiles** including login type information  
- Maps numeric login type codes to **human-readable labels**  
- Exports users to a **timestamped CSV file** (`zoom_users_YYYYMMDD_HHMMSS.csv`)  

## 🧩 Requirements

- Python 3.8 or higher  
- Zoom account with **Server-to-Server OAuth App** credentials  [(instructions)](https://github.com/ericlosier/zoom-script-library/wiki/Creating-a-Zoom-Server%E2%80%90to%E2%80%90Server-OAuth-App)
- Required Python packages:
  - `requests`
  - `csv` (default)
  - `base64` (default)
  - `sys` (default)
  - `datetime` (default)
  - `dataclasses` (default)

Install dependencies (if not already available):

```bash
pip install requests
```

## ⚙️ Configuration
Before running the script, update the following variables in the file:

```
CLIENT_ID: str = "CLIENT_ID"
CLIENT_SECRET: str = "CLIENT_SECRET"
ACCOUNT_ID: str = "ACCOUNT_ID"
```

These values come from your **Zoom Server-to-Server OAuth App Credentials** [(instructions)](https://github.com/ericlosier/zoom-script-library/wiki/Creating-a-Zoom-Server%E2%80%90to%E2%80%90Server-OAuth-App).

### 🔐 Zoom Server-to-Server OAuth App Scopes
The following granular scopes should be added to the Zoom Server-to-Server OAuth app used by this script:

- user:read:list_users:admin  
- user:read:user:admin  

## 🚀 Usage
Run the script directly from the command line:

```bash
python zoom_user_export.py
```

## 🧠 How It Works
1. **Obtain OAuth Token**

	The script calls the Zoom OAuth token endpoint (`https://zoom.us/oauth/token`) using the **account_credentials** grant type to retrieve an access token.

2. **Retrieve All Users**

	It calls the `/users` endpoint with pagination (using `next_page_token`) to retrieve all users in the account.

3. **Fetch User Details**

	For each user returned by the list endpoint, the script calls `/users/{userId}` to retrieve full profile details including login type information.

4. **Map Login Types**

	Numeric login type codes are mapped to human-readable labels (e.g., `100` → `Work Email`, `101` → `Single Sign-On (SSO)`).

5. **Export to CSV**

	All user data is written to a timestamped CSV file containing id, email, first name, last name, status, type, login type code, and login type label.

## 🧰 Functions Overview
| Function | Description |
|---|---|
| `_encode_basic_auth(client_id, client_secret)` | Encodes client credentials for HTTP Basic auth header. |
| `get_access_token(client_id, client_secret, account_id)` | Retrieves a new OAuth access token using account credentials. |
| `map_login_type(code)` | Maps a numeric login type code to a human-readable label. |
| `_get_user_detail(access_token, user_id)` | Fetches full user details from `/users/{userId}`. |
| `get_zoom_users(access_token, page_size)` | Retrieves all users with pagination and fetches detailed profiles. |
| `write_users_to_csv(users, filename_prefix)` | Writes user data to a timestamped CSV file. |
| `main()` | Main entry point that orchestrates token retrieval, user fetching, and CSV export. |

## ⚠️ Error Handling
- If the OAuth token request fails, the script prints an error message and exits.  

- If fetching user details fails for a specific user, the script raises an error with the status code and response.  

- If no users are returned by the Zoom API, the script logs a message to the console.  

- The script handles network exceptions (`requests.RequestException`) and generic errors gracefully.

## 🧾 Example CSV Output
| id | email | first_name | last_name | status | type | login_type_code | login_type_label |
|---|---|---|---|---|---|---|---|
| AbC123xYz | user1@example.com | John | Smith | active | 2 | 100 | Work Email |
| DeF456uVw | user2@example.com | Jane | Doe | active | 2 | 100, 101 | Work Email, Single Sign-On (SSO) |

## 🧑‍💻 Example Console Output
```
Requesting Zoom access token...
Access token obtained.
Fetching users from Zoom...
Fetched 150 users.
Writing users to CSV...
Export complete: zoom_users_20260429_120000.csv
```

## 📚 References
- [Creating a Zoom Server‐to‐Server OAuth App](https://github.com/ericlosier/zoom-script-library/wiki/Creating-a-Zoom-Server%E2%80%90to%E2%80%90Server-OAuth-App)
- Zoom API Documentation:
  - [GET /users](https://developers.zoom.us/docs/api/users/#tag/users/get/users)
  - [GET /users/{userId}](https://developers.zoom.us/docs/api/users/#tag/users/get/users/{userId})
