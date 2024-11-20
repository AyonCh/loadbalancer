from sys import argv
import socket

PORT = int(argv[1])

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(("127.0.0.1", PORT))

server.listen()

while True:
    (clienthost, address) = server.accept()

    print(clienthost, address)
    
