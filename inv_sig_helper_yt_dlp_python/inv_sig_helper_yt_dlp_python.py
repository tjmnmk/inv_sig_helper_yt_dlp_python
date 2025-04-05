import socket
import threading
from config import Config

from logger import logger
from stream_handler import ConnectionHandler
from player import Player

def handle_client(conn, addr, player):
    logger.info(f"[+] New connection from {addr}")

    try:
        ConnectionHandler(conn, player).runner()
    finally:
        conn.close()
        logger.info(f"[-] Connection closed from {addr}")
    
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((Config.get_host(), Config.get_port()))
    server.listen()
    logger.info(f"[+] Server listening on {Config.get_host()}:{Config.get_port()}")

    player = Player()

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr, player), daemon=True)
        thread.start()

if __name__ == "__main__":
    main()