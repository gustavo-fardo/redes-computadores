import socket
import threading

IP = "127.0.0.1"
PORT = 65432

def client_thread(conn, addr):
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data) 

# socket.AF_INET -> IPv4
# socket.SOCK_STREAM -> TCP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((IP, PORT))
    while True:
        s.listen()
        conn, addr = s.accept()
        t = threading.Thread(target=client_thread, args=(conn, addr,))
        t.start()

