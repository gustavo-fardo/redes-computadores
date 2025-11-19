import socket
import random
import threading
import time
from utils import MSG_SIZE

def msg_formato_invalido():
    print("=> Formato inválido de requisição")

result_file = f"resultados/resultado_{time.strftime('%Y%m%d_%H%M%S')}.txt"

user_input = input("Digite o endereço e a porta do servidor: IP_Servidor:Porta_Servidor\n")
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
                    print(split[0])
                    if split[0] == "sair":
                        # Envia sair para o servidor
                        exit()
                    else:
                        msg_formato_invalido()
                else:
                    req_type = split[0]
                    content = split[1]
                    print(req_type)
                    if req_type == "arquivo":
                        s.sendall(b"Hello, world")
                        print(content)
                        # Pede arquivo para o servidor
                    elif req_type == "chat":
                        print(content)
                        # Envia msg para o servidor
                    else:
                        msg_formato_invalido()
            except:
                msg_formato_invalido()
                exit()

    def recieve_message():
        while True:
            data = s.recv(MSG_SIZE)
            if not data:
                print("=> Finalizando Conexão")
                exit()
            print("recebido")
            print(data)

    thread_send = threading.Thread(target=send_message, daemon=True)
    thread_recv = threading.Thread(target=recieve_message, daemon=True)

    thread_send.start()
    thread_recv.start() 

    thread_send.join()
    thread_recv.join()
