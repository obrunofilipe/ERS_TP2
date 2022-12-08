import socket
import sys
import threading
import monitoring
import time

neighbours = []
"""
{
    "ip" : 1/0
}
"""

interface_status = {}

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


def init_status():
    global interface_status
    for n in neighbours:
        interface_status[n] = 0 # inicializar todas as interfaces como inativas


def get_neighbours():
    s : socket.socket
    msg : str

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    msg = "Pedir vizinhos"

    s.sendto(msg.encode('utf-8'), (endereco, 2000))
    resposta, server_add = s.recvfrom(1024)
    
    global neighbours
    neighbours = resposta.decode('utf-8').split(" ")


 
def request_video_processing(s , msg, add):
    stream_flag = False
    for (_,flag) in interface_status.items():
        if flag == 1:
            stream_flag = True

    if not stream_flag:
        #ativar interaface do cliente para difundir o video
        # ativar a interface mais próxima e a do cliente 
        # pedir o video ao nodo seguinte no caminhoa até ao servidor
        # ficar à espera do vídeo
        server_id = msg.decode("utf-8").split(";")[0]
        next_step = monitoring_rec[server_id]['ip']
        interface_status[next_step] = 1 
        s.sendto(msg,(next_step,5000))
        threading.Thread(target=difusion_service,args=()).start()
        #service to send video
    else:
        print(f'JA TENHO O VIDEO ATIVEI A INTERFACE::: {add[0]}')
    interface_status[add[0]] = 1



def request_video_service():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    HOST = ''
    PORT = 5000

    s.bind((HOST,PORT))

    while True:
        msg, add = s.recvfrom(1024)

        print("\n\n\n Recebi:: \n\n\n",msg.decode('utf-8'))

        threading.Thread(target=request_video_processing,args=(s,msg,add)).start()


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
        if n != address[0] and steps < 6:
            s.sendto(packet,(n,port))


   
    incoming_delay = (send_timeStamp - rcv_timeStamp) * 1e3



    if id in monitoring_rec:
        server_monitoring = monitoring_rec[id]
        old_delay = server_monitoring['delay']
        alpha = 0.1
        delay = alpha*old_delay + (1-alpha)*incoming_delay

        if delay < server_monitoring['delay']:
            monitoring_rec[id]['delay'] = delay
            monitoring_rec[id]['steps'] = steps+1
            monitoring_rec[id]['ip'] = address[0]
            print(f"Server Record {id} Atualizado:: delay:{delay}, steps:{steps+1}, ip:{address[0]}")
    else:
        monitoring_rec[id] = {}
        monitoring_rec[id]['delay'] = incoming_delay
        monitoring_rec[id]['steps'] = steps+1
        monitoring_rec[id]['ip'] = address[0]
        print(f"Server Record {id} Criado:: delay:{incoming_delay}, steps:{steps+1}, ip:{address[0]}")



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

def difusion_processing(s,msg,add): #controlled floading
    for (ip,status) in interface_status.items():
        if ip != add[0] and status:
            s.sendto(msg,(ip,6000))


def difusion_service():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    HOST = ''
    PORT = 6000

    s.bind((HOST,PORT))
    while True:
        msg, add = s.recvfrom(20480)
        threading.Thread(target=difusion_processing,args=(s,msg,add)).start()

def main():
    get_neighbours()
    init_status()
    print(neighbours)
    threading.Thread(target=request_video_service, args=()).start()
    threading.Thread(target=probe_service, args=()).start()







if __name__ == "__main__":
    main()