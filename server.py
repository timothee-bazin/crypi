#!/usr/bin/python3
import socket
import threading

class User:
    def __init__(self, creds):
        self.creds = creds
        self.logged = False
        self.voted = False
        self.client_socket = None
        self.client_address = None

class Server:
    def __init__(self, host='127.0.0.1',port=12345):
        self.host = host
        self.port = port
        self.users = {}
        self.candidats = []
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
        user = self.client_authentificate(client_socket, client_address)
        if user is None:
            return
        user.client_socket = client_socket
        user.client_address = client_address

        while True:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                print(f"Client {client_address} disconnected")
                client_socket.close()
                break

            print(f"Received data from {client_address}: {data}")
            if data.startswith("CONTEXTE"):
                pass
            elif data.startswith("VOTE"):
                pass
            elif data.startswith("CONFIRM"):
                pass


    def client_authentificate(self, client_socket, client_address):
        data = client_socket.recv(1024).decode('utf-8')
        if data:
            print(f"Received data from {client_address}: {data}")

        if not data.startswith("LOGIN"):
            client_socket.send("LOGIN {creds} is expected".encode('utf-8'))
            return None

        creds = data.split("LOGIN ")[-1]
        if self.authenticate(creds):
            client_socket.send("Authentication successful!".encode('utf-8'))
            return self.users[creds]
        else:
            client_socket.send("Authentication failed!".encode('utf-8'))
            return None

    def client_contexte(self, user, data):
        creds = data.split("CONTEXTE ")[-1]
        if self.authenticate(creds):
            client_socket.send("Authentication successful!".encode('utf-8'))
            return self.users[creds]
        else:
            client_socket.send("Authentication failed!".encode('utf-8'))
            return None

    def authenticate(self, creds):
        return creds in self.users and not self.users[creds].logged


def read_file_lines_to_list(filename):
    with open(filename, "r") as file:
        lines = file.readlines()
        res = [line.strip() for line in lines]
    return res


if __name__ == '__main__':
    server = Server()
    for creds in read_file_lines_to_list("credentials.txt"):
        server.users[creds] = User(creds)
    server.candidates = read_file_lines_to_list("candidats.txt")
    server.start()
