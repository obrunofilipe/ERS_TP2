import socket
import sys
import threading

from tkinter import Tk
from ClienteGUI import ClienteGUI

neighbours = []
SERVER_IP = "10.0.11.10"


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
    s.bind(('',5000))


    #id;nome-video
    msg = "movie.Mjpeg"
    s.sendto(msg.encode('utf-8'), (neighbours[0],5000))
    threading.Thread(target=recv_video_processing,args=[s]).start()

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