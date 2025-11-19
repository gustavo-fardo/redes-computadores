import zlib

MSG_SIZE = 1024
TYPE_SIZE = 2
ID_SIZE = 2
LEN_SIZE = 4
CHKSUM_SIZE = 4
HEADER_SIZE = TYPE_SIZE + ID_SIZE + LEN_SIZE + CHKSUM_SIZE
PAYLOAD_SIZE = MSG_SIZE - HEADER_SIZE

def decode_msg(msg):
    type_dict = {1: "GET", 2: "DATA", 3: "INFO", 4: "END", 5: "ERR", 6: "RET"}
    type = int.from_bytes(msg[0:2], 'big')
    id = int.from_bytes(msg[2:4], 'big')
    length = int.from_bytes(msg[4:8], 'big')
    checksum = int.from_bytes(msg[8:12], 'big')
    data = msg[12:12+length]

    print("")
    print("Tipo:", type_dict[type])
    print("Id Segm: ", id)
    print("Tamanho: ", length)
    print("Checksum: ", checksum)
    print("Dados: ", data.decode())

    return type_dict[type], id, length, checksum, data

def encode_msg(type : str, data : bytes, id = 0) -> bytes:
    if type == "GET":
        type_b = 1
        id = 0
    elif type == "DATA":
        type_b = 2
    elif type == "INFO":
        type_b = 3
        id = 0
    elif type == "END":
        type_b = 4
        id = 0
        data = "".encode()
    elif type == "ERR":
        type_b = 5
        id = 0
    elif type == "RET":
        type_b = 6
    length = len(data)
    data_b = data
    checksum = calc_chksum(data_b)

    type_b = type_b.to_bytes(TYPE_SIZE, 'big')
    id_b = id.to_bytes(ID_SIZE, 'big')
    length_b = length.to_bytes(LEN_SIZE, 'big')
    checksum_b = checksum.to_bytes(CHKSUM_SIZE, 'big')

    msg = type_b + id_b + length_b + checksum_b + data_b

    return msg

def calc_chksum(msg : bytes) -> int:
    return zlib.crc32(msg) & 0xffffffff