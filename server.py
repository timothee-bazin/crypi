#!/usr/bin/python3

import socket
import threading
import rsa
import secrets
import json

from connexion import Connexion
from utils import bytes_startswith, bytes_split, read_file_lines_to_list
from Crypto.Cipher import AES
import tenseal


class User:
    def __init__(self, creds = True):
        # Check usage of the variables (certaines sont jamais utilisé pour le moment mais sont utiles normalement)
        self.creds = None
        self.logged = False

        self.voted = False
        self.connexion = None

class Server:
    def __init__(self, host='127.0.0.1',port=12346):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.voters = {}
        for creds in read_file_lines_to_list("credentials.txt"):
            self.voters[creds] = User(creds)

        self.candidats = read_file_lines_to_list("candidats.txt")

        # Generate TenSEAL context
        self.context_params = {
            "poly_modulus_degree" : 8192,
            "coeff_mod_bit_sizes" : [60, 40, 40, 60],
            "global_scale" : 2**40
        }
        self.context = tenseal.context(tenseal.SCHEME_TYPE.CKKS,
                poly_modulus_degree=self.context_params["poly_modulus_degree"],
                coeff_mod_bit_sizes=self.context_params["coeff_mod_bit_sizes"]
                )
        self.context.global_scale = self.context_params["global_scale"]
        self.context.generate_galois_keys()
        self.context_secret_key = self.context.secret_key()

        self.encrypted_sum = None

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

        self.compute_result()


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
            self.voters[creds].creds = creds
            self.voters[creds].logged = True
            self.voters[creds].connexion = connexion
            return True
        else:
            connexion.send("Authentication failed!")
            return False

    def authenticate(self, creds):
        # TODO check authentification process
        return creds in self.voters #and not self.voters[creds].logged

    def client_context(self, connexion):
        data = connexion.recv_safe(1024)
        if not data or not data.startswith("CONTEXT"):
            connexion.send_safe("CONTEXT is expected")
            return False

        data = self.context.serialize()
        data += b"===END==="
        offset = 0
        block_size = 65536
        while offset < len(data):
            connexion.send(data[offset:offset+block_size], auto_upgrade = False, verbose = False)
            offset += block_size
        return True

    def client_candidats(self, connexion):
        data = connexion.recv_safe(1024)
        if not data or not data.startswith("CANDIDATS"):
            connexion.send_safe("CANDIDATS is expected")
            return False

        connexion.send_safe(",".join(self.candidats))
        return True

    def client_vote(self, connexion):
        data = connexion.recv(4096, auto_decode = False, auto_upgrade = False, verbose = False)
        if not data or not bytes_startswith(data, "VOTE "):
            connexion.send_safe("VOTE {data1,data2} is expected")
            return False

        print("Receiving Vote...")

        delimiter = b"===END==="
        buffer = bytes_split(data, "VOTE ")
        while delimiter not in buffer:
            data = connexion.recv(4096, auto_decode = False, auto_upgrade = False, verbose = False)
            if not data:
                # connexion fermée
                break
            buffer += data

        # enlever le délimiteur à la fin
        vote_bytes = buffer[:-len(delimiter)]
        vote = tenseal.ckks_vector_from(self.context, vote_bytes)
        print("done !")

        if self.encrypted_sum is None:
            self.encrypted_sum = vote
        else:
            self.encrypted_sum += vote

        connexion.send_safe("Vote success!")
        return True


    def compute_result(self):
        if self.encrypted_sum is None:
            print("No vote computed")
            return
        decrypted_tallies = self.encrypted_sum.decrypt(self.context_secret_key)
        decrypted_tallies = [round(x) for x in decrypted_tallies] # arrondi
        print("Résultat des comptes :", decrypted_tallies)
        max_tally = max(decrypted_tallies)
        winners = [self.candidats[i] for i in range(len(self.candidats)) if decrypted_tallies[i] == max_tally]
        print("Nombre de votes :", sum(decrypted_tallies))
        if len(winners) == 1:
            print("Gagnant :", winners[0])
        else:
            print("Il y a une égalité entre les gagnants :", winners)

if __name__ == '__main__':
    server = Server()
    server.start()
