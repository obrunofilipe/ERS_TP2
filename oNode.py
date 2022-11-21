import socket
import sys
import threading
import monitoring
import time

neighbours = []

"""
Estrutura de monitoring:

{
    "id" : {
        "delay" : --,
        "steps" : --,
        "ip" : --,
    },
    ....
}

"""

monitoring_rec = {}
endereco = "10.0.11.10"

def get_neighbours():
    s : socket.socket
    msg : str

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    msg = "Pedir vizinhos"

    s.sendto(msg.encode('utf-8'), (endereco, 2000))
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

def probe_processing(s,msg,address):
    global monitoring_rec
    metrics = msg.decode('utf-8').split(";")
    id = metrics[0]
    port = 4000
    print("Recebi a mensagem ::",metrics)
    send_timeStamp = time.time()
    rcv_timeStamp = float(metrics[1])
    steps = int(metrics[2])

    packet = monitoring.make_probe(id,rcv_timeStamp,steps+1) #
    for n in neighbours:
        if n != address[0]:
            s.sendto(packet,(n,port))


   
    delay = (send_timeStamp - rcv_timeStamp) * 1e3


    if id in monitoring_rec:
        server_monitoring = monitoring_rec[id]
        if delay < server_monitoring['delay']:
            monitoring_rec[id]['delay'] = delay
            monitoring_rec[id]['steps'] = steps+1
            monitoring_rec[id]['ip'] = address[0]
            print(f"Server Record {id} Atualizado:: delay:{delay}, steps:{steps+1}, ip:{address[0]}")
    else:
        monitoring_rec[id] = {}
        monitoring_rec[id]['delay'] = delay
        monitoring_rec[id]['steps'] = steps+1
        monitoring_rec[id]['ip'] = address[0]
        print(f"Server Record {id} Criado:: delay:{delay}, steps:{steps+1}, ip:{address[0]}")
    








def probe_service():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    HOST = ''
    PORT = 4000

    s.bind((HOST,PORT))
    print(f"A receber probes no: {HOST}:{PORT}")
    while True:
        msg, address = s.recvfrom(1024)
        print("recebi probe:",msg)
        threading.Thread(target=probe_processing,args=(s,msg,address)).start()

def main():
    get_neighbours()
    print(neighbours)
    threading.Thread(target=difusion_video_service, args=()).start()
    threading.Thread(target=probe_service, args=()).start()






if __name__ == "__main__":
    main()