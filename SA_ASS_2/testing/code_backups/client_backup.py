import argparse
import socket
import random
from threading import Thread
from datetime import datetime
#SERVER_HOST = "localhost"
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 10000
separator_token = "<SEP>"

parser = argparse.ArgumentParser()
parser.add_argument("-ipps", "--ip_port_server", required=True)
args = parser.parse_args()

SERVER_PORT = int(args.ip_port_server)
print(f'Will try to connect to {SERVER_HOST}:{SERVER_PORT}')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")

s.connect((SERVER_HOST, SERVER_PORT))

print("[+] Connected.")

name = "Anonym"

def listen_for_messages():
    while True:
        message = s.recv(1024).decode()
        print(message)

t = Thread(target=listen_for_messages)
t.daemon = True
t.start()

while True:
    to_send =  input()
    if to_send.lower() == 'q':
        break
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    to_send = f"[{date_now}] {name}{separator_token}{to_send}"
    s.send(to_send.encode())
s.close()