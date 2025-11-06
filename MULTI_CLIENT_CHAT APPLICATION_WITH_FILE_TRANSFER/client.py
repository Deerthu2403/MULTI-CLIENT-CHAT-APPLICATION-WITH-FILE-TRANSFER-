import socket
import threading
import os

# Server config
HOST = '127.0.0.1'
PORT = 5000
BUFFER_SIZE = 1024


def receive_messages(client):
    while True:
        try:
            msg = client.recv(BUFFER_SIZE).decode()
            if not msg:
                break

            if msg.startswith("/file"):
                _, filename, filesize = msg.split(" ", 2)
                filesize = int(filesize)
                print(f"[FILE INCOMING] {filename} ({filesize} bytes)")

                with open("received_" + filename, "wb") as f:
                    bytes_read = 0
                    while bytes_read < filesize:
                        data = client.recv(BUFFER_SIZE)
                        if not data:
                            break
                        f.write(data)
                        bytes_read += len(data)

                print(f"[FILE SAVED] received_{filename}")

            else:
                print(msg)

        except:
            break


def send_messages(client, username):
    while True:
        msg = input()
        if msg.startswith("/sendfile"):
            _, filepath = msg.split(" ", 1)
            if not os.path.exists(filepath):
                print("[ERROR] File not found.")
                continue

            filename = os.path.basename(filepath)
            filesize = os.path.getsize(filepath)

            # notify server
            client.send(f"/sendfile {filename}".encode())
            client.send(str(filesize).encode())

            with open(filepath, "rb") as f:
                while True:
                    bytes_data = f.read(BUFFER_SIZE)
                    if not bytes_data:
                        break
                    client.send(bytes_data)

            print(f"[FILE SENT] {filename}")
        else:
            client.send(msg.encode())


def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    username = input("Enter your username: ")
    client.send(username.encode())

    thread_recv = threading.Thread(target=receive_messages, args=(client,))
    thread_recv.start()

    thread_send = threading.Thread(target=send_messages, args=(client, username))
    thread_send.start()


if __name__ == "__main__":
    start_client()
