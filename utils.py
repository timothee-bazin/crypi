# /usr/sbin/python3
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
