import struct
import time
import traceback
from struct import *
import enum
import socket
# from msvcrt import getch
from threading import Thread
# import keyboard
from scapy.all import *


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
        self.team_name = "PD1"
        self.ip = CLIENT_IP
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.game_is_on = False

    def connect_to_server(self, server_ip, server_port):
        """
        This function sends a connection request to the server.
        """
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1) # as is
        self.tcp_socket.bind(('', localPORTTCP))
        self.tcp_socket.connect((server_ip, server_port))
        print("Connected to Server")

    def send_name(self):
        msg = self.team_name + '\n'
        self.tcp_socket.send(msg.encode())

    def send_to_server(self, event):
        """
        This function sends an event to the server.
        :param event: event to send
        """
        try:
            print(event.name)
            self.tcp_socket.send(event.name.encode())
        except:
            print("something went wrong - with key pressing sending from CLIENT to SERVER")

    def start_run(self):
        """
        This function lets the client to listen for boradcast from the server,
        and then sends the Client's Team Name to the Server
        """
        print("Client Started, listening for offer requests...")
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1) # as is
        self.udp_socket.bind(('', localPORTUDP)) # bind socket to local port number ??

        while True:
            try:
                msg, server_address = self.udp_socket.recvfrom(BUFFER_SIZE) #read reply characters fromsocket into string
                unpacked_msg = struct.unpack('Ibh', msg) #unpacking the message for a tuple with :
                magic_cookie = unpacked_msg[0]
                msg_type = unpacked_msg[1]
                server_port = unpacked_msg[2]
                if magic_cookie != MAGIC_COOKIE or msg_type != MSG_TYPE:
                    continue
                print(f'Received offer from {server_address[0]}, attempting to connect...')
                self.connect_to_server(server_address[0], server_port)
                try:
                    print('good')
                    # send team name to server
                    self.send_name()
                except:
                    print('bad')
                    self.tcp_socket.close()
                    continue
                break
            except:
                continue
        self.udp_socket.close()


    def finish_run(self):
        """
        This function closes the tcp socket of the client.
        """
        self.tcp_socket.close()


    # def answer_question(self):
    #     # print("trying pressing")
    #     counter_press = 0
    #     keyboard.on_press(self.send_to_server)
    #     while self.game_is_on:
    #         continue
    #     print("stopped typing")

    # def keyboard_presser(self):
    #     # print("trying pressing")
    #     counter_press = 0
    #     keyboard.on_press(self.send_to_server)
    #     while self.game_is_on:
    #         continue
    #     print("stopped typing")

    # def game_play(self):
    #     try:
    #         keyboard_thread = Thread(target=self.keyboard_presser)
    #         msg = self.tcp_socket.recv(2048).decode()
    #         print(msg)  # game started
    #         self.game_is_on = True
    #         keyboard_thread.start()
    #         msg = self.tcp_socket.recv(2048).decode()
    #         self.game_is_on = False
    #         keyboard_thread.join()
    #         print(msg)  # game ended
    #         print("Server disconnected, listening for offer requests...")
    #         self.tcp_socket.close()
    #         return
    #     except:
    #         # traceback.print_exc()
    #         self.finish_run()
    #         return
    def game_play(self):
        """
        This function is used when the client starts to play the game - and starts to press button on the keyboard
        """
        message = self.tcp_socket.recv(BUFFER_SIZE)
        message = str(message, 'utf-8')
        print(message)
        message = None
        while True:
            try:
                incoming_message, _, _ = select([self.tcp_socket],[],[],0.2)
                if incoming_message:
                    message = self.tcp_socket.recv(BUFFER_SIZE)
            except:
                pass
            if not message:
                os.system("stty raw -echo")
                char_coming, _, _ = select([sys.stdin], [], [], 0.2)
                if char_coming:
                    key = sys.stdin.read(1)
                    self.tcp_socket.send(key.encode())
            else:
                os.system("stty -raw echo")
                message = str(message, 'utf-8')
                print(message)
                break
        self.udp_socket.close()

def main():
    while True:
        client = Client()
        client.start_run()
        try:
            client.game_play()
            # sleep(5)
        except:
            # traceback.print_exc()
            continue


if __name__ == '__main__':
    main()


