import pickle
import socket
import threading

HOST = "127.0.0.1"
PORT = 9090

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((HOST, PORT))

server.listen()

clients = []

nicknames = []


def update_online(new_online, action):
    obj = {
        'online': new_online,
        'action': action
    }

    data = pickle.dumps(obj)
    for client in clients:
        client.sendall(data)


def broadcast_info(message):
    obj = {
        'message': message,
        'foreground': "sms"
    }
    data = pickle.dumps(obj)
    for client in clients:
        client.send(data)


def broadcast_message(message):
    if message['send_to'] == 'All':
        obj = {
            'message': f"{message['from']}: {message['message']}\n",
            'foreground': 'sms'
        }
        data = pickle.dumps(obj)

        for client in clients:
            client.sendall(data)
    else:
        obj = {
            'message': f"(private){message['from']}->{message['send_to']}: {message['message']}\n",
            'foreground': "sms"
        }
        data = pickle.dumps(obj)
        sends = [clients[nicknames.index(message['from'])], clients[nicknames.index(message['send_to'])]]
        for s in sends:
            s.sendall(data)


def handle(client):
    while True:
        try:
            message = pickle.loads(client.recv(4096))
            broadcast_message(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            broadcast_info(f"{nickname} left chat\n")
            update_online(nickname, "del")
            break


def receive():
    while True:
        client, address = server.accept()
        ask = pickle.dumps({'ask': 'Nickname'})
        client.send(ask)
        nickname = client.recv(4096).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client)
        obj = {
            'ask_online': nicknames
        }
        data = pickle.dumps(obj)
        client.sendall(data)
        broadcast_info(f"{nickname} joined chat\n")
        update_online(nickname, "add")
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


print("Start")
receive()
