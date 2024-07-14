import requests
import json
import random
import time
import sys
import os
from http.cookiejar import MozillaCookieJar
from datetime import datetime

# ANSI color codes for terminal output
class colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    END = '\033[0m'

# Function to read registered boards from JSON file
def read_registered_boards(filename):
    try:
        with open(filename, 'r') as f:
            boards = json.load(f)
        return boards
    except FileNotFoundError:
        return []

# Function to convert Netscape cookies to a dictionary
def parse_netscape_cookies(cookie_file):
    cookies = MozillaCookieJar(cookie_file)
    cookies.load()
    cookies_dict = {}
    for cookie in cookies:
        cookies_dict[cookie.name] = cookie.value
    return cookies_dict

# Function to send command to a specific board using cookies
def send_command_to_board_with_cookies(esp_id, command, cookies_file):
    url = 'http://192.168.10.62:5000/command'
    payload = {
        'esp_id': esp_id,
        'command': command
    }
    
    cookies_dict = parse_netscape_cookies(cookies_file)
    try:
        response = requests.post(url, headers={'Content-Type': 'application/x-www-form-urlencoded'}, data=payload, cookies=cookies_dict, timeout=10)
        if response.status_code == 200:
            log(f"Sent command '{command}' to ESP board '{esp_id}' successfully.")
            return True, response
        else:
            log(f"Error: Failed to send command to ESP board '{esp_id}'. Status code: {response.status_code}")
            return False, response
    except requests.exceptions.RequestException as e:
        log(f"Error: Failed to send command to ESP board '{esp_id}'. Exception: {str(e)}")
        return False, None

# Function to retrieve and verify command using esp_id and esp_secret_key
def retrieve_command_with_secret_key(esp_id, esp_secret_key):
    url = 'http://192.168.10.62:5000/get_command'
    params = {
        'esp_id': esp_id,
        'esp_secret_key': esp_secret_key
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            retrieved_command = data.get('command', '')
            log(f"Retrieved command for ESP board '{esp_id}': '{retrieved_command}'")
            return True, response
        else:
            log(f"Failed to retrieve command for ESP board '{esp_id}'. Response status: {response.status_code}")
            return False, response
    except requests.exceptions.RequestException as e:
        log(f"Error: Failed to retrieve command for ESP board '{esp_id}'. Exception: {str(e)}")
        return False, None

# Function to register boards and write to output file
def register_board(server_url, cookies_file, start_id, end_id, output_file):
    try:
        # Load cookies from cookies.txt file
        with open(cookies_file, 'r') as f:
            cookies = {}
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    cookies[parts[0]] = parts[1].strip()

        # Endpoint for registration
        endpoint = f"{server_url}/register_device"

        # Read existing registered boards from file
        existing_boards = read_registered_boards(output_file)
        registered_boards = []

        for esp_id in range(start_id, end_id + 1):
            esp_secret_key = f'esp_secret_key_{esp_id}'  # Generate secret key based on esp_id

            # Check if board is already registered
            esp_id_str = f'esp32_{esp_id}'
            if any(board['esp_id'] == esp_id_str for board in existing_boards):
                log(f"Skipping registration for ESP32 with ID '{esp_id_str}', already registered.")
                continue

            payload = {
                'esp_id': esp_id_str,
                'esp_secret_key': esp_secret_key
            }

            # Send POST request
            try:
                response = requests.post(endpoint, cookies=cookies, data=payload, timeout=10)
                if response.status_code == 200:
                    response_data = response.json()
                    if response_data.get('message') == 'ESP32 registered successfully':
                        log(f"ESP32 with ID '{esp_id_str}' registered successfully with secret key: {esp_secret_key}.")
                        registered_boards.append({
                            'esp_id': esp_id_str,
                            'esp_secret_key': esp_secret_key
                        })
                    else:
                        log(f"Registration failed for {esp_id_str}. Server response: {response_data}")
                else:
                    log(f"Failed to register {esp_id_str}. Status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                log(f"Error: Failed to register {esp_id_str}. Exception: {str(e)}")
                input(f"{colors.YELLOW}Press Enter to continue...{colors.END}")
                return

        # Append newly registered boards to existing list
        existing_boards.extend(registered_boards)

        # Write all registered boards to output file
        with open(output_file, 'w') as outfile:
            json.dump(existing_boards, outfile, indent=4)

    except FileNotFoundError:
        log(f"Error: {cookies_file} not found.")
        input(f"{colors.YELLOW}Press Enter to continue...{colors.END}")

    except Exception as e:
        log(f"Error occurred: {e}")
        input(f"{colors.YELLOW}Press Enter to continue...{colors.END}")

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    with open('log.txt', 'a') as f:
        f.write(log_message + '\n')

# Main function to run the script
def main():
    if len(sys.argv) != 3:
        print("Usage: python board_registration_and_testing.py <start_id> <end_id>")
        return

    start_id = int(sys.argv[1])
    end_id = int(sys.argv[2])
    server_url = 'http://192.168.10.62:5000'
    cookies_file = 'cookies.txt'
    output_file = f'output_{start_id}_to_{end_id}.json'  # Output file specific to this instance

    log(f"Started instance for boards {start_id} to {end_id}")

    register_board(server_url, cookies_file, start_id, end_id, output_file)

    # Test commands (you can add your command testing logic here)

    log(f"Finished instance for boards {start_id} to {end_id}")

if __name__ == "__main__":
    main()
