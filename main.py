import select
import socket
import sys
from threading import Thread
from time import sleep

BUFF_SIZE = 2096

LOCAL_HOST = '127.0.0.1'
LOCAL_PORT = 1337

HOST_TO = '127.0.0.1'
PORT_TO = 3306


def keep_alive_terminal():
    # keep alive openshift connection
    while True:
        sleep(15)
        print('please don\'t close')


def proxy(sock_in, sock_out):
    data = b''
    while True:
        part = sock_in.recv(BUFF_SIZE)
        data += part
        if len(part) < BUFF_SIZE:
            break

    # print(f'>> {len(data)}: ', data) #debug logs
    sock_out.sendall(data)

    if not data:
        print('broken connection')
        sys.exit(1)


if __name__ == '__main__':
    Thread(target=keep_alive_terminal).start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((LOCAL_HOST, LOCAL_PORT))
        server.listen()
        read_sockets, write_sockets, error_sockets = select.select([server], [], [])

        # for every connection to server
        while True:
            for s in read_sockets:
                (client, (ip, port)) = s.accept()
                print('new connection')

                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as mysql:
                    mysql.connect((HOST_TO, PORT_TO))

                    # keep alive socket connection
                    while True:
                        proxy(mysql, client)
                        proxy(client, mysql)
