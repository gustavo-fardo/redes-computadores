import socket

IP = "127.0.0.1"
PORT = 65432
BUFSIZE = 1024

while True:
    user_input = input("Digite sua requisição em formato: @IP_Servidor:Porta_Servidor/nome_do_arquivo.ext\n")
    user_input = user_input.split("/")
    file_name = user_input[1]
    server_info = user_input[0].split(":")
    ip_server = server_info[0][1:]
    port_server = int(server_info[1])

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        addr = (ip_server, port_server)
        req = b"GET " + file_name.encode()
        s.sendto(req, addr)
        data, addr = s.recvfrom(BUFSIZE) # bloqueia até receber dados
        print("Recebido", data.decode(), "de", addr)

