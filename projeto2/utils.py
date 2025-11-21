import hashlib

MSG_SIZE = 1024
TYPE_SIZE = 2
STATUS_SIZE = 2
LEN_SIZE = 4
HASH_SIZE = 32
HEADER_SIZE = TYPE_SIZE + STATUS_SIZE + LEN_SIZE + HASH_SIZE
PAYLOAD_SIZE = MSG_SIZE - HEADER_SIZE

SHOW_HEADER = False

def decode_msg(msg):
    type_dict = {1: "GET", 2: "DATA", 3: "MSG", 4: "END"}
    status = {0: "OK", 1: "ERRO_ARQUIVO_NAO_ENCONTRADO", 2: "ERRO_OUTRO"}
    type = int.from_bytes(msg[0:2], 'big')
    status = status[int.from_bytes(msg[2:4], 'big')]
    length = int.from_bytes(msg[4:8], 'big')
    hash_sha = msg[8:40]
    data = msg[HEADER_SIZE:HEADER_SIZE+PAYLOAD_SIZE]

    if SHOW_HEADER:
        print("")
        print("Tipo:", type_dict[type])
        print("Status:", status)
        print("Tamanho: ", length)
        print("hash_sha: ", hash_sha)
        print("Dados: ", data.decode())

    return type_dict[type], status, length, hash_sha, data

def encode_msg(type : str, data : bytes, hash_sha = b'0', length = 1, status = 0) -> bytes:
    if type == "GET":
        type_b = 1
    elif type == "DATA":
        type_b = 2
    elif type == "MSG":
        type_b = 3
    elif type == "END":
        type_b = 4
        data = "".encode()
    data_b = data

    type_b = type_b.to_bytes(TYPE_SIZE, 'big')
    status_b = status.to_bytes(STATUS_SIZE, 'big')
    length_b = length.to_bytes(LEN_SIZE, 'big')

    hash_sha = hash_sha.ljust(HASH_SIZE, b'\0')[:HASH_SIZE]

    msg = type_b + status_b + length_b + hash_sha + data_b 

    return msg

def calc_sha(file_path : str) -> bytes:
    hash_func = hashlib.sha256()
    with open(file_path, 'rb') as file:
        while chunk := file.read(MSG_SIZE):
            hash_func.update(chunk)
    return hash_func.digest()