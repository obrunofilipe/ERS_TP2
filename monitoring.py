import time



def make_probe(server_id, timeStamp, n_steps, probe_round):
    packet : bytes
    message = ""
    message = f'{server_id};{timeStamp};{n_steps};{probe_round}'
    print(message)
    return message.encode('utf-8')

