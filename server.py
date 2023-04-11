#!/usr/bin/python3
import socket
import threading

class Server:
    def __init__(self, host='127.0.0.1',port=12345):
        self.host = host
        self.port = port
        self.users = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server started on {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Client {client_address} connected")
            threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()


    def handle_client(self, client_socket, client_address):
        while True:
            data = client_socket.recv(1024).decode('utf-8')
            if data:
                print(f"Received data from {client_address}: {data}")
                if self.authenticate(data):
                    client_socket.send("Authentication successful!".encode('utf-8'))
                else:
                    client_socket.send("Authentication failed!".encode('utf-8'))
            else:
                print(f"Client {client_address} disconnected")
                client_socket.close()
                break


    def authenticate(self, data):
        username, password = data.split(':', 1)
        if username in self.users and self.users[username] == password:
            return True
        else:
            return False


def read_credentials(filename):
    with open(filename, "r") as file:
        lines = file.readlines()
        credentials = [line.strip() for line in lines]
    return credentials

if __name__ == '__main__':
    server = Server()
    server.users = read_credentials("credentials.txt")
    server.start()