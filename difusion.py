import socket
import sys
import threading


neighbours = []


def get_neighbours():
    s : socket.socket
    msg : str

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    msg = "Pedir vizinhos"

    s.sendto(msg.encode('utf-8'), ('10.0.5.10', 2000))
    resposta, server_add = s.recvfrom(1024)
    
    global neighbours
    neighbours = resposta.decode('utf-8').split(" ")



def difusion_video_processing(s , msg, add):
    print(neighbours)
    for ip in neighbours:
        if ip != add:
            print("Enviei para ::", ip)
            s.sendto(msg, (ip,3000))
    



def difusion_video_service():

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    HOST = ''
    PORT = 3000

    s.bind((HOST,PORT))

    while True:
        msg, add = s.recvfrom(1024)

        print("Recebi::",msg.decode('utf-8'))

        threading.Thread(target=difusion_video_processing,args=(s,msg,add)).start()





def main():
    get_neighbours()

    threading.Thread(target=difusion_video_service, args=()).start()






if __name__ == "__main__":
    main()