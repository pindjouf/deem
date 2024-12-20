import socket
from src.resolver import resolver

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(("127.0.0.1", 53053))

while True:
    (client_socket, address) = server_socket.recvfrom(1024)
    resolver(client_socket.hex())
