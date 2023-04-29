#!/usr/bin/python3

import socket
import threading
import rsa
from connexion import Connexion

from cryptography.fernet import Fernet


class User:
    def __init__(self, creds = True):
        self.creds = None
        self.logged = False
        self.voted = False
        self.connexion = None

class Server:
    def __init__(self, host='127.0.0.1',port=12346):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.users = {}
        for creds in read_file_lines_to_list("credentials.txt"):
            self.users[creds] = User(creds)

        self.candidats = read_file_lines_to_list("candidats.txt")

        # Générer une clé secrète pour le chiffrement symétrique
        self.fernet_key = Fernet.generate_key()
        self.fernet = Fernet(self.fernet_key)

       # Générer une paire de clés RSA
        (self.pubkey, self.privkey) = rsa.newkeys(512)


    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server started on {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Client {client_address} connected")
            threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()


    def handle_client(self, client_socket, client_address):
        connexion = Connexion(client_socket, client_address, self.privkey)

        # share keys
        self.client_init(connexion)

        # Log in
        while not self.client_login(connexion):
            continue

        while True:
            data = connexion.recv_safe(1024)
            if not data:
                print(f"Client {client_address} disconnected")
                client_socket.close()
                break

            if data.startswith("CONTEXTE "):
                pass
            elif data.startswith("VOTE "):
                pass
            elif data.startswith("CONFIRM "):
                pass

    def client_init(self, connexion):
        data = connexion.recv(1024, auto_decode = False)
        # Don't decode the expected key
        if not data[:7].decode('utf-8').startswith("INIT "):
            connexion.send("INIT {rsa_pub_key} is expected")
            return None

        # Manipulate bytes not str
        client_pubkey_bytes = data[len("INIT "):]
        connexion.client_pubkey = rsa.PublicKey.load_pkcs1(client_pubkey_bytes)

        pubkey_bytes = self.pubkey.save_pkcs1()
        # don't upgrade because the client doesn't know our key
        connexion.send(pubkey_bytes, auto_upgrade = False)

    def client_login(self, connexion):
        data = connexion.recv_safe(1024)
        if not data.startswith("LOGIN "):
            connexion.send_safe("LOGIN {creds} is expected")
            return False

        creds = data.split("LOGIN ")[-1]
        if self.authenticate(creds):
            connexion.send_safe("Authentication successful!")
            self.users[creds].creds = creds 
            self.users[creds].logged = True 
            self.users[creds].connexion = connexion 
            return True
        else:
            connexion.send("Authentication failed!")
            return False


    def client_contexte(self, connexion, data):
        creds = data.split("CONTEXTE ")[-1]
        if self.authenticate(creds):
            connexion.send("Authentication successful!")
            return self.connexions[creds]
        else:
            connexion.send("Authentication failed!")
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
    server.start()
