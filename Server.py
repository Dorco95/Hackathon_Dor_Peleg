import enum
import time
import traceback
from socket import *
from threading import *
import struct
import random
from select import select

SERVER_IP = gethostbyname(gethostname())
# SERVER_IP = '172.1.0.4'
# SERVER_IP = 'localhost'
# SERVER_IP = get_if_addr("eth1") # 172.1.0
# SERVER_IP = get_if_addr("eth2") # 172.99.0
SERVER_PORT_TCP = 12712 # ??????
UDP_DEST_PORT = 14000
UDP_PORT = 13333
BUFFER_SIZE = 2048
MAGIC_COOKIE = 0xabcddcba
MSG_TYPE = 0x2


class Server:
    def __init__(self):
        self.udp_socket = socket(AF_INET, SOCK_DGRAM)
        self.tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.connections = {}
        self.equations = [('1+1',2), ('1+2',3), ('4+5',9), ('1+1-1+1-1-1+3',3), ('1.5+3.3+2.2',7)]
        self.answered = False
        self.names = {}
        self.client_sockets = []
        self.winner = None


    def send_broadcast_messages(self, udp_socket):
        message_to_send = struct.pack('Ibh', MAGIC_COOKIE, MSG_TYPE, SERVER_PORT_TCP)
        while len(self.connections) < 2:
            udp_socket.sendto(message_to_send, ('<broadcast>', UDP_DEST_PORT)) # change brodcast: 172.99.255.255
            time.sleep(1)


    def accept_connection(self, broadcast_thread, tcp_socket):
        while broadcast_thread.is_alive():
            try:
                client_socket, address = tcp_socket.accept()
                player = client_socket.recv(BUFFER_SIZE).decode()
                self.names[client_socket.getsockname()] = player
                self.client_sockets.append(client_socket)
                self.connections[player] = {"client_socket": client_socket, "address": address}
            except:
                continue


    def waiting_for_clients(self):
        # sockets definition:
        self.udp_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.udp_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        self.udp_socket.bind(('', UDP_PORT))
        self.tcp_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        self.tcp_socket.bind(('', SERVER_PORT_TCP))
        self.tcp_socket.listen(20)
        self.tcp_socket.settimeout(2)
        # Threads part:
        broadcast_thread = Thread(target=self.send_broadcast_messages, args=(self.udp_socket,))
        accept_thread = Thread(target=self.accept_connection, args=(broadcast_thread, self.tcp_socket))
        broadcast_thread.start()
        accept_thread.start()
        accept_thread.join()
        broadcast_thread.join()
        game_thread = Thread(target=self.game_play)
        game_thread.start()
        sleep(10)
        # Close and waiting_for_clients again:
        self.udp_socket.close()
        self.tcp_socket.close()
        self.waiting_for_clients

    def game_thread(self):
        # Game time:
        ans = None
        play_until = time.time() + 10
        while time.time() <= play_until and self.answered == False: # handle first to answer
            try:
                incoming_message, _, _ = select(self.client_sockets,[],[], 10)
                if len(incoming_message) == 0:
                    continue
                for sock in incoming_message:
                    ans = int(sock.recv(BUFFER_SIZE).decode())
                    player_answered = self.names[sock.getsockname()]
                    # Check the client answer:
                    if ans == correct_ans:
                        player_win = player_answered
                        self.winner = player_win
                        break
                    else:
                        for player in list(self.connections.keys()):
                            if player != player_answered:
                                player_win = player
                        self.winner = player_win
                        break
                self.answered = True
                break
            except: 
                continue
    


    def game_play(self):
        # Building message:
        math = random.choice(self.equations)
        players = list(self.connections.keys())
        msg = f'Welcome to Quick Maths.\nPlayer 1: {players[0]}'
        msg += f'Player 2: {players[1]}'
        msg += "==\nPlease answer the following questions as fast as you can:\n"
        question = math[0]
        correct_ans = math[1]
        msg += f'How much is {question}?'
        # Sending message:
        for sock in self.client_sockets:
            sock.send(msg.encode())
        # # Game time:
        # ans = None
        # play_until = time.time() + 10
        # while time.time() <= play_until and self.answered == False: # handle first to answer
        #     try:
        #         incoming_message, _, _ = select(self.client_sockets,[],[])
        #         # if len(incoming_message) == 0:
        #         #     continue
        #         for sock in incoming_message:
        #             ans = int(sock.recv(BUFFER_SIZE).decode())
        #             player_answered = self.names[sock.getsockname()]
        #             # Check the client answer:
        #             if ans == correct_ans:
        #                 player_win = player_answered
        #                 self.winner = player_win
        #                 break
        #             else:
        #                 for player in list(self.connections.keys()):
        #                     if player != player_answered:
        #                         player_win = player
        #                 self.winner = player_win
        #                 break
        #         self.answered = True
        #         break
        #     except: 
        #         continue
        
        game_thread = Thread(target=self.game_thread)
        game_thread.start()
        game_thread.join(10)
        
        # Game finished:
        # Message to clients:
        msg = "Game over!\n"
        msg += f'The correct answer was {math[1]}!\n\n'
        if self.winner == None:
            msg += "Draw..."
        else:
            msg += f'Congratulations to the winner: {self.winner}'
        # Sending message and close connections
        for player in self.connections:
            try:
                self.connections[player]['client_socket'].send(msg.encode())
                self.connections[player]['client_socket'].close()
            except:
                continue
        print("Game over, sending out offer requests...")


def main():
    print(f'Server started, listening on IP address {SERVER_IP}')
    while 1:
        server = Server()
        try:
            server.waiting_for_clients()
        except Exception:
            continue
        try:
            server.game_play()
        except Exception:
            for player in self.connections:
                server.connections[player]['client_socket'].close()
            continue


if __name__ == '__main__':
    main()
