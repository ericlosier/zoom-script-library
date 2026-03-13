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

# Check user's current timezone and update with new timezone if needed
def update_user_timezone(token, email, new_timezone):
    
    # Headers for the API request
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
    
    # Get the current timezone
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
    print(f"Current timezone for {current_user['first_name']} {current_user['last_name']}: {current_user['timezone']}")
    
    # Modify timezone only if required
    if current_user['timezone'] != new_timezone:
        try:
            # API endpoint for users
            endpoint = f"{BASE_URL}/users/{email}"
            payload = {
                "timezone": new_timezone
            }
        
            # Make API request
            response = requests.patch(endpoint, json=payload, headers=headers)
            response.raise_for_status()
                
        except requests.exceptions.RequestException as e:
            print(f"Error accessing Zoom API: {e}")
            return False
            
        print(f"New timezone: success!")
    else:
        print(f"New timezone: already set.")
    
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
 |_   _(_)_ __  ___ ______ _ _  ___ 
   | | | | '  \/ -_)_ / _ \ ' \/ -_)
  _|_|_|_|_|_|_\___/__\___/_||_\___|
 | | | |_ __  __| |__ _| |_ ___     
 | |_| | '_ \/ _` / _` |  _/ -_)    
  \___/| .__/\__,_\__,_|\__\___|    
       |_|                          """)
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
            new_timezone = row['timezone']

            print(f"{i} - Processing {email}: {new_timezone}")
            
            update_user_timezone(access_token, email, new_timezone)
                
            print("-" * 50)
    
    print(f"")
    print(f"All {i} users from CSV processed. Exiting!")

# Check for command-line arguments at runtime
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python update_zoom_timezones.py <users.csv>")
        sys.exit(1)
    main(sys.argv[1])
