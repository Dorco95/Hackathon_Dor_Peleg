import enum
import time
import traceback
from socket import *
from threading import *
import struct
import random

# SERVER_IP = gethostbyname(gethostname())
SERVER_IP = '172.1.0.4'
# SERVER_IP = 'localhost'
# SERVER_IP = get_if_addr("eth1") # 172.1.0
# SERVER_IP = get_if_addr("eth2") # 172.99.0
SERVER_PORT_TCP = 12712 # ??????
SERVER_PORT_UDP = 12711
UDP_DEST_PORT = 13110
BUFFER_SIZE = 2048
MAGIC_COOKIE = 0xabcddcba
MSG_TYPE = 0x2

class Server:
    def __init__(self):
        self.udp_socket = socket(AF_INET, SOCK_DGRAM)
        self.tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.connections = {} # Players: "player1":
        self.game_treads = {}
        self.players = {}
        self.equations = [('1+1',2), ('1+2',3)]

    def send_broadcast_messages(self, udp_socket):
        message_to_send = struct.pack('Ibh', MAGIC_COOKIE, MSG_TYPE, SERVER_PORT_TCP)
        while len(self.connections) < 2:
            udp_socket.sendto(message_to_send, ('<broadcast>', UDP_DEST_PORT))
            time.sleep(1)


    def accept_conn(self, broadcast_thread, tcp_socket):
        while broadcast_thread.is_alive():
            print(len(self.connections))
            try:
                client_socket, address = tcp_socket.accept()
                player = client_socket.recv(2048).decode()
                print(11111111, player)
                self.connections[player] = {"client_socket": client_socket, "address": address}
            except timeout:
                # traceback.print_exc()
                continue


    def waiting_for_clients(self):
        """
            This function sends UDP broadcast messages each 1 sec
            for 10 seconds and listening for clients responses.
        """
        self.udp_socket.bind(('', SERVER_PORT_UDP))
        self.udp_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) # as is
        self.tcp_socket.bind(('', SERVER_PORT_TCP))
        self.tcp_socket.listen(20)
        self.tcp_socket.settimeout(2) # ???
        broadcast_thread = Thread(target=self.send_broadcast_messages, args=(self.udp_socket,))
        accpt_conn_thread = Thread(target=self.accept_conn, args=(broadcast_thread, self.tcp_socket))
        broadcast_thread.start()
        accpt_conn_thread.start()
        # broadcast_thread.join() # Changed by Peleg.
        accpt_conn_thread.join()
        self.udp_socket.close()
        self.tcp_socket.close()

    def game_play_trd(self, connection_dict: dict, player_name, math):
        print(player_name)
        players = list(connection_dict.keys())
        msg = f'Welcome to Quick Maths.\nPlayer 1: {players[0]}'
        msg += f'Player 2: {players[1]}'
        msg += "==\nPlease answer the following questions as fast as you can:\n"
        question = math
        # sleep(1)
        msg += f'How much is {question}?'
        connection_dict[player_name]['client_socket'].send(msg.encode()) #  the message to the socket name of each player
        counter = 0
        ans = None
        # start = time.time()
        play_until = time.time() + 10
        while time.time() <= play_until and counter == 0: # handle first to answer
            ans = connection_dict[player_name]['client_socket'].recv(2048).decode()
            counter += 1
            print(f'hereeeeeee{ans}') # what the client typpe ???????????????
        if counter > 0:
            self.players[time.time()-start] = (ans, player_name)
        else:
            self.players[10] = (ans, player_name)
        print(self.players)
        print('finished BBC')


    def game_play(self):
        if len(self.connections) < 2:  # we cant start the game with 1 person
            print("not enough players to play")
            self.client_sockets_close()
            return
        math = random.choice(self.equations)
        print(1111, math)
        for player in self.connections:
            player_game_trd = Thread(target=self.game_play_trd, args=(self.connections, player, math[0]))

            # ???

            self.game_treads[player] = player_game_trd
            player_game_trd.start()
        for trd in self.game_treads:
            print("waiting for trd of "+trd)
            self.game_treads[trd].join()

            # ???
        # finish game
        msg = "\nGame over!\n"
        msg += f'The correct answer was {math[1]}!\n\n'
        if len(self.players) == 0:
            msg += "Draw..."
        else:
            fastest_time = min(list(self.players.keys()))
            if self.players[fastest_time][0] == math[1]:
                msg += f'Congratulations to the winner: {players[fastest_time][1]}'
            else:
                conn_players = list(self.connections.keys())
                for player in conn_players:
                    if player != self.players[fastest_time][1]:
                        msg += f'Congratulations to the winner: {player}'
                        break
        for player in self.connections:
            self.connections[player]['client_socket'].send(msg.encode())
            self.connections[player]['client_socket'].close()
        print("Game over, sending out offer requests...")



    def client_sockets_close(self):
        for player in self.connections:
            print(self.connections)
            print(self.connections[player])
            print(self.connections[player]["client_socket"])
            self.connections[player]["client_socket"].close()


    def crash(self):
        self.client_sockets_close()
        self.tcp_socket.close()
        self.udp_socket.close()


print(f'Server started, listening on IP address {SERVER_IP}')
while 1:
    server = Server()
    try:
        server.waiting_for_clients()
    except Exception:
        traceback.print_exc()
        continue
    try:
        server.game_play()
    except Exception:
        traceback.print_exc()
        server.client_sockets_close()
        continue
