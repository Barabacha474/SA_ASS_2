import subprocess
import time
import socket
import argparse
from threading import Thread
from datetime import datetime
import difflib
import os
import hashlib

# Constants for client-server communication
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 10000
separator_token = "<SEP>"
message = "Test message"
backup_folder = "code_backups"

# Create a folder to store previous versions of the files
if not os.path.exists(backup_folder):
    os.makedirs(backup_folder)


# Function to get the contents of a file
def get_file_contents(filename):
    with open(filename, 'r') as file:
        return file.readlines()


# Function to save a backup of the current file
def save_file_backup(filename, backup_name):
    with open(filename, 'r') as file:
        content = file.read()
    with open(os.path.join(backup_folder, backup_name), 'w') as backup_file:
        backup_file.write(content)


# Function to calculate file hash (for change detection)
def file_hash(filename):
    hasher = hashlib.md5()
    with open(filename, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()


# Function to compare two files and estimate how much they have changed
def compare_files(file1, file2):
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        content1 = f1.readlines()
        content2 = f2.readlines()

    # Use difflib to get the differences between the files
    diff = difflib.unified_diff(content1, content2, lineterm='')
    diff_lines = list(diff)

    # Calculate percentage of lines changed
    total_lines = max(len(content1), len(content2))
    changed_lines = len([line for line in diff_lines if line.startswith('+') or line.startswith('-')])

    # If total_lines is zero (which is unlikely), we avoid division by zero
    percent_changed = (changed_lines / total_lines * 100) if total_lines > 0 else 0
    return percent_changed, changed_lines


# Function to run the server and measure its startup time
def run_server():
    # Record the start time before launching the server
    start_time = time.time()

    # Start the server process
    server_process = subprocess.Popen(
        ["python3", "server.py", "--ip_port", str(SERVER_PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Allow some time for the server to start
    time.sleep(1)

    # Calculate the time taken to start the server
    server_start_time = time.time() - start_time
    print(f"Server started in {server_start_time:.4f} seconds.")

    return server_process, server_start_time


# Function to run the client, send a message, and measure the time
def run_client():
    # Record the start time before connecting to the server
    start_time = time.time()

    # Connect to the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER_HOST, SERVER_PORT))

    # Measure the time taken to establish the connection
    connection_time = time.time() - start_time
    print(f"Client connected to server in {connection_time:.4f} seconds.")

    # Function to listen for responses from the server
    def listen_for_messages():
        while True:
            try:
                message = s.recv(1024).decode()
                if message:
                    print(f"Received from server: {message}")
            except Exception as e:
                print(f"[!] Error receiving message: {e}")
                break

    # Start a thread to listen for server messages
    t = Thread(target=listen_for_messages)
    t.daemon = True
    t.start()

    # Send a message to the server and measure the time taken
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    to_send = f"[{date_now}] Client{separator_token}{message}"
    s.send(to_send.encode())
    message_send_time = time.time() - start_time
    print(f"Message sent in {message_send_time:.4f} seconds.")

    # Close the connection after sending
    time.sleep(1)
    s.close()

    return connection_time, message_send_time


# Function to check how much the code has changed
def check_code_changes():
    # Define file paths
    client_file = "client.py"
    server_file = "server.py"
    client_backup = os.path.join(backup_folder, "client_backup.py")
    server_backup = os.path.join(backup_folder, "server_backup.py")

    # Check if backups exist
    if os.path.exists(client_backup) and os.path.exists(server_backup):
        # Compare the client.py and server.py with their previous versions
        client_change_percent, client_changed_lines = compare_files(client_file, client_backup)
        server_change_percent, server_changed_lines = compare_files(server_file, server_backup)

        print(f"\nCode Change Estimation:")
        print(f"client.py: {client_changed_lines} lines changed ({client_change_percent:.2f}% change)")
        print(f"server.py: {server_changed_lines} lines changed ({server_change_percent:.2f}% change)")
    else:
        print("\nNo previous backups found. Skipping change estimation.")

    # Save the current versions as the new backups
    save_file_backup(client_file, "client_backup.py")
    save_file_backup(server_file, "server_backup.py")


if __name__ == "__main__":
    # Check how much the code has changed since the last run
    check_code_changes()

    # Run the server and measure the startup time
    server_process, server_start_time = run_server()

    # Run the client, measure connection and message sending time
    connection_time, message_send_time = run_client()

    # Give some time for the server to handle the message and print output
    time.sleep(2)

    # Terminate the server process
    server_process.terminate()
    print(f"Server process terminated.")

    # Print summary of performance results
    print("\nPerformance Summary:")
    print(f"Server Startup Time: {server_start_time:.4f} seconds")
    print(f"Client Connection Time: {connection_time:.4f} seconds")
    print(f"Message Send Time: {message_send_time:.4f} seconds")