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
                'account_id': {ACCOUNT_ID}
            }
        )
        auth_response.raise_for_status()
        access_token = auth_response.json()['access_token']
        
        print(f"OAuth token refreshed successfully!")
    
        return access_token
        
    except requests.exceptions.RequestException as e:
        print(f"Error refreshing OAuth token: {e}")
        return None

# Check if user has SSO login method and add if needed
def add_sso(token, email):
    
    # Headers for the GET API request
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json', 
        'Connection': 'keep-alive', 
        'Accept-Encoding': 'gzip, deflate, br', 
        'User-Agent': 'MyScript/1.1'
    }
    
    # Initialize empty list for users
    zoom_users = []
    next_page_token = ''
    
    # Get the current login methods for user
    try:
        while True:
            # API endpoint for users
            endpoint = f"{BASE_URL}/users/{email}"
            params = {
                'page_size': 100,
                'next_page_token': next_page_token
            }
            
            # Make API request
            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Add users to list
            zoom_users.append(data)
            
            # Check if there are more pages
            next_page_token = data.get('next_page_token', '')
            if not next_page_token:
                break
                
    except requests.exceptions.RequestException as e:
        if response.status_code == 404:
            print(f"User not found on Zoom.")
        else:
            print(f"Error accessing Zoom API: {e}")
        return False       
    
    current_user = zoom_users[0]
    print(f"Current login methods for {current_user['first_name']} {current_user['last_name']}: {current_user['login_types']}")
    
    # Headers for the POST & PATCH API requests
    headers_p = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json', 
        'User-Agent': 'MyScript/1.1'
    }
    
    # Check if 101 (SSO) is in the login_types list
    if 101 in current_user.get("login_types", []):
        print(f"SSO Login Method: already set.")
        
    else:
        try:
            # Add the SSO login method -- also use the existing first, last and display names (otherwise, they get blanked out)
            endpoint = f"{BASE_URL}/users"
            payload = {
                "action": "ssoCreate",
                "user_info": {
                    "email": current_user['email'],
                    "first_name": current_user['first_name'],
                    "last_name": current_user['last_name'],
                    "display_name": current_user['display_name'],
                    "type": current_user['type']
                }
            }

            # Make API request
            response = requests.post(endpoint, json=payload, headers=headers_p)
            response.raise_for_status()
                
        except requests.exceptions.RequestException as e:
            print(f"Error accessing Zoom API: {e}")
            return False

        # Update the user's department which was overwritten by the previous API call
        try:
            endpoint = f"{BASE_URL}/users/{email}"
            payload = {
                "dept": current_user['dept'],
            }

            # Make API request
            response = requests.patch(endpoint, json=payload, headers=headers_p)
            response.raise_for_status()
                
        except requests.exceptions.RequestException as e:
            print(f"Error accessing Zoom API: {e}")
            return False
            
            
        # Validate the new SSO login method was indeed added successfully
        zoom_users.clear()
        try:
            while True:
                # API endpoint for users
                endpoint = f"{BASE_URL}/users/{email}"
                params = {
                    'page_size': 100,
                    'next_page_token': next_page_token
                }
            
                # Make API request
                val_response = requests.get(endpoint, headers=headers, params=params)
                val_response.raise_for_status()
            
                data = val_response.json()
            
                # Add users to list
                zoom_users.append(data)
            
                # Check if there are more pages
                next_page_token = data.get('next_page_token', '')
                if not next_page_token:
                    break
                
        except requests.exceptions.RequestException as e:
            if val_response.status_code == 404:
                print(f"User not found on Zoom.")
            else:
                print(f"Error accessing Zoom API: {e}")
            return False       
    
        current_user = zoom_users[0]
        
        # Check if 101 (SSO) is in the login_types list
        if 101 in current_user.get("login_types", []):
            print(f"Added new SSO Login Method: success!")
            
        else:
            print(f"Added new SSO Login Method: failed!")
    
    return True

# Main function
def main(csv_file):
    
    # Welcome message
    print(f"")
    print(r"""
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
       |_|                      """)
    print(f"")

    # Get OAuth access token
    access_token = refresh_oauth_token()
    
    print(f"Cycling through users from CSV...")
    print(f"")
    
    i = 0
    with open(csv_file, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            i += 1
            
            email = row['email']
            print(f"{i} - Processing {email}...")
            add_sso(access_token, email)
            print("-" * 50)
    
    print(f"")
    print(f"All {i} users from CSV processed. Exiting!")

# Check for command-line arguments at runtime
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python add_sso.py <users.csv>")
        sys.exit(1)
    main(sys.argv[1])
