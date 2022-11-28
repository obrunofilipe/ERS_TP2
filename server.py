import socket
import threading
import time
import json
import monitoring

difusion_node = "10.0.5.1"
id = '1'  
endereco = "10.0.11.10"
neighbours = []

def get_neighbours():
    f = open("config_topologia_teste_2.json")
    n = json.load(f)
    global neighbours
    neighbours = n['servers'][id]


def request_video_processing(s : socket, msg : bytes, add : tuple):
    while True :
        s.sendto("video".encode('utf-8'),(neighbours[0],6000))
        print(f'sending video to {add}')
        time.sleep(2)

def request_video_service():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    port = 5000
    s.bind((endereco, port))
    print(f"Estou à escuta no {endereco}:{port}")

    while True:
        msg, add = s.recvfrom(1024)
        threading.Thread(target=request_video_processing,args=(s,msg,add)).start()
    
    s.close()


def bootstrap_processing(s : socket, msg : bytes, address : tuple):
    print(address[0],address[1])
    neighbours = send_neighbours(address[0]) #lista de vizinhos
    message = " ".join(neighbours)
    print(message.split(" "))
    s.sendto(message.encode('utf-8'), address)  
    

def send_neighbours(ip):
    f = open("config_topologia_teste_2.json")
    neighbours = json.load(f)

    print(neighbours['nodes'][ip])
    return neighbours['nodes'][ip]

def bootstrap_service():
    s : socket.socket
    port : int
    msg : bytes
    add : tuple

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    port = 2000

    s.bind((endereco, port))

    print(f"Estou à escuta no {endereco}:{port}")

    while True:
        msg, add = s.recvfrom(1024)
        print("recebi pedido de neighbours")
        threading.Thread(target=bootstrap_processing, args=(s, msg, add)).start()

    s.close()

def send_probe_service():
    port = 4000
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.bind(('',port))
    
    while True:
        packet = monitoring.make_probe(id, time.time(),0)
        for n in neighbours:
            print(f"A enviar probes para: {n}:{port}")
            s.sendto(packet,(n,port))
        time.sleep(20)
        

       
def main():
    get_neighbours()
    print(neighbours)
    threading.Thread(target=bootstrap_service, args=()).start()
    threading.Thread(target=request_video_service, args=()).start()
    threading.Thread(target=send_probe_service, args=()).start()


if __name__ == '__main__':
    main()