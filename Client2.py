import struct
import time
import traceback
from struct import *
import enum
import socket
from threading import Thread
import getch
from scapy.all import *
import os
import sys
from select import select
import multiprocessing


# CLIENT_IP = '172.1.0/24'
# CLIENT_IP = get_if_addr("eth1") # 172.1.0 (eth1)
# CLIENT_IP = '172.1.0/24'
CLIENT_IP = socket.gethostbyname(socket.gethostname())  # 172.99.0 (eth2)
localPORTUDP = 13110
localPORTTCP = 2142
BUFFER_SIZE = 2048
MAGIC_COOKIE = 0xabcddcba
MSG_TYPE = 0x2


class Client:
    def __init__(self):
        self.team_name = "Second team"
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def connect_to_server(self, server_ip, server_port):
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1) # as is
        self.tcp_socket.bind(('', localPORTTCP))
        self.tcp_socket.connect((server_ip, server_port))
        print("Connected to Server")


    def send_name(self):
        msg = self.team_name + '\n'
        self.tcp_socket.send(msg.encode())
        

    def running_client(self):
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.udp_socket.bind(('', localPORTUDP))
        # Trying to connect server:
        while True:
            try:
                msg, server_address = self.udp_socket.recvfrom(BUFFER_SIZE)
                unpacked_msg = struct.unpack('Ibh', msg)
                magic_cookie = unpacked_msg[0]
                msg_type = unpacked_msg[1]
                server_port = unpacked_msg[2]
                if magic_cookie != MAGIC_COOKIE or msg_type != MSG_TYPE:
                    continue
                print(f'Received offer from {server_address[0]}, attempting to connect...')
                self.connect_to_server(server_address[0], server_port)
                try:
                    self.send_name()
                except:
                    self.tcp_socket.close()
                    continue
                break
            except:
                continue
        self.udp_socket.close()

   
    def game_play(self):
        welcome_message = self.tcp_socket.recv(BUFFER_SIZE)
        print(welcome_message.decode())
        # while True:
        # key_press = getch.getch()
            # if len(key_press) > 0:
        # self.tcp_socket.sendall(key_press.encode())
                # break
        p = multiprocessing.Process(target=self.getch_play)
        p.start()
        end_of_game_msg = self.tcp_socket.recv(BUFFER_SIZE).decode()
        p.terminate()
        # end_of_game_msg = self.tcp_socket.recv(BUFFER_SIZE).decode()
        print(end_of_game_msg)
        # End:
        print("Server disconnected, listening for offer requests...")
        self.tcp_socket.close()

    def getch_play(self):
        key_press = getch.getch()
        self.tcp_socket.sendall(key_press.encode())



def main():
    while True:
        client = Client()
        print("Client Started, listening for offer requests...")
        client.running_client()
        try:
            game_thread = Thread(target=client.game_play())
            game_thread.start()
            # game_thread.join()
        except:
            continue



if __name__ == '__main__':
    main()


