import socket

#Example host and port, matches tcp_server.py
target_host = '0.0.0.0'
target_port = 9998

#Create socket object
#AF_INET indicates use of standard IPv4 addr or hostname
#SOCK_STREAM indicates client will be TCP
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Connect client
client.connect((target_host,target_port))

#Send data as bytes
client.send(b"Howdy")

#Receive data
response = client.recv(1024)

print(response.decode())
client.close()