import socket
import threading
import os

# Server config
HOST = '127.0.0.1'
PORT = 5000
BUFFER_SIZE = 1024

clients = {}  # {conn: username}


def broadcast(message, sender_conn=None):
    """Send message to all clients except sender"""
    for conn in clients:
        if conn != sender_conn:
            try:
                conn.send(message.encode())
            except:
                conn.close()
                remove_client(conn)


def handle_client(conn, addr):
    username = conn.recv(BUFFER_SIZE).decode()
    clients[conn] = username
    print(f"[NEW CONNECTION] {username} connected from {addr}")
    broadcast(f"{username} has joined the chat.")

    while True:
        try:
            msg = conn.recv(BUFFER_SIZE).decode()
            if not msg:
                break

            # File transfer request
            if msg.startswith("/sendfile"):
                _, filename = msg.split(" ", 1)
                handle_file_transfer(conn, filename)
            else:
                print(f"{username}: {msg}")
                broadcast(f"{username}: {msg}", conn)

        except:
            break

    conn.close()
    remove_client(conn)
    broadcast(f"{username} has left the chat.")


def handle_file_transfer(conn, filename):
    """Receive file from one client and forward to all others"""
    filesize = int(conn.recv(BUFFER_SIZE).decode())
    print(f"[FILE] Receiving {filename} ({filesize} bytes)")

    with open(filename, "wb") as f:
        bytes_read = 0
        while bytes_read < filesize:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            f.write(data)
            bytes_read += len(data)

    print(f"[FILE] {filename} received. Forwarding to clients...")

    # Forward file to all other clients
    for client_conn in clients:
        if client_conn != conn:
            try:
                client_conn.send(f"/file {filename} {filesize}".encode())
                with open(filename, "rb") as f:
                    while True:
                        bytes_data = f.read(BUFFER_SIZE)
                        if not bytes_data:
                            break
                        client_conn.send(bytes_data)
            except:
                pass

    os.remove(filename)  # clean up temp file


def remove_client(conn):
    if conn in clients:
        print(f"[DISCONNECT] {clients[conn]} disconnected.")
        del clients[conn]


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[STARTED] Server running on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


if __name__ == "__main__":
    start_server()
