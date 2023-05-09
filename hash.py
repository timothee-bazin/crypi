import hashlib

# Open the credentials file for reading and the hashed credentials file for writing
with open('credentials.txt', 'r') as f_in, open('hashed_credentials.txt', 'w') as f_out:
    # Iterate over each line in the credentials file
    for line in f_in:
        # Hash the line using SHA-256 (you can use a different hash algorithm if you prefer)
        hashed_line = hashlib.sha256(line.strip().encode()).hexdigest()
        # Write the hashed line to the output file
        f_out.write(hashed_line + '\n')
