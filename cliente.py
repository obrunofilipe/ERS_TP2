import socket
import sys
import threading

from tkinter import Tk
from ClienteGUI import ClienteGUI

neighbours = []
SERVER_IP = "10.0.11.10"

# Função que tem como objetivo fazer o pedido da lista de vizinhos ao nodo bootstrapper

def get_neighbours():
    s : socket.socket
    msg : str

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('',2000))

    msg = "Pedir vizinhos"
    global neighbours
    s.sendto(msg.encode('utf-8'), (SERVER_IP, 2000))
    resposta, server_add = s.recvfrom(1024)
    neighbours = resposta.decode('utf-8').split(";")[0].split(" ")

    s.close()


# Função que envia o pedido de vídeo para o nodo de acessoo do cliente que depois viajará até ao servidor
# Quando este pedido é enviado, é criada uma thread que ficará à espera dos pacotes de vídeo vindos do servidor para os poder reproduzir

def request_video():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('',5000))


    #id;nome-video
    msg = "movie.Mjpeg"
    s.sendto(msg.encode('utf-8'), (neighbours[0],5000))
    threading.Thread(target=recv_video_processing,args=[s]).start()


# Função responsável por processar os pacotes da stream vindos do servidor de modo a reproduzi-los e a apresentá-los ao servidor
# através de uma interface gráfica

def recv_video_processing(s):

    while True:
        try:
            addr = '127.0.0.1'
            port = 6000
        except:
            print("[Usage: Cliente.py]\n")	

        root = Tk()
	
        # Create a new client
        app = ClienteGUI(root, addr, port)
        app.master.title("Cliente Exemplo")	
        root.mainloop()




def main():

    get_neighbours()
    request_video()


if __name__ == "__main__":
    main()