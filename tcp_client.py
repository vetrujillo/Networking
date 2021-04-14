import socket

target_host = "www.google.com"
target_port = 80

#Create socket object
#AF_INET indicates use of standard IPv4 addr or hostname
#SOCK_STREAM indicates client will be TCP
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Connect client
client.connect((target_host,target_port))

#Send data as bytes
client.send(b"GET / HTTP/1.1\r\nHost: google.com\r\n\r\n")

#Receive data
response = client.recv(4096)

print(response.decode())
client.close()