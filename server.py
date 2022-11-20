import socket
import threading
import time
import json

difusion_node = "10.0.5.1"


def get_video_processing(s : socket, msg : bytes, add : tuple):
    while True :
        s.sendto("video".encode('utf-8'),(difusion_node,3000))
        time.sleep(2)

def get_video_service():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    endereco = '10.0.5.10'
    port = 3000
    s.bind((endereco, port))
    print(f"Estou à escuta no {endereco}:{port}")

    while True:
        msg, add = s.recvfrom(1024)
        threading.Thread(target=get_video_processing,args=(s,msg,add)).start()
    
    s.close()


def bootstrap_processing(s : socket, msg : bytes, address : tuple):
    print(address[0],address[1])
    neighbours = get_neighbours(address[0]) #lista de vizinhos
    message = " ".join(neighbours)
    s.sendto(message.encode('utf-8'), address)  
    

def get_neighbours(ip):
    f = open("config_topologia_1.json")
    neighbours = json.load(f)

    return neighbours[ip]

def bootstrap_service():
    s : socket.socket
    endereco : str
    port : int
    msg : bytes
    add : tuple

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    endereco = '10.0.5.10'
    port = 2000

    s.bind((endereco, port))

    print(f"Estou à escuta no {endereco}:{port}")

    while True:
        msg, add = s.recvfrom(1024)
        threading.Thread(target=bootstrap_processing, args=(s, msg, add)).start()

    s.close()

       
def main():
    threading.Thread(target=bootstrap_service, args=()).start()
    threading.Thread(target=get_video_service, args=()).start()


if __name__ == '__main__':
    main()