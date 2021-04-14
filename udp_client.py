import socket

target_host = "127.0.0.1"
target_port = 9997

#Create socket object
#Client will use IPv4 and will operate with UDP
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#Send data
#Because UDP is connectionless, there is no need to connect()
# prior to sending data
client.sendto(b"AAABBBCCC", (target_host, target_port))

#Receive data
data, addr = client.recvfrom(4096)

print(data.decode())
client.close()