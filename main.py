import socket
import os
import sys
import argparse

argumentParser = argparse.ArgumentParser()
argumentParser.add_argument("-a", "--address", type=str, help="host address. 127.0.0.1 by default")
argumentParser.add_argument("-p", "--port", type=int, help="port. 8000 by default")
argumentParser.add_argument("-r", "--root", type=str, help="root directory")

args = argumentParser.parse_args()

HOST = "127.0.0.1" if args.address is None else args.address
PORT = 8000 if args.port is None else args.port
ROOT_DIR = "./" if args.root is None else args.root

def parse_request(request):
    tokens = request.decode("utf8").split("\r\n")
    request_line = tokens[0]
    headers = []
    last_idx = 1
    for i in range(1, len(tokens)):
        if tokens[i] == '':
            last_idx = i
            break
        headers.append(tokens[i])
    
    body = ""
    for i in range(last_idx + 1, len(tokens)):
        body += tokens[i]
    
    print("Request Line:", request_line)
    print("Headers:", headers)
    print("Body:", body)
    return request_line, headers, body

def send_response(client_conn, request_line, headers, body):
    status_line = b"HTTP/1.1 200 OK\n"
    headers = b"\n"
    body = b""
    
    path = os.path.join(ROOT_DIR, request_line.split()[1][1:])
    
    if os.path.isdir(path):
        listing = os.listdir(path)
        body += b"<h1>Directory listing</h1>" 
        body += b"<ul>"
        for item in listing:
            body += b"<li>" + f"<a href=\"{path}{item}\">".encode("utf8") + item.encode("utf8") + b"</a></li>"
        body += b"</ul>"
    elif os.path.isfile(path):
        file = open(path, "rb")
        content = file.read()
        body = content
        file.close()
    else:
        status_line = b"HTTP/1.1 404 NOT FOUND\n"
        body = b"<p>Resourse could not be found on the server</p>"

    # Form the http response
    response = status_line + headers + body
    
    print(response)
    
    client_conn.sendall(response)

print(f"Listening at port {PORT}")

while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        conn, addr = s.accept()
        
        with conn:
            print("Connected by", addr)
            request = b""
            BUFFER = 1024

            # Read the request from the client
            while True:
                data = conn.recv(BUFFER)
                length = len(data)
                request += data
                
                if data == b"":
                    break
                
                # This is to detect the end of the request
                # It seems to work though there might be some corner cases
                # I will write some tests
                if length < BUFFER and data[length - 1] == 0xA:
                    break

            request_line, headers, body = parse_request(request)

            send_response(conn, request_line, headers, body)
