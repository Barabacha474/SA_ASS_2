import socket
import threading
from threading import Thread
import argparse
# server's IP address
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 10000
separator_token = "<SEP>"
client_sockets = set()

parser = argparse.ArgumentParser()
parser.add_argument("-ipp", "--ip_port", required=True)
args = parser.parse_args()
print(f'Hi {args.ip_port}, Welcome', flush=True)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.bind((SERVER_HOST, SERVER_PORT))

s.listen(100)
print("[*] Server started", flush = True)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

lock = threading.Lock()

flag = True
lst = []
start_of_lst = "Previous messages\n"
end_of_lst = "End of previous messages\n"

def listen_for_client(cs):
    """
    This function keep listening for a message from `cs` socket
    Whenever a message is received, broadcast it to all other connected clients
    """
    with lock:
        cs.send(start_of_lst.encode())
        for item in lst:
            cs.send(item.encode())
        cs.send(end_of_lst.encode())

    while True:
        try:
            msg = cs.recv(1024).decode()
        except Exception as e:
            print(f"[!] Error: {e}")
            client_sockets.remove(cs)
        else:
            msg = msg.replace(separator_token, ":")
            with lock:
                lst.append(msg + "\n")
            print(f"[*] Received: {msg}")
            msg_end = msg[29:]
            print(f"[*] msg_end: {msg_end}")
            if (msg_end == "GET number of messages"):
                msg += f"\nTotal number of messages in chat: {len(lst)}"
        for client_socket in client_sockets:
            client_socket.send(msg.encode())

print("Trying")
try:
    while flag:
        print("Waiting for client")
        client_socket, client_address = s.accept()
        print(f"[+] {client_address} connected.", flush = True)
        client_sockets.add(client_socket)
        t = Thread(target=listen_for_client, args=(client_socket,), daemon=True)
        t.start()
except KeyboardInterrupt:
    print(f"[!] Keyboard Interrupt")

for cs in client_sockets:
    cs.close()
s.close()

