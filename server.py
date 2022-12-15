import socket
import threading
import time
import json
import sys
import monitoring
import Servidor
difusion_node = "10.0.5.1"
CONFIG_FILE = "config_topologia_teste_2.json"
id = ""
neighbours = []
probe_round = 0
video_streaming = True


# Função que permite que o servidor conheça o seu nodo de acesso

def get_neighbours():
    f = open("config_topologia_teste_2.json")
    n = json.load(f)
    global neighbours
    neighbours = n['servers'][id]
    print("Server neighbours", neighbours)


# Função responsável por processar o pedido de vídeo
# Ao receber um pedido de stream, este irá criar uma instância da classe Servidor que irá receber o nome do vídeo a codificar e o IP do nodo de acesso
# e vai iniciar a codificação do vídeo e envio dos pacotes RTP para o nodo de acesso, podendo este percorrer a rede até aos clientes interessados

def request_video_processing(s : socket, msg : bytes, add : tuple):
    print("RECEBI UM PEDIDO", msg)
    server = Servidor.Servidor(msg.decode('utf-8').split(";")[0], neighbours[0])
    server.main()


# Serviço que está sempre a correr até chegar ao servidor um pedido da stream
# Quando este chega, é então criada uma thread que irá tratar deste pedido.

def request_video_service():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    port = 5000
    s.bind(('', port))
    print(f"Estou à escuta na porta: {port}")

    #while True:
    msg, add = s.recvfrom(1024)
    video_streaming = False
    threading.Thread(target=request_video_processing,args=(s,msg,add)).start()
    
    s.close()

# Função que tem como objetivo processar um pedido de bootstrapping, ou seja, um pedido dos vizinhos que um nodo faz ao servidor
# Perante um pedido destes, o cliente irá ler o ficheiro de configuração da topologia da rede, identificar o IP que lhe enviou o pedido
# e irá enviar uma resposta com a lista de vizinhos desse nodo

def bootstrap_processing(s : socket, msg : bytes, address : tuple):
    print(address[0],address[1])
    neighbours = send_neighbours(address[0]) #lista de vizinhos
    print("TTL:", neighbours[1])
    message = " ".join(neighbours[0])
    message += ";"
    message += str(neighbours[1])
    print(message)
    s.sendto(message.encode('utf-8'), address)  

# Função responsável por extrair do ficheiro de configuração a lista de vizinhos de um dado IP

def send_neighbours(ip):
    f = open(CONFIG_FILE)
    neighbours = json.load(f)
    response = (neighbours['nodes'][ip], neighbours['TTL'])
    print("Neighbours: ", neighbours['nodes'][ip])
    return response


# Serviço que se encontra em execução continuamente na porta 2000 e que irá receber os pedidos que conhecimento dos vizinhos de cada nodo.
# Recebendo um pedido destes, de modo a que este não fique indisponível durante muito tempo, lançará uma thread que será responsável por fazer o processamento
# e envio da resposta do mesmo.

def bootstrap_service():
    s : socket.socket
    port : int
    msg : bytes
    add : tuple

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    port = 2000

    s.bind(('', port))

    print(f"Estou à escuta na porta: {port}")

    while True:
        msg, add = s.recvfrom(1024)
        print("recebi pedido de neighbours")
        threading.Thread(target=bootstrap_processing, args=(s, msg, add)).start()

    s.close()


# Serviço que se encontra em execução contínua a fazer o envio de pacotes de prova para a rede, de forma periódica.

def send_probe_service():
    port = 4000
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.bind(('',port))
    global probe_round
    while True:
        packet = monitoring.make_probe(id, time.time(),0, probe_round)
        for n in neighbours:
            print(f"A enviar probes para: {n}:{port}")
            s.sendto(packet,(n,port))
        time.sleep(20)
        probe_round += 1
        


def main():
    global id
    id = sys.argv[1]
    get_neighbours()
    print(neighbours)
    threading.Thread(target=bootstrap_service, args=()).start()
    threading.Thread(target=request_video_service, args=()).start()
    threading.Thread(target=send_probe_service, args=()).start()


if __name__ == '__main__':
    main()