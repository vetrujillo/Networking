import socket
import threading

IP = '0.0.0.0'
PORT = 9998

def main():
    #Create server variable to use IPv4 and TCP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #Passing IP addr and port that server will listen on
    server.bind((IP, PORT))
    #Server will start listening w/ max backlog of connections set to 5
    server.listen(5)
    print(f'[*] Listening on {IP}:{PORT}')

    #Server placed in main loop where it waits for incoming connection
    while True:
        #When client connects, client socket and remote connection details
        #are stored in the corresponding variables
        client, address = server.accept()
        print(f'[*] Accepted connection from {address[0]}:{address[1]}')
        #Create thread object pointing to handle_client func, with client
        # socket as an argument
        client_handler = threading.Thread(target=handle_client, args=(client,))
        #Thread is started to handle client connection, at which point main
        # server loop is ready to handle another incoming connection
        client_handler.start()

#This function performs recv() and sends a simple message back to client
def handle_client(client_socket):
    with client_socket as sock:
        request = sock.recv(1024)
        print(f'[*] Received: {request.decode("utf-8")}')

if __name__ == '__main__':
    main()
