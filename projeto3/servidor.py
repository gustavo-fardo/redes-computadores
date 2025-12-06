import socket
import threading
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

MSG_SIZE = 10000

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Read the last received HTML file
        with open("r.html", "r", encoding="utf-8") as f:
            content = f.read()

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))

IP = "127.0.0.1"
PORT = 65432

# print(f"HTTP server running at http://{IP}:{PORT}")
# HTTPServer((IP, PORT), Handler).serve_forever()

def client_thread(conn, addr):
    with conn:
        print(f"\n[{addr}] => Conexão estabelecida")
        data = conn.recv(MSG_SIZE).decode("utf-8")
        print(f"\n[{addr}] Requisição recebida:")
        print(data)

        lines = data.split("\r\n")
        if len(lines) > 0:
            first_line = lines[0]
            _, path, _ = first_line.split(" ")

            file_path = "." + path   # exemplo: ./pagina.html

            if os.path.exists(file_path):
                # descobrir tipo do arquivo
                if file_path.endswith(".html"):
                    content_type = "text/html"
                elif file_path.endswith(".jpg") or file_path.endswith(".jpeg"):
                    content_type = "image/jpeg"
                else:
                    # formato proibido 403
                    body = b"<h1>403 - Forbidden</h1>"
                    header = (
                        "HTTP/1.1 404 Forbidden\r\n"
                        "Content-Type: text/html\r\n"
                        f"Content-Length: {len(body)}\r\n"
                        "Connection: close\r\n"
                        "\r\n"
                    ).encode("utf-8")

                    conn.sendall(header + body)

                with open(file_path, "rb") as f:
                    body = f.read()

                header = (
                    "HTTP/1.1 200 OK\r\n"
                    f"Content-Type: {content_type}\r\n"
                    f"Content-Length: {len(body)}\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                ).encode("utf-8")

                conn.sendall(header + body)

            else:
                # arquivo nao existe 404
                body = b"<h1>404 - Not Found</h1>"
                header = (
                    "HTTP/1.1 404 Not Found\r\n"
                    "Content-Type: text/html\r\n"
                    f"Content-Length: {len(body)}\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                ).encode("utf-8")

                conn.sendall(header + body)

        print(f"[{addr}] => Resposta enviada:")
        print(header.decode("utf-8") + body.decode("utf-8", errors="ignore"))

        conn.close()
        print(f"\n[{addr}] => Fim da transmissao")

# socket.AF_INET -> IPv4
# socket.SOCK_STREAM -> TCP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((IP, PORT))
    s.listen()
    print("\n== SERVIDOR INICIADO, AGUARDANDO CONEXÕES ===================")
    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=client_thread, args=(conn, addr,))
        t.start()

