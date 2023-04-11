#!/usr/bin/python3

import socket

class Client:
    #TODO
    def __init__(self, hostname, serv_socket, port):
        self.host = hostname
        self.serv = serv_socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = port
        return 

    #TODO
    def connect_socket(self):  
        self.sock.connect((self.host, self.port))

    def send_msg(self, message):
        self.sock.send(message.encode('utf-8'))
        return self.sock.recv(1024).decode()

    def close_socket(self):
        self.sock.close()
        return

    def authenticate(self, username, password):
        message = username + ":" + password
        response = self.send_msg(message)
        if response.decode('utf-8') == "Authentication successful!":


    def vote(self):
        
