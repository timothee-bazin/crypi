#!/usr/bin/python3

import socket
import threading
import rsa
import secrets

from connexion import Connexion
from phe import paillier
from Crypto.Cipher import AES


class User:
    def __init__(self, creds = True):
        self.creds = None
        self.logged = False

        self.voted = False
        self.vote = None

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

        # Générer une clé secrète pour paillier
        self.pubkey, self.privkey = paillier.generate_paillier_keypair()

        self.encrypted_sum = self.pubkey.encrypt(0)

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server started on {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Client {client_address} connected")
            threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()



    def handle_client(self, client_socket, client_address):
        connexion = Connexion(client_socket, client_address)

        func_steps = [
                self.client_init,
                self.client_login,
                self.client_context,
                self.client_candidats,
                self.client_vote
                ]

        for func_step in func_steps:
            while connexion.up and not func_step(connexion):
                continue

        print(f"Ending process with {client_address}")
        connexion.close()


    def client_init(self, connexion):
        data = connexion.recv(1024, auto_decode = False)

        # Don't decode the expected key
        if not bytes_startswith(data, "INIT "):
            connexion.send("INIT {rsa_pub_key} is expected")
            return False

        # Manipulate bytes not str
        client_pubkey_bytes = bytes_split(data, "INIT ")
        client_pubkey = rsa.PublicKey.load_pkcs1(client_pubkey_bytes)

        # Générer une clé symétrique de 256 bits
        sym_key = secrets.token_bytes(32)

        connexion.cipher = AES.new(sym_key, AES.MODE_ECB)

        # don't upgrade because the client doesn't know our key
        safe_message = rsa.encrypt(sym_key, client_pubkey)

        connexion.send(safe_message, auto_upgrade = False)
        return True

    def client_login(self, connexion):
        data = connexion.recv_safe(1024)
        if not data or not data.startswith("LOGIN "):
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

    def authenticate(self, creds):
        return creds in self.users #and not self.users[creds].logged

    def client_context(self, connexion):
        data = connexion.recv_safe(1024)
        if not data or not data.startswith("CONTEXT"):
            connexion.send_safe("CONTEXT is expected")
            return False

        connexion.send_safe(str(self.pubkey.n))
        return True

    def client_candidats(self, connexion):
        data = connexion.recv_safe(1024)
        if not data or not data.startswith("CANDIDATS"):
            connexion.send_safe("CANDIDATS is expected")
            return False

        connexion.send_safe(",".join(self.candidats))
        return True

    def client_vote(self, connexion):
        data = connexion.recv_safe(4096)
        if not data or not data.startswith("VOTE "):
            connexion.send_safe("VOTE {data1,data2} is expected")
            return False

        vote_str = bytes_split(data, "VOTE ")
        vote_data = vote_str.split(',')
        if len(vote_data) != 2:
            connexion.send_safe("Vote failed!")
            return False
        vote = paillier.EncryptedNumber(self.pubkey, int(vote_data[0]), int(vote_data[1]))
        self.encrypted_sum += vote
        connexion.send_safe("Vote success!")
        return True





def read_file_lines_to_list(filename):
    with open(filename, "r") as file:
        lines = file.readlines()
        res = [line.strip() for line in lines]
    return res

def bytes_startswith(bytes_str, prefix):
    try:
        return bytes_str[:len(prefix)].decode('utf-8').startswith(prefix)
    except UnicodeDecodeError:
        return False

def bytes_split(bytes_str, prefix):
    return bytes_str[len(prefix):]

if __name__ == '__main__':
    server = Server()
    server.start()
