import socket
from utils import decode_msg, encode_msg, calc_chksum, MSG_SIZE, PAYLOAD_SIZE
import random
import time

IP = "127.0.0.1"
PORT = 65432
result_file = f"resultados/resultado_{time.strftime('%Y%m%d_%H%M%S')}.txt"

user_input = input("Digite sua requisição em formato: @IP_Servidor:Porta_Servidor/nome_do_arquivo.ext\n")
try:
    user_input = user_input.split("/")
    file_name = user_input[1]
    server_info = user_input[0].split(":")
    ip_server = server_info[0][1:]
    port_server = int(server_info[1])
except:
    print("=> Formato inválido de requisição")
    exit()

# socket.AF_INET -> IPv4
# socket.SOCK_DGRAM -> UDP
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    addr = (ip_server, port_server)
    s.settimeout(10.0)
    print("\n== CONECTANDO COM SERVIDOR ===============================")
    print("- IP: ", IP)
    print("- PORTA: ", PORT)
    
    print("\n== REQUISITANDO ARQUIVO ==================================")
    print("\nGET", file_name)
    req = encode_msg("GET", file_name.encode())
    s.sendto(req, addr)

    file_data = {}
    loss_segm = []
    n_segm = 0
    data_transmission = True

    print("\n== AGUARDANDO RECEBIMENTO ================================")
    while data_transmission:
        try:
            msg, addr = s.recvfrom(MSG_SIZE)
            type, id, length, checksum, data = decode_msg(msg)

            if type == "INFO":
                n_segm = int(data)
                print(f"\n- Arquivo será recebido em {n_segm} pacotes")

            if type == "DATA":
                
                if n_segm <= 0:
                    n_segm = id

                # Simulação de perda
                if random.random() < 0.1:
                    print("\n- Simulando perda do segmento")
                    print("\n---")
                    continue

                # Simulação de corrompimento
                if random.random() < 0.1:
                    data = data[id-5:id]

                test_checksum = calc_chksum(data)
                print("\n- Checksum recalculado: ", test_checksum)
                if test_checksum != checksum:
                    print("=> Perda detectada")
                else:
                    file_data[id] = data.decode()
                    print("=> Recebido com integridade") 

                print("\n---")

            if type == "END":
                for i in range(1, n_segm):
                    if i not in file_data:
                        loss_segm.append(i)
                data_transmission = False

        except socket.timeout:
            print("\n== TIMEOUT: Servidor não respondeu ========================")
            exit()

    print("\n== RECEBIMENTO FINALIZADO =================================")
    print("- Segmentos perdidos: ", loss_segm)

    print("\n== REQUISITANDO RETRANSMISSÃO SE NECESSÁRIO ===========")
    while len(loss_segm) > 0:
        ret_msg = encode_msg("RET", "".encode(), id=loss_segm[0])
        s.sendto(ret_msg, addr)
        try:
            msg, addr = s.recvfrom(MSG_SIZE) # bloqueia até receber dados
            type, id, length, checksum, data = decode_msg(msg)

            if type == "DATA":
                if id == loss_segm[0]:
                    test_checksum = calc_chksum(data)
                    if test_checksum == checksum:
                        file_data[loss_segm[0]] = data.decode()
                        loss_segm.pop(0)
        except socket.timeout:
            print("\n== TIMEOUT: Servidor não respondeu ========================")
            exit()

    print("\n== RETRANSMISSÃO CONCLUÍDA ================================")
            
    with open(result_file, "w") as f:
        for seg_id in sorted(file_data.keys()):
            f.write(file_data[seg_id])
        print(f"\n== ARQUIVO REMONTADO E SALVO =============================")
