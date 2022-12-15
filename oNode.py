import socket
import sys
import threading
import monitoring
import time

neighbours = []
"""
Estrutura do Estado das interfaces. 1 representa que a interface está ativa e 0 que está inativa

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

# Endereço conhecido do servidor Master, o servidor bootstrapper
endereco = "10.0.11.10"


# Variável global que indica de que servidor está a chegar o fluxo de stream a este nodo
incoming_server = "-1"

# Variável global usada para evitar ciclos na difusão dos pacotes de monitorização
PACKET_TTL = -1


lock = threading.Lock()


# Função de inicialização da estrutura das interfaces

def init_status():
    global interface_status
    lock.acquire()
    for n in neighbours:
        interface_status[n] = 0 # inicializar todas as interfaces como inativas
    lock.release()

# Função que tem como objetivo descobrir qual o delay mínimo entre todos os servidores presentes na estrutura de monitorização "monitoring_rec"

def min_delay():
    global incoming_server
    min = ('', 10000)

    lock.acquire()
    
    for id in monitoring_rec:
        delay = monitoring_rec[id]['delay']
        if delay < min[1]:
            min = (id, delay)
    lock.release()
    
    if incoming_server != min[0]:
        incoming_server = min[0]
        return True
    else:
        return False


# Função que tem como objetivo efetuar um novo pedido de stream ao próximo salto em direção ao novo servidor na situação em que o servidor ótimo deixa
# de ser o servidor de quem o nodo está a receber a stream para o servidor alternativo a esse

def request_new_server():
    global interface_status

    lock.acquire()
    
    for id in monitoring_rec: # desativar todas as interfaces que levam a servidores
        ip = monitoring_rec[id]['ip']
        interface_status[ip] = 0


    next_step = monitoring_rec[incoming_server]['ip'] # ver qual é o próximo passo para o incoming_server
    #interface_status[next_step] = 1                   # ativar a interface desse próximo passo

    stream_flag = False
    for (_,flag) in interface_status.items():
        if flag == 1:
            stream_flag = True

    lock.release()
    
    if stream_flag: # só faz um novo pedido se a stream alguma vez foi pedida
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto("movie.Mjpeg".encode('utf-8'),(next_step,5000))
    

# Função que tem como objetivo fazer o pedido da lista de vizinhos e do TTL dos pacotes de monitorização ao nodo bootstrapper
# Recebendo os vizinhoos e um TTL, guarda-os em variáveis globais, neighbours e PACKET_TTL, respetivamente


def get_neighbours():
    s : socket.socket
    msg : str

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    msg = "Pedir vizinhos"

    s.sendto(msg.encode('utf-8'), (endereco, 2000))
    resposta, server_add = s.recvfrom(1024)
    
    global neighbours
    global PACKET_TTL

    PACKET_TTL = int(resposta.decode('utf-8').split(";")[1])

    print("PACKET_TTL =", PACKET_TTL)

    neighbours = resposta.decode('utf-8').split(";")[0].split(" ")


# Função responsável por processar o pedido de um vídeo chegado de um nodo cliente ou de outro nodo intermédio
# Depois de feito o processamento, este redireciona o pedido para a interface de saída do próximo salto até ao servidor ideal e ativa a interface
# relativa ao nodo do qual recebeu este pedido
 
def request_video_processing(s , msg, add):
    stream_flag = False

    lock.acquire()
    
    for (_,flag) in interface_status.items():
        if flag == 1:
            stream_flag = True

    if not stream_flag:
        # ativar interaface do cliente para difundir o video
        # ativar a interface mais próxima e a do cliente 
        # pedir o video ao nodo seguinte no caminhoa até ao servidor
        # ficar à espera do vídeo
        #server_id = msg.decode("utf-8").split(";")[0]
        for server_id in monitoring_rec:
            next_step = monitoring_rec[server_id]['ip'] # fazer o pedido ao servidor com menor delay
            s.sendto(msg,(next_step,5000))
        threading.Thread(target=difusion_service,args=()).start()
        #service to send video
    else:
        print(f'JA TENHO O VIDEO ATIVEI A INTERFACE::: {add[0]}')
    interface_status[add[0]] = 1
    
    lock.release()


# Serviço que se encontra sempre disponível à espera de pacotes de pedido de vídeo vindos de clientes para a porta 5000
# Recebendo um destes pacotes, cria uma thread que vai efetuar o processamento do mesmo de forma a que possa continuar a receber pacotes sem que o serviço
# fique indisponível

def request_video_service():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    HOST = ''
    PORT = 5000

    s.bind((HOST,PORT))

    while True:
        msg, add = s.recvfrom(1024)

        print("\n\n\n Recebi:: \n\n\n",msg.decode('utf-8'))

        threading.Thread(target=request_video_processing,args=(s,msg,add)).start()


# Função que tem como objetivo processar os pacotes de prova enviados pelo servidor para a rede.
# Recebendo um destes pacotes, depois de extrair a informação relevante, e cria outro pacote com a mesma estrutura com os dados atualizados de modo a difundi-lo
# para todos os seus vizinhos, exceto para aquele do qual recebeu o pacote.

def probe_processing(s,msg,address):
    global monitoring_rec
    metrics = msg.decode('utf-8').split(";")
    id = metrics[0]
    port = 4000
    print("Recebi a mensagem ::",metrics)
    send_timeStamp = time.time()
    rcv_timeStamp = float(metrics[1])
    steps = int(metrics[2])
    probe_round = int(metrics[3])

    packet = monitoring.make_probe(id,rcv_timeStamp,steps+1,probe_round) # fazer a nova probe
    for n in neighbours:
        if n != address[0] and steps < PACKET_TTL:
            s.sendto(packet,(n,port))
   
    incoming_delay = (send_timeStamp - rcv_timeStamp) * 1e3

    lock.acquire()

    if id in monitoring_rec:
        server_monitoring = monitoring_rec[id]
        old_delay = server_monitoring['delay']
        alpha = 0.1
        delay = alpha*old_delay + (1-alpha)*incoming_delay

        if monitoring_rec[id]['probe_round'] < probe_round:
            monitoring_rec[id]['delay'] = delay
            monitoring_rec[id]['steps'] = steps+1
            monitoring_rec[id]['ip'] = address[0]
            monitoring_rec[id]['probe_round'] = probe_round
            print(f"Server Record {id} Atualizado:: delay:{delay}, steps:{steps+1}, ip:{address[0]}")
    else:
        monitoring_rec[id] = {}
        monitoring_rec[id]['delay'] = incoming_delay
        monitoring_rec[id]['steps'] = steps+1
        monitoring_rec[id]['probe_round'] = probe_round
        monitoring_rec[id]['ip'] = address[0]
        print(f"Server Record {id} Criado:: delay:{incoming_delay}, steps:{steps+1}, ip:{address[0]}")
    
    lock.release()

    changed = min_delay() # atualizar qual é o servidor com menor delay neste momento

    if changed:
        request_new_server()

    


# Serviço que está sempre em execução à escuta de pacotes de monitorização na porta 4000. Estes pacotes quando são recebidos são encaminhados para
# uma thread que é criada com o propósito de processar o pacote

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


# Função que permite fazer o reenvio do vídeo para os vizinhos cujas interfaces estejam ativas
# Para o poder fazer, recorre à estrutura "interface_status"

def difusion_processing(s,msg,add): #controlled flooding

    incoming_ip = add[0]
    delays = []

    lock.acquire()

    for id in monitoring_rec:
        delays.append((monitoring_rec[id]['ip'], monitoring_rec[id]['delay'])) # colecionar todos os pares (ip, delay) dos vizinhos deste nodo

    if incoming_ip == monitoring_rec[incoming_server]['ip']: # só envia o vídeo se o ip do qual veio o vídeo for a interface com menor delay
        print(f'\n\nVideo incoming from: {incoming_ip}\n\n')
        for (ip,status) in interface_status.items():
            if ip != add[0] and status:
                s.sendto(msg,(ip,6000))

    lock.release()

    

# Serviço que se encontra sempre disponível na porta 6000 que trata dos pacotes de vídeo vindos de um servidor
# Mal um pacote destes é recebido, é criada uma thread que trata do reenvio do mesmo para os seus vizinhos

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