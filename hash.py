import os
import hashlib

def generate_hashed_credentials(input_file, output_file):
    with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
        for line in f_in:
            user, password = line.strip().split(':')
            salt = os.urandom(32)
            hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100)
            f_out.write(f"{user}:{hash.hex()}:{salt.hex()}\n")

generate_hashed_credentials('credentials.txt', 'hashed_credentials.txt')