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
    s.bind((IP, PORT))

    file_data = ""

    while True:
        req, addr = s.recvfrom(MSG_SIZE)       
        print("\n== RECEBIDA REQUISIÇÃO, PROCESSANDO =======================")
        type, id, length, checksum, data = decode_msg(req)

        # Processa requisição de arquivo
        if type == "GET":
            file_name = data.decode()

            if os.path.exists(file_name):
                try:
                    with open(file_name, "r") as f:
                        file_data = f.read().encode()

                        # Calcular número de segmentos necessários
                        n_segm = len(file_data)//PAYLOAD_SIZE
                        if len(file_data)%PAYLOAD_SIZE > 0:
                            n_segm += 1    

                        # Comunica número de segmentos ao cliente
                        payload = str(n_segm).encode()
                        msg = encode_msg("INFO", payload)
                        s.sendto(msg, addr)
                        
                        # Gera segmentos de tamanho máximo do arquivo e envia
                        id_segm = 1
                        for i, ch in enumerate(file_data, start=1):
                            if i % PAYLOAD_SIZE == 0:
                                payload = file_data[i-PAYLOAD_SIZE:i]
                                msg = encode_msg("DATA", payload, id_segm)
                                s.sendto(msg, addr)
                                id_segm += 1

                        # Envia último segmento se houver dados restantes
                        if i%PAYLOAD_SIZE < PAYLOAD_SIZE:
                            payload = file_data[i - (i%PAYLOAD_SIZE):i]
                            msg = encode_msg("DATA", payload, id_segm)
                            s.sendto(msg, addr)
                            id_segm += 1

                        # Comunica fim da transmissão
                        msg = encode_msg("END", "".encode())
                        s.sendto(msg, addr)
                except Exception as e:
                    msg = encode_msg("ERR", str(e).encode())
                    s.sendto(msg, addr)
            else:
                # Não encontrou o arquivo
                msg = encode_msg("ERR", "Arquivo não encontrado".encode())
                s.sendto(msg, addr)
        
        # Retransmite segmento solicitado
        if type == "RET":
            index = id*PAYLOAD_SIZE
            payload = file_data[index-PAYLOAD_SIZE:index]
            msg = encode_msg("DATA", payload, id)
            s.sendto(msg, addr)