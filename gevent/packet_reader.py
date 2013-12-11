"""
Very simple ping-pong server using binary packet.

PING: PING (Magic, UBInt32) | Seq. Number (UBInt32)          | Timestamp (UBInt64)
PONG: PONG (Magic, UBInt32) | Ack. Number (Seq + 1, UBInt32) | Timestamp (UBInt64)
"""

import time
import threading

from gevent import socket, Timeout, timeout, Greenlet, sleep
from construct import *
from termcolor import colored


ping_parser = Struct(
    'ping',
    Magic('PING'),
    UBInt32('seq'),
    UBInt64('timestamp')
)

pong_parser = Struct(
    'pong',
    Magic('PONG'),
    UBInt32('ack'),
    UBInt64('timestamp')
)


def ping_parse(data):
    try:
        ping = ping_parser.parse(data)

        return ping
    except FieldError, e:
        print str(e)
    except ConstError, e:
        print str(e)

    return None


def pong_parse(data):
    try:
        pong = pong_parser.parse(data)

        return pong
    except FieldError, e:
        print str(e)
    except ConstError, e:
        print str(e)

    return None


def make_ping(seq):
    ping = ping_parser.build(
        Container(
            seq=seq,
            timestamp=int(time.time())
        )
    )

    return ping


def make_pong(ping):
    pong = pong_parser.build(
        Container(
            ack=ping.seq + 1,
            timestamp=int(time.time())
        )
    )

    return pong


server_run = True


def server_thread(port):
    global server_run

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', port))

    while server_run:
        try:
            with Timeout(2, False):
                (data, from_ip) = server_socket.recvfrom(1024)

            if data is None:
                continue

            ping = ping_parse(data)
            if ping is None:
                continue

            msg = 'Received - Seq: %d, Timestamp: %d' % (ping.seq, ping.timestamp)
            print colored(msg, 'green')

            pong = make_pong(ping)

            server_socket.sendto(pong, from_ip)

        except timeout:
            continue
        except KeyboardInterrupt:
            server_run = False


def client_request(no):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    seq = int(time.time() * no) % 1000

    while True:
        try:
            ping = make_ping(seq)

            print colored('[' + str(no) + '] Sending PING...', 'red')

            client_socket.sendto(ping, ('127.0.0.1', 33445))

            pong_packet, from_ip = client_socket.recvfrom(1024)
            pong = pong_parse(pong_packet)

            print colored('[' + str(no) + '] Ack. number: %d' % pong.ack, 'blue')

            seq = pong.ack

            sleep(1 + no)
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    server = Greenlet.spawn(server_thread, 33445)
    client = Greenlet.spawn(client_request, 1)
    client = Greenlet.spawn(client_request, 2)
    client = Greenlet.spawn(client_request, 3)

    try:
        server.join()
    except Timeout:
        pass
    except KeyboardInterrupt:
        pass
