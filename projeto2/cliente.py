import socket
import random
import threading
import time
import os
from utils import encode_msg, decode_msg, calc_sha, MSG_SIZE

def msg_formato_invalido():
    print("=> Formato inválido de requisição")

result_file = f"resultados/resultado_{time.strftime('%Y%m%d_%H%M%S')}.txt"
os.makedirs("resultados", exist_ok=True)

user_input = input("> Digite o endereço e a porta do servidor no formato <IP_Servidor:Porta_Servidor>:")
try:
    server_info = user_input.split(":")
    ip_server = server_info[0]
    port_server = int(server_info[1])
except:
    msg_formato_invalido()
    exit()

# socket.AF_INET -> IPv4
# socket.SOCK_STREAM -> TCP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((ip_server, port_server))
    print("\n== CONECTANDO COM SERVIDOR ===============================")
    print("- IP: ", ip_server)
    print("- PORTA: ", port_server)

    def send_message():
        while True:
            req_input = input("\n== REALIZE UMA DAS REQUISIÇÕES A SEGUIR ==================\n1) sair\n""2) arquivo|nome_arquivo.ext\n3) chat|mensagem\n")
            try:
                split = req_input.split("|")
                if len(split) < 2:
                    if split[0] == "sair":
                        print("=> Encerrando conexão com o servidor")
                        s.send(encode_msg("END", "Encerrar conexão".encode()))
                        exit()
                    else:
                        msg_formato_invalido()
                else:
                    req_type = split[0]
                    content = split[1]
                    if req_type == "arquivo":
                        s.send(encode_msg("GET", content.encode()))
                    elif req_type == "chat":
                        s.send(encode_msg("MSG", content.encode()))
                    else:
                        msg_formato_invalido()
            except:
                msg_formato_invalido()
                exit()

    def recieve_message():
        global result_file
        current_length = 0

        while True:
            data = s.recv(MSG_SIZE)
            if not data:
                print("=> Finalizando Conexão")
                exit()
            type, status, length, hash_sha, payload = decode_msg(data)
            if type == "DATA":
                if status == "OK":
                    current_length += len(payload)
                    if current_length < length:
                        with open(result_file, "ab") as f:
                            f.write(payload)
                    else:
                        with open(result_file, "ab") as f:
                            f.write(payload[current_length - length:])
                        current_length = 0
                        hash_final = calc_sha(result_file)
                        if hash_final != hash_sha:
                            print("=> Arquivo corrompido durante a transferência.")
                        else:
                            print(f"=> Arquivo recebido com sucesso. Salvo em: {result_file}")
                        result_file = f"resultados/resultado_{time.strftime('%Y%m%d_%H%M%S')}.txt"
                        print("=> Verificação de integridade:")
                        print("- Hash esperado: ", hash_sha.hex())
                        print("- Hash recebido: ", hash_final.hex())
                else:
                    print(f"=> Erro ao receber dados: {status} | {payload.decode()}")
            elif type == "MSG":
                print(f"[SERVIDOR] => Mensagem recebida: {payload.decode()}")

    thread_send = threading.Thread(target=send_message, daemon=True)
    thread_recv = threading.Thread(target=recieve_message, daemon=True)

    thread_send.start()
    thread_recv.start() 

    thread_send.join()
    thread_recv.join()
