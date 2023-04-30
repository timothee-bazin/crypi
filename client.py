#!/usr/bin/python3

import socket
import rsa
import pickle

from connexion import Connexion
from phe import paillier
from Crypto.Cipher import AES

class Client:
    def __init__(self, host='127.0.0.1',port=12346):
        self.host = host
        self.port = port

        # Fernet
        self.context = None

       # Générer une paire de clés RSA
        self.server_pubkey = None

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connexion = Connexion(client_socket, self.host)

        # Outils pour le vote
        self.candidats = []

    def connect_socket(self):
        self.connexion.client_socket.connect((self.host, self.port))
        print(f"Connected to server {self.host}:{self.port}")

    def close_socket(self):
        self.client_socket.close()
        print("Disconnected from server")

    def server_init(self):
        (pubkey, privkey) = rsa.newkeys(512)
        pubkey_bytes = pubkey.save_pkcs1(format="PEM")
        self.connexion.send(b"INIT " + pubkey_bytes)

        server_sym_key_crypted = self.connexion.recv(4096, auto_decode = False)
        server_sym_key = rsa.decrypt(server_sym_key_crypted, privkey) 

        self.connexion.cipher = AES.new(server_sym_key, AES.MODE_ECB)


    def server_authenticate(self, username, password):
        message = username + ":" + password
        self.connexion.send_safe("LOGIN " + message)
        response = self.connexion.recv_safe(1024)
        if response == "Authentication successful!":
            return True
        elif response == "Authentication failed!":
            return False
        else:
            raise(Exception.args)


    def server_context(self):
        self.connexion.send_safe("CONTEXT")
        paillier_pubkey = self.connexion.recv_safe(4096, auto_decode = False)
        self.context = paillier.PaillierPublicKey(n=int(paillier_pubkey))

    def server_candidats(self):
        self.connexion.send_safe("CANDIDATS")
        self.candidats = self.connexion.recv_safe(1024).split(',')

    def server_vote(self, index):
        vote = self.context.encrypt(index)
        votestr = str(vote.ciphertext()) + "," + str(vote.exponent)
        self.connexion.send_safe("VOTE " + votestr)
        confirm = self.connexion.recv_safe(1024)



if __name__ == '__main__':
    client = Client()

    # Connect to the server
    client.connect_socket()

    # Authenticate using example credentials
    client.server_init()

    is_authenticated = client.server_authenticate("user1", "password1")
    print(f"Authentication result: {is_authenticated}")

    client.server_context()
    client.server_candidats()
    client.server_vote(1)

    # Disconnect from the server
    #client.close_socket()
