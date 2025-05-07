#!/usr/bin/env python3

import socket
import sys
import os

HOST = 'localhost'
PORT = 50001
BUFSIZE = 1024

def read_frame(sock):
    length_data = sock.recv(4).decode()      # Read 4-byte length
    if not length_data:
        return None
    length = int(length_data)
    data = b''
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk:
            break
        data += chunk
    return data

def send_frame(sock, data):
    length = f"{len(data):04}".encode()
    sock.sendall(length + data)

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <filename>")
    sys.exit(1)

filename = sys.argv[1]

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    send_frame(s, filename.encode())             # Send framed filename

    with open("received_" + os.path.basename(filename), 'wb') as f:
        while True:
            frame = read_frame(s)
            if not frame:
                break
            if frame == b'NOFILE':
                print(f"Server: File '{filename}' not found.")
                os.remove("received_" + os.path.basename(filename))  # Clean up
                break
            elif frame == b'DONE':
                print(f"File '{filename}' received successfully.")
                break
            else:
                f.write(frame)  # Write chunk to file
