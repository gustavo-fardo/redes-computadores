import socket
from utils import decode_msg, encode_msg, PAYLOAD_SIZE, MSG_SIZE
import os

IP = "127.0.0.1"
PORT = 65432

# socket.AF_INET -> IPv4
# socket.SOCK_DGRAM -> UDP
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    print("\n== INICIADO SERVIDOR ======================================")
    print("- IP: ", IP)
    print("- PORTA: ", PORT)
    s.bind((IP, PORT)) # IPv4 espera tupla (IP, PORT)

    file_data = ""

    while True:
        req, addr = s.recvfrom(MSG_SIZE) # bloqueia até receber dados        
        print("\n== RECEBIDA REQUISIÇÃO, PROCESSANDO =======================")
        type, id, length, checksum, data = decode_msg(req)

        if type == "GET":
            file_name = data.decode()

            if os.path.exists(file_name):
                # try:
                with open(file_name, "r") as f:
                    file_data = f.read().encode()

                    n_segm = len(file_data)//PAYLOAD_SIZE
                    if len(file_data)%PAYLOAD_SIZE > 0:
                        n_segm += 1    
                    payload = str(n_segm).encode()
                    msg = encode_msg("INFO", payload)
                    s.sendto(msg, addr)
                    
                    id_segm = 1
                    for i, ch in enumerate(file_data, start=1):
                        if i % PAYLOAD_SIZE == 0:
                            if not(i % 5*PAYLOAD_SIZE == 0):
                                payload = file_data[i-PAYLOAD_SIZE:i]
                                
                                msg = encode_msg("DATA", payload, id_segm)
                                s.sendto(msg, addr)
                            id_segm += 1

                    if i%PAYLOAD_SIZE < PAYLOAD_SIZE:
                        payload = file_data
                        msg = encode_msg("DATA", payload, id_segm)
                        s.sendto(msg, addr)
                        id_segm += 1

                    msg = encode_msg("END", "".encode())
                    s.sendto(msg, addr)
                # except Exception as e:
                    # msg = encode_msg("ERR", "".encode())
                    # s.sendto(msg, addr)
            else:
                msg = encode_msg("ERR", "".encode())
                s.sendto(msg, addr)
        
        if type == "RET":
            index = id*PAYLOAD_SIZE
            payload = file_data[index-PAYLOAD_SIZE:index]
            msg = encode_msg("DATA", payload, id)
            s.sendto(msg, addr)