import socket
import sys
import threading

neighbours = []

  
def get_neighbours():
    s : socket.socket
    msg : str

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('',2000))

    msg = "Pedir vizinhos"
    global neighbours
    s.sendto(msg.encode('utf-8'), (SERVER_IP, 2000))
    resposta, server_add = s.recvfrom(1024)
    neighbours = resposta.decode('utf-8').split(" ")

    s.close()


def request_video():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('',3000))


    #id;nome-video
    msg = ""
    s.sendto(msg.encode('utf-8'), (neighbours[0],5000))
    threading.Thread(target=recv_video_processing,args=[s]).start()

def recv_video_processing(s):

    while True:
        msg,add = s.recvfrom(4096)
        print("Mensagem recebida do:",add,"mensagem::",msg)



def main():

    get_neighbours()
    request_video()


if __name__ == "__main__":
    main()