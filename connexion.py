#!/usr/bin/python3
import socket
import threading
import rsa

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class Connexion:
    def __init__(self, client_socket, client_address):
        self.up = True
        self.client_socket = client_socket
        self.client_address = client_address

        self.cipher = None

    def close(self):
        print(f"{self.client_address} disconnected")
        self.up = False
        self.client_socket.close()

    def send(self, message, auto_upgrade = True, verbose = True):
        if self.cipher and auto_upgrade:
            print("[!] Upgrade security send fonction")
            self.send_safe(message)
            return

        if verbose:
            print(f"Sending data to {self.client_address} : {message}")
        if type(message) is str:
            message = message.encode('utf-8')

        if not self.up:
            print("Connexion is closed, not sending.")
            return

        self.client_socket.send(message)

    def send_safe(self, message, verbose = True):
        if self.cipher is None:
            print("[!] Downgrade security send fonction")
            self.send(message)
            return

        if verbose:
            print(f"Sending secured data to {self.client_address} : {message}")
        if type(message) is str:
            message = message.encode('utf-8')

        if not self.up:
            print("Connexion is closed, not sending.")
            return

        padded_message = pad(message, AES.block_size)
        safe_message = self.cipher.encrypt(padded_message)
        self.client_socket.send(safe_message)

    def recv(self, size, auto_decode = True, auto_upgrade = True, verbose = True):
        # Auto upgrade
        if self.cipher and auto_upgrade:
            print("[!] Upgrade security recv fonction")
            return self.recv_safe(size)

        if not self.up:
            return None

        data = self.client_socket.recv(size)
        if auto_decode:
           data = data.decode('utf-8')

        if not data:
            self.close()
            return None

        if verbose:
            print(f"Received data from {self.client_address}: {data}")
        return data

    def recv_safe(self, size, auto_decode = True, verbose = True):
        if self.cipher is None:
            print("[!] Downgrading security recv fonction")
            return self.recv(size)

        if not self.up:
            return None

        encrypted_answer = self.client_socket.recv(size)
        if encrypted_answer:
            padded_data = self.cipher.decrypt(encrypted_answer)
            data = unpad(padded_data, AES.block_size)
        else:
            self.close()
            return None

        if auto_decode:
            data = data.decode('utf-8')


        if verbose:
            print(f"Received secured data from {self.client_address}: {data}")
        return data
