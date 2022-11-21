import time



def make_probe(server_id, timeStamp, n_steps):
    packet : bytes
    message = ""
    message = f'{server_id};{timeStamp};{n_steps}'
    print(message)
    return message.encode('utf-8')

