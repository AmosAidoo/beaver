import socket
import os
import argparse
import queue
import select

argumentParser = argparse.ArgumentParser()
argumentParser.add_argument("-a", "--address", type=str, help="host address. 127.0.0.1 by default")
argumentParser.add_argument("-p", "--port", type=int, help="port. 8000 by default")
argumentParser.add_argument("-r", "--root", type=str, help="root directory")

args = argumentParser.parse_args()

HOST = "127.0.0.1" if args.address is None else args.address
PORT = 8000 if args.port is None else args.port
ROOT_DIR = "./" if args.root is None else args.root

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)

server_address = (HOST, PORT)
server.bind(server_address)

BUFFER = 1024

print(f"Listening at {server_address[0]}:{server_address[1]}")

print(server)

# Sockets from which we expect to read
inputs = [server]

# Sockers from which we expect to write
outputs = []

# Outgoing message queues
message_queues = {}

server.listen(5)

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
    
    client_conn.sendall(response)

print(f"Listening at port {HOST}:{PORT}")

while inputs:
    readable, writable, exceptional = select.select(inputs, outputs, inputs)

    # Handle inputs
    for s in readable:
        if s is server:
            connection, client_address = s.accept()
            print("New connection from", client_address)
            connection.setblocking(0)
            inputs.append(connection)

            message_queues[connection] = queue.Queue()
        else:
            data = s.recv(BUFFER)
            if data:
                message_queues[s].put(data)

                if s not in outputs:
                    outputs.append(s)
            else:
                # Interpret empty result as closed connection
                print("Closing", client_address, "after reading no data")

                if s in outputs:
                    outputs.remove(s)
                inputs.remove(s)
                s.close()

                # Remove message queue
                del message_queues[s]

    for s in writable:
        try:
            request = message_queues[s].get_nowait()
        except queue.Empty:
            print("Output queue for", s.getpeername(), "is empty")
            outputs.remove(s)
        else:
            request_line, headers, body = parse_request(request)
            send_response(s, request_line, headers, body)

            if s in outputs:
                outputs.remove(s)
            inputs.remove(s)
            s.close()

    for s in exceptional:
        print("Handling exceptional condition for", s.getpeername())
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()

        del message_queues[s]
