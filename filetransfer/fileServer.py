#!/usr/bin/env python3

import socket
import os
import sys

HOST = 'localhost'
PORT = 50001
BUFSIZE = 1024

def read_frame(sock):
    length_data = sock.recv(4).decode()         # Read the first 4 bytes for the length
    if not length_data:
        return None
    length = int(length_data)                   # Convert string to int
    data = b''
    while len(data) < length:                   # Keep receiving until we get the whole frame
        chunk = sock.recv(length - len(data))
        if not chunk:
            break
        data += chunk
    return data

def send_frame(sock, data):
    length = f"{len(data):04}".encode()         # Format the length as 4-byte zero-padded string
    sock.sendall(length + data)                 # Send length and data together

def handle_client(conn, addr):                  # This function is called by each child process
    print(f"[Child {os.getpid()}] Connected by {addr}")
    filename = read_frame(conn).decode().strip()
    print(f"[Child {os.getpid()}] Client requested: {filename}")

    if not os.path.exists(filename):
        send_frame(conn, b'NOFILE')
        print(f"[Child {os.getpid()}] File not found.")
    else:
        with open(filename, 'rb') as f:
            while True:
                chunk = f.read(BUFSIZE)
                if not chunk:
                    break
                send_frame(conn, chunk)
        send_frame(conn, b'DONE')
        print(f"[Child {os.getpid()}] Sent file '{filename}' successfully.")

    conn.close()                                # Close client connection
    sys.exit(0)                                 # Child process exits

# Main server code
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((HOST, PORT))
    server_sock.listen(5)
    print(f"[Server] Listening on {HOST}:{PORT}")

    while True:                                 # Server runs forever
        conn, addr = server_sock.accept()       # Accept a client
        pid = os.fork()                         # Create a new process to handle client
        if pid == 0:                            # In child process
            server_sock.close()                 # Child doesn't need the main server socket
            handle_client(conn, addr)           # Handle client, then exit
        else:
            conn.close()                        # Parent closes the client socket 