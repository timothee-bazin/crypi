#!/usr/bin/python3
import socket
import threading
import rsa

class Connexion:
    def __init__(self, client_socket, client_address, privkey = None):
        self.client_socket = client_socket
        self.client_address = client_address

        self.privkey = privkey
        self.client_pubkey = None

    def send(self, message, auto_upgrade = True):
        if self.client_pubkey and auto_upgrade:
            print("[!] Upgrade security send fonction")
            self.send_safe(message)
            return

        print(f"Sending data to {self.client_address} : {message}")
        if type(message) is str:
            message = message.encode('utf-8')

        self.client_socket.send(message)

    def send_safe(self, message):
        if self.client_pubkey is None:
            print("[!] Downgrade security send fonction")
            self.send(message)
            return

        print(f"Sending secured data to {self.client_address} : {message}")
        if type(message) is str:
            message = message.encode('utf-8')

        block_size = rsa.common.byte_size(self.client_pubkey.n) - 11  # calculer la taille du bloc de chiffrement

        encrypted_blocks = []
        for i in range(0, len(message), block_size):
            block = message[i:i+block_size]
            encrypted_block = rsa.encrypt(block, self.client_pubkey)
            encrypted_blocks.append(encrypted_block)

        safe_message = b"".join(encrypted_blocks)
        print(safe_message)
        self.client_socket.send(safe_message)

    def recv(self, size, auto_decode = True, auto_upgrade = True):
        # Auto upgrade
        if self.client_pubkey and auto_upgrade:
            print("[!] Upgrade security recv fonction")
            return self.recv_safe(size)

        data = self.client_socket.recv(size)
        if auto_decode:
           data = data.decode('utf-8')

        if data:
            print(f"Received data from {self.client_address}: {data}")
        return data

    def recv_safe(self, size, auto_decode = True):
        if self.client_pubkey is None:
            print("[!] Downgrading security recv fonction")
            return self.recv(size)

        encrypted_answer = self.client_socket.recv(size)
        print(b"encrypted : " + encrypted_answer)

        data = rsa.decrypt(encrypted_answer, self.privkey)
        if auto_decode:
            data = data.decode('utf-8')

        if data:
            print(f"Received secured data from {self.client_address}: {data}")
        return data
