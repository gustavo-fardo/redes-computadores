import socket

IP = "127.0.0.1"
PORT = 65432
BUFSIZE = 1024

# socket.AF_INET -> IPv4
# socket.SOCK_DGRAM -> UDP
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((IP, PORT)) # IPv4 espera tupla (IP, PORT)
    while True:
        req, addr = s.recvfrom(BUFSIZE) # bloqueia até receber dados
        print("Recebido:", req.decode())
        req = req.decode().split(" ")
        file_name = req[1]

        with open(file_name, "r") as f:
            data = f.read().encode()

            print("Enviando", len(data), "para", addr)

            s.sendto(data, addr)