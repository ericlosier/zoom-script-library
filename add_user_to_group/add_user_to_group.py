import csv
import sys
import requests
import json
from datetime import datetime

# Zoom API base URL
BASE_URL = "https://api.zoom.us/v2"

# Zoom OAuth endpoints
TOKEN_URL = "https://zoom.us/oauth/token"

# Your Zoom API credentials
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
ACCOUNT_ID = "YOUR_ACCOUNT_ID"

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

        print(f"OAuth token refreshed successfully!")
        
        return access_token
    
    except requests.exceptions.RequestException as e:
        print(f"Error refreshing OAuth token: {e}")
        return None

# Get all Zoom groups and return a mapping of group name to group ID
def get_zoom_groups(token):
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }

    groups = {}
    next_page_token = ''

    try:
        while True:
            params = {'page_size': 100, 'next_page_token': next_page_token}
            response = requests.get(f"{BASE_URL}/groups", headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            for group in data.get('groups', []):
                groups[group['name']] = group['id']

            next_page_token = data.get('next_page_token', '')
            if not next_page_token:
                break

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving Zoom groups: {e}")
        return {}

    return groups

# Add a user to a Zoom group
def add_user_to_group(token, email, group_name, groups_dict):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    group_id = groups_dict.get(group_name)
    if not group_id:
        print(f"Group '{group_name}' not found. Skipping user {email}.")
        return False

    payload = {
        "members": [{"email": email}]
    }

    try:
        response = requests.post(f"{BASE_URL}/groups/{group_id}/members", headers=headers, json=payload)
        if response.status_code == 201 and response.json().get('ids'):
            print(f"Successfully added {email} to group '{group_name}'.")
        elif response.status_code == 201 and not response.json().get('ids'):
            print(f"User {email} not found or already a member of '{group_name}'.")
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error adding {email} to group '{group_name}': {e}")
        return False

    return True

# Main function
def main(csv_file):
    print(f"")
    print(r"""
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
                             |_|        """)
    print(f"")

    # Get OAuth access token
    access_token = refresh_oauth_token()

    if not access_token:
        print("Failed to obtain access token. Exiting.")
        sys.exit(1)

    print("Retrieving Zoom groups...")
    print(f"")

    groups_dict = get_zoom_groups(access_token)
    if not groups_dict:
        print("No groups retrieved. Exiting.")
        sys.exit(1)

    print("Processing users from CSV...")
    print(f"")

    i = 0
    with open(csv_file, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            i += 1
            email = row['email']
            group_name = row['group_name']
            print(f"{i} - Adding {email} to group '{group_name}'...")
            add_user_to_group(access_token, email, group_name, groups_dict)
            print("-" * 50)

    print(f"")
    print(f"All {i} users from CSV processed. Exiting!")

# Check for command-line arguments at runtime
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python add_userto_group.py <users.csv>")
        sys.exit(1)
    main(sys.argv[1])
