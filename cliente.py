import socket
import sys
import threading

neighbours = []
SERVER_IP ='10.0.5.10'

def get_neighbours():
    s : socket.socket
    msg : str

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('',2000))

    msg = "Pedir vizinhos"

    s.sendto(msg.encode('utf-8'), (SERVER_IP, 2000))
    resposta, server_add = s.recvfrom(1024)
    neighbours = resposta.decode('utf-8').split(" ")
    s.close()


def get_video():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('',3000))

    msg = "pedido video"
    s.sendto(msg.encode('utf-8'), (SERVER_IP,3000))
    threading.Thread(target=recv_video_processing,args=[s]).start()

def recv_video_processing(s):

    while True:
        msg,add = s.recvfrom(4096)
        print("Mensagem recebida do:",add,"mensagem::",msg)



def main():

    get_neighbours()
    get_video()

if __name__ == "__main__":
    main()