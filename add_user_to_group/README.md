# Zoom Add User to Group Script `(add_user_to_group.py)`

This Python script adds **users to Zoom groups** based on data from a **CSV file**. It uses the **Zoom REST API (v2)** and authenticates via **OAuth account-level credentials**. The script retrieves all existing Zoom groups, matches them by name, and adds users to the appropriate group.

## 📋 Features

- Authenticates with Zoom using **OAuth (Account Credentials flow)**  
- Reads user email and target group name from a **CSV file**  
- Retrieves all existing Zoom groups and maps names to IDs  
- Adds each user to the specified group  
- Provides detailed console output for each processed user  

## 🧩 Requirements

- Python 3.7 or higher  
- Zoom account with **Server-to-Server OAuth App** credentials  [(instructions)](https://github.com/ericlosier/zoom-script-library/wiki/Creating-a-Zoom-Server%E2%80%90to%E2%80%90Server-OAuth-App)
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

These values come from your **Zoom Server-to-Server OAuth App Credentials** [(instructions)](https://github.com/ericlosier/zoom-script-library/wiki/Creating-a-Zoom-Server%E2%80%90to%E2%80%90Server-OAuth-App).

### 🔐 Zoom Server-to-Server OAuth App Scopes
The following granular scopes should be added to the Zoom Server-to-Server OAuth app used by this script:

- group:read:list_groups:admin  
- group:write:member:admin  

## 🚀 Usage
Run the script directly from the command line with a CSV file containing user data:

```bash
python add_user_to_group.py users.csv
```

## 🧠 How It Works
1. **Obtain OAuth Token**

	The script calls the Zoom OAuth token endpoint (`https://zoom.us/oauth/token`) using the **account_credentials** grant type to retrieve an access token.

2. **Retrieve Zoom Groups**

	It calls the `/groups` endpoint to get all existing groups and builds a mapping of group names to group IDs.

3. **Read CSV File**

	It reads each row from the provided CSV file, extracting the user’s email and target group name.

4. **Add User to Group**

	For each user, the script calls the `/groups/{groupId}/members` endpoint to add the user to the specified group.

5. **Log Results**

	Each operation is logged to the console, showing whether the user was successfully added or skipped.

## 🧰 Functions Overview
| Function | Description |
|---|---|
| `refresh_oauth_token()` | Retrieves a new OAuth access token using account credentials. |
| `get_zoom_groups(token)` | Retrieves all Zoom groups and returns a mapping of group names to IDs. |
| `add_user_to_group(token, email, group_name, groups_dict)` | Adds a user to the specified Zoom group. |
| `main(csv_file)` | Main entry point that orchestrates token retrieval, group lookup, and user addition. |

## ⚠️ Error Handling
- If the OAuth token request fails, the script prints an error message and exits.  

- If a group name from the CSV does not exist, the script logs a warning and skips that user.  

- If a user is not found or already a member, the script logs the issue to the console.  

- The script handles network or API exceptions gracefully.

## 🧾 Example CSV File
| email | group_name |
|---|---|
| user1@example.com | Sales Team |
| user2@example.com | Marketing |

## 🧑‍💻 Example Console Output
```
  ____                                
 |_  /___  ___ _ __                   
  / // _ \/ _ \ '  \                  
 /___\___/\___/_|_|_|   _             
   /_\  __| |__| | | | | |___ ___ _ _ 
  / _ \/ _` / _` | | |_| (_-</ -_) '_|
 /_/ \_\__,_\__,_|  \___//__/\___|_|  
 | |_ ___   / __|_ _ ___ _  _ _ __      
 |  _/ _ \ | (_ | '_/ _ \ || | '_ \     
  \__\___/  \___|_| \___/\_,_| .__/     
                             |_|        

OAuth token refreshed successfully!

Retrieving Zoom groups...

Processing users from CSV...

1 - Adding user1@example.com to group 'Sales Team'...
Successfully added user1@example.com to group 'Sales Team'.
--------------------------------------------------
2 - Adding user2@example.com to group 'Marketing'...
User user2@example.com not found or already a member of 'Marketing'.
--------------------------------------------------

All 2 users from CSV processed. Exiting!
```

## 📚 References
- [Creating a Zoom Server‐to‐Server OAuth App](https://github.com/ericlosier/zoom-script-library/wiki/Creating-a-Zoom-Server%E2%80%90to%E2%80%90Server-OAuth-App)
- Zoom API Documentation:
  - [GET /groups](https://developers.zoom.us/docs/api/users/#tag/groups/get/groups)
  - [POST /groups/{groupId}/members](https://developers.zoom.us/docs/api/users/#tag/groups/post/groups/{groupId}/members)
  