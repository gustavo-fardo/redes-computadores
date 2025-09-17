import socket
from utils import decode_msg, encode_msg, calc_chksum, MSG_SIZE

IP = "127.0.0.1"
PORT = 65432


user_input = input("Digite sua requisição em formato: @IP_Servidor:Porta_Servidor/nome_do_arquivo.ext\n")
user_input = user_input.split("/")
file_name = user_input[1]
server_info = user_input[0].split(":")
ip_server = server_info[0][1:]
port_server = int(server_info[1])

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    addr = (ip_server, port_server)
    
    req = encode_msg("GET", file_name)
    s.sendto(req, addr)

    file_data = {}
    loss_segm = []
    type = ""
    incomplete_file = True
    end_transmission = False

    while incomplete_file:
        msg, addr = s.recvfrom(MSG_SIZE) # bloqueia até receber dados
        type, id, len, checksum, data = decode_msg(msg)

        if type == "DATA" and not(end_transmission):
            test_checksum = calc_chksum(data)
            print("\nChecksum: ", test_checksum)
            if test_checksum != checksum:
                loss_segm.append(id)
                print("Segmentos perdidos: ", loss_segm)
            else:
                file_data[id] = data.decode()
                print("Recebido com integridade") 

        if type == "END":
            end_transmission = True

        if type == "DATA" and end_transmission:
            if len(loss_segm) > 0:
                ret_msg = encode_msg("RET", "", loss_segm[0])
                test_checksum = calc_chksum(data)
                if test_checksum == checksum:
                    file_data[loss_segm[0]] = data.decode()
                    loss_segm.pop(0)
            else:
                incomplete_file = False
            
