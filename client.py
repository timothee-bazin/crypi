#!/usr/bin/python3

import socket

class Client:
    def __init__(self, host='127.0.0.1',port=12345):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def connect_socket(self):  
        self.client_socket.connect((self.host, self.port))
        print(f"Connected to server {self.host}:{self.port}")

    def send_msg(self, message):
        self.client_socket.send(message.encode('utf-8'))
        return self.client_socket.recv(1024).decode()

    def close_socket(self):
        self.client_socket.close()
        print("Disconnected from server")

    def authenticate(self, username, password):
        message = username + ":" + password
        response = self.send_msg(message)
        if response == "Authentication successful!":
            return True
        elif response == "Authentication failed!":
            return False
        else:
            raise(Exception.args)

    def vote(self):
        pass
        
if __name__ == '__main__':
    client = Client()

    # Connect to the server
    client.connect_socket()

    # Authenticate using example credentials
    is_authenticated = client.authenticate("user1", "password1")
    print(f"Authentication result: {is_authenticated}")

    # Disconnect from the server
    client.close_socket()