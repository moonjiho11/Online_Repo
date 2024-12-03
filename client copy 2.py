import socket
client = socket.socket()
client.connect(('0.0.0.0',6543)) #127.0.0.1 = 내 컴퓨터
client.send('hello')
print(client.recv(1024))