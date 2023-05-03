#!/usr/bin/python3

import socket
import rsa
import pickle
import json

from connexion import Connexion
from utils import bytes_startswith, bytes_split
from Crypto.Cipher import AES
import tenseal

class Client:
    def __init__(self, host='127.0.0.1',port=12346):
        self.host = host
        self.port = port

        # Tenseal
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

        print("Receiving context...")

        delimiter = b"===END==="
        buffer = b""
        while delimiter not in buffer:
            data = self.connexion.recv(65536, auto_decode = False, auto_upgrade = False, verbose = False)
            if not data:
                # connexion fermée
                break
            buffer += data

        ctx = buffer[:-len(delimiter)]
        self.context =  tenseal.context_from(ctx)
        print("done !")

    def server_candidats(self):
        self.connexion.send_safe("CANDIDATS")
        self.candidats = self.connexion.recv_safe(1024).split(',')

    def server_vote(self, index):
        vote = [0] * len(self.candidats)
        vote[index] = 1
        encrypted_vote = tenseal.CKKSVector(self.context, vote)

        data = b"VOTE " + encrypted_vote.serialize()
        data += b"===END==="
        offset = 0
        block_size = 1024
        while offset < len(data):
            sent_bytes = self.connexion.send(data[offset:offset+block_size], auto_upgrade = False, verbose = False)
            offset += block_size

        confirm = self.connexion.recv_safe(1024)



def simulate_full_process(target_vote):
    print('=========================================')
    client = Client()
    client.connect_socket()
    client.server_init()
    client.server_authenticate("user1", "password1")
    client.server_context()
    client.server_candidats()
    client.server_vote(target_vote)

if __name__ == '__main__':
    simulate_full_process(2)
    #simulate_full_process(2)
    #simulate_full_process(2)
