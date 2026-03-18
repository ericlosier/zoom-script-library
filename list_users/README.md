# Zoom Active Users Export Script `(list_users.py)`

This Python script retrieves a list of **active Zoom users** from your Zoom account using the **Zoom REST API (v2)** and exports the results to a **CSV file**. It uses **OAuth account-level credentials** for authentication and handles pagination automatically.

## 📋 Features

- Authenticates with Zoom using **OAuth (Account Credentials flow)**  
- Retrieves all **active users** from your Zoom account  
- Handles **pagination** to fetch all users beyond the first page  
- Exports user details to a **timestamped CSV file**  
- Includes a reusable **CSV export utility** for lists or dictionaries 

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

These values come from your **Zoom Server-to-Server OAuth App Credentials**. More info on this topic can be found in [**this Wiki page**](https://github.com/ericlosier/zoom-script-library/wiki/Creating-a-Zoom-Server%E2%80%90to%E2%80%90Server-OAuth-App).

### 🔐 Zoom Server-to-Server OAuth App Scopes
The following granular scopes should be added to the Zoom Server-to-Server OAuth app used by this script:

- user:read:list\_users:admin

## 🚀 Usage
Run the script directly from the command line:

```python list_users.txt```

Optionally, you can specify a custom CSV filename:

```python list_users.txt custom_output.csv```

If no filename is provided, the script automatically generates one in the format:

`zoom_active_users_YYYYMMDD_HHMMSS.csv`

## 🧠 How It Works
**1. Obtain OAuth Token**

The script calls the Zoom OAuth token endpoint (`https://zoom.us/oauth/token`) using the **account_credentials** grant type to retrieve an access token.

**2. Fetch Active Users**

It sends a GET request to the `/users` endpoint with `status=active` and iterates through all pages using the `next_page_token`.

**3. Export to CSV**

The retrieved user data is written to a CSV file using the `list_to_csv()` helper function.

## 🧾 Output Example
The generated CSV file includes columns such as:

- id
- first_name
- last_name
- email
- type
- pmi
- timezone
- verified
- created_at

All attributes returned by the  [GET /users API endpoint](https://developers.zoom.us/docs/api/users/#tag/users/get/users) are included in the CSV output.

## 🧰 Functions Overview
| Function | Description |
|---|---|
| `refresh_oauth_token()` | Retrieves a new OAuth access token using account credentials. |
| `list_to_csv(data, filename, delimiter)` | Converts a list of dictionaries or lists into a CSV file. |
| `list_active_users(token)` | Fetches all active Zoom users and writes them to a CSV file. |
| `main(csv_file)` | Main entry point that orchestrates token retrieval and user export. |

## ⚠️ Error Handling
- If the OAuth token request fails, the script prints an error message and exits.
- If no users are found or the API returns an error, it logs the issue to the console.
- The CSV export function validates input data and raises descriptive errors for invalid formats.

## 🧑‍💻 Example Console Output
```
  ____                 
 |_  /___  ___ _ __    
  / // _ \/ _ \ '  \   
 /___\___/\___/_|_|_|  
 | |  (_)__| |_        
 | |__| (_-<  _|       
 |____|_/__/\__|       
 | | | |___ ___ _ _ ___
 | |_| (_-</ -_) '_(_-<
  \___//__/\___|_| /__/
                       
OAuth token refreshed successfully!

Retrieving active users list from Zoom...
Successfully retrieved 125 users from Zoom.

CSV file 'zoom_active_users_20260313_153845.csv' created successfully. Exiting!
```

## 📚 References
- [Creating a Zoom Server‐to‐Server OAuth App](https://github.com/ericlosier/zoom-script-library/wiki/Creating-a-Zoom-Server%E2%80%90to%E2%80%90Server-OAuth-App)
- Zoom API Documentation:
	- [GET /users](https://developers.zoom.us/docs/api/users/#tag/users/get/users)
