import socket
from src.resolver import resolver
from src.serialize import serialize

def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_ip = "127.0.0.1"
    server_port = 53053
    server_socket.bind((server_ip, server_port))

    print(f"DNS Server started on {server_ip}:{server_port}...")

    try:
        while True:
            try:
                data, address = server_socket.recvfrom(1024)
                print(f"\nQuery received from {address}")
                
                response = resolver(data.hex())
                raw_bytes = serialize(response)
                server_socket.sendto(raw_bytes, address)
                
                print(f"Response sent to {address}")
                
            except Exception as e:
                print(f"Error handling query: {e}")
                continue
                
    except KeyboardInterrupt:
        print("\nShutting down DNS server...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    server()
