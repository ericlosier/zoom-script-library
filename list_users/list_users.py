import csv
import sys
import requests
import json
import datetime

# Zoom API base URL
BASE_URL = "https://api.zoom.us/v2"
    
# Zoom OAuth endpoints
TOKEN_URL = "https://zoom.us/oauth/token"

# Your Zoom API credentials
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
ACCOUNT_ID = "YOUR_ACCOUNT_ID"

# CSV filename
CSV_OUTPUT_FILE = "zoom_active_users_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv"

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

# Convert LIST or DICT array object to CSV and output to file
def list_to_csv(data, filename, delimiter=","):
    """
    Converts a list of dictionaries or lists into a CSV file.

    Args:
        data (list): List of dictionaries or lists containing the data to write.
        filename (str): Output CSV filename (default: 'output.csv').
        delimiter (str): Delimiter character for the CSV file (default: ',').

    Returns:
        str: Confirmation message indicating success or failure.
    """
    try:
        # Validate that input is a list
        if not isinstance(data, list):
            raise TypeError("Input data must be a list.")

        if not data:
            raise ValueError("Input list is empty. No data to write.")

        # Case 1: List of dictionaries
        if all(isinstance(item, dict) for item in data):
            # Collect all unique keys for headers
            headers = set()
            for item in data:
                headers.update(item.keys())
            headers = sorted(headers)

            with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
                writer.writeheader()
                for item in data:
                    writer.writerow({key: item.get(key, "") for key in headers})

        # Case 2: List of lists
        elif all(isinstance(item, list) for item in data):
            with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
                for row in data:
                    writer.writerow(row)

        else:
            raise TypeError("All elements in the list must be of the same type (dict or list).")

        #print(f"CSV file '{filename}' created successfully.")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False


    return True

# Retrieve list of active users and create CSV file with user details
def list_active_users(token):
    
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
    
    # Get the list of active users
    try:
        while True:
            # API endpoint for listing users
            endpoint = f"{BASE_URL}/users"
            params = {
                'status': 'active',
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
            print(f"No users found on Zoom.")
        else:
            print(f"Error accessing Zoom API: {e}")
        return False       
    
    # print(f"{zoom_users}")

    # Get the number of items (users) in the array
    num_items = zoom_users[0]['total_records']
    
    print(f"Successfully retrieved {num_items} users from Zoom.")
    print(f"")

    if list_to_csv(zoom_users[0]['users'], CSV_OUTPUT_FILE):
        print(f"CSV file '{CSV_OUTPUT_FILE}' created successfully. Exiting!")
    else:
        print(f"Error creating '{CSV_OUTPUT_FILE}', aborting.")
            
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
 | |  (_)__| |_        
 | |__| (_-<  _|       
 |____|_/__/\__|       
 | | | |___ ___ _ _ ___
 | |_| (_-</ -_) '_(_-<
  \___//__/\___|_| /__/
                       """)
    print(f"")

    # Get OAuth access token
    access_token = refresh_oauth_token()
    
    print(f"")
    print(f"Retrieving active users list from Zoom...")
    
    list_active_users(access_token)
    

# Check for command-line arguments at runtime
if __name__ == "__main__":
    if len(sys.argv) != 2:
        main(CSV_OUTPUT_FILE)
    else:
        main(sys.argv[1])
