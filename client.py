#!/usr/bin/python3

import socket
import rsa
from connexion import Connexion

class Client:
    def __init__(self, host='127.0.0.1',port=12346):
        self.host = host
        self.port = port

       # Générer une paire de clés RSA
        (self.pubkey, self.privkey) = rsa.newkeys(512)
        self.server_pubkey = None

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connexion = Connexion(client_socket, self.host, self.privkey)


    def connect_socket(self):
        self.connexion.client_socket.connect((self.host, self.port))
        print(f"Connected to server {self.host}:{self.port}")

    def close_socket(self):
        self.client_socket.close()
        print("Disconnected from server")

    def share_rsa_key(self):
        pubkey_bytes = self.pubkey.save_pkcs1(format="PEM")
        self.connexion.send(b"INIT " + pubkey_bytes)

        server_pubkey_bytes = self.connexion.recv(1024, auto_decode = False)
        self.connexion.client_pubkey = rsa.PublicKey.load_pkcs1(server_pubkey_bytes)

    def authenticate(self, username, password):
        message = username + ":" + password
        response = self.connexion.send("LOGIN " + message)
        if response == "Authentication successful!":
            return True
        elif response == "Authentication failed!":
            return False
        else:
            raise(Exception.args)



if __name__ == '__main__':
    client = Client()

    # Connect to the server
    client.connect_socket()


    # Authenticate using example credentials
    pubkey = client.share_rsa_key()
    print(pubkey)

    is_authenticated = client.authenticate("user1", "password1")
    print(f"Authentication result: {is_authenticated}")

    message = "hello world!"
    response = client.send_safe(message)

    # Disconnect from the server
    #client.close_socket()
