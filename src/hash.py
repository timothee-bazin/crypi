import os
import hashlib

def generate_hashed_credentials(input_creds):
    user, password = input_creds.strip().split(':')
    salt = os.urandom(32)
    hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100)
    print(f"{user}:{hash.hex()}:{salt.hex()}\n")

generate_hashed_credentials(input("Enter username:password\n"))