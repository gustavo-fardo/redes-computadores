import socket
import threading
from utils import encode_msg, decode_msg, calc_sha, PAYLOAD_SIZE, MSG_SIZE
import os

IP = "127.0.0.1"
PORT = 65432

clients = []

def client_thread(conn, addr):
    global clients
    with conn:
        print(f"\n[{addr}] => Conexão estabelecida")
        while True:
            data = conn.recv(MSG_SIZE)
            if not data:
                break
            type, status, length, hash_sha, payload = decode_msg(data)
            if type == "END":
                print(f"\n[{addr}] => Conexão fechada pelo cliente")
                clients.remove(conn)
                break
            elif type == "MSG":
                print(f"\n[{addr}] => Mensagem recebida: {payload.decode()}")
            elif type == "GET":
                file_name = payload
                print(f"\n[{addr}] => Arquivo requisitado: {file_name.decode()}")
                if os.path.exists(file_name):
                    try:
                        with open(file_name, "rb") as f:
                            file_data = f.read()
                            file_size = len(file_data)
                            file_hash = calc_sha(file_name)

                            # Calcular número de segmentos necessários
                            n_segm = file_size//PAYLOAD_SIZE
                            if file_size%PAYLOAD_SIZE > 0:
                                n_segm += 1    
                            
                            # Gera segmentos de tamanho máximo do arquivo e envia
                            for i, ch in enumerate(file_data, start=1):
                                if i % PAYLOAD_SIZE == 0:
                                    payload = file_data[i-PAYLOAD_SIZE:i]
                                    msg = encode_msg("DATA", payload, file_hash, file_size)
                                    conn.sendall(msg)

                            # Envia último segmento se houver dados restantes
                            if i%PAYLOAD_SIZE < PAYLOAD_SIZE:
                                payload = file_data[i - (i%PAYLOAD_SIZE):i]
                                msg = encode_msg("DATA", payload, file_hash, file_size)
                                conn.sendall(msg)

                            print(f"\n[{addr}] => Fim da transmissao")
                    except Exception as e:
                        msg = encode_msg("DATA", str(e).encode(), status=2)
                        print(f"\n[{addr}] => Erro ao enviar arquivo: {e}")
                        conn.sendall(msg)
                else:
                    # Não encontrou o arquivo
                    msg = encode_msg("DATA", "".encode(), status=1)
                    print(f"\n[{addr}] => Arquivo não encontrado: {file_name.decode()}")
                    conn.sendall(msg)

def send_chat_messages():
    global clients
    while True:
        if len(clients) > 0:
            message = input("\n=> Digite uma mensagem para enviar ao cliente: ")
            msg = encode_msg("MSG", message.encode())
            for conn in clients:
                conn.sendall(msg)

# socket.AF_INET -> IPv4
# socket.SOCK_STREAM -> TCP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((IP, PORT))
    print("\n== SERVIDOR INICIADO, AGUARDANDO CONEXÕES ===================")
    t_chat = threading.Thread(target=send_chat_messages)
    t_chat.start()
    while True:
        s.listen()
        conn, addr = s.accept()
        clients.append(conn)
        t = threading.Thread(target=client_thread, args=(conn, addr,))
        t.start()

