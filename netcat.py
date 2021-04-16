import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading

def execute(cmd):
    """Receives a command, runs it, returns output as string"""
    cmd = cmd.strip()
    if not cmd:
        return
    #check_output() runs command on local operating system and returns
    #output from that command
    output = subprocess.check_output(shlex.split(cmd),
                                    stderr=subprocess.STDOUT)
    return output.decode()

class NetCat:
    def __init__(self, args, buffer=None):
        '''Initialize NetCat object with arguments from cmd line and buffer'''
        self.args = args
        self.buffer = buffer
        #Create socket object
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    #Entry point for managing NetCat objet, delegates execution to 2 methods
    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()

    def send(self):
        #Connect to target and port, and send buffer if one is specified
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)

        #Allows us to manually close connection with CTRL-C
        try:
            #Begin loop to receive data from target. If no data, break loop
            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break
                #If data received, print response, pause to get interactive input
                # send that input, continue loop    
                if response:
                    print(response)
                    buffer = input('> ')
                    buffer += '\n'
                    self.socket.send(buffer.encode())
        #Loop will continue until KeyboardInterrupt            
        except KeyboardInterrupt:
            print('User terminated.')
            self.socket.close()
            sys.exit()    

    def listen(self):
        #Binds to target/port
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        #Starts listening in a loop
        while True:
            client_socket, _ = self.socket.accept()
            #Passes connected socket to handle method
            client_thread = threading.Thread(
                target=self.handle, args=(client_socket,)
            )
            client_thread.start()

    def handle(self, client_socket):
        '''Executes task corresponding to cmd line arg received'''
        #If cmd should be executed, this method passes command to execute 
        # function and sends output back on socket
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())
        
        #If file is uploaded, a loop is set to listen for content on listening
        # socket and recv data until it stops
        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break
            
            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)
            message = f'Saved file {self.args.upload}'
            client_socket.send(message.encode())

        #If a shell is to be created, loop is set up, a prompt is sent to
        # sender, and code is set to wait for a cmd string to come back
        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'BHP: #> ')
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'server killed {e}')
                    self.socket.close()
                    sys.exit()

if __name__ == '__main__':
    #argparse used to create cmd interface
    parser = argparse.ArgumentParser(
        description = 'BHP Net Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        #Example usage displayed when user invokes --help
        epilog=textwrap.dedent('''Example:
            netcat.py -t 192.168.1.108 -p 5555 -l -c # command shell
            netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt # upload to file
            netcat.py -t 192.168.1.108 -p 5555 -l -e=\"cat /etc/passwd\" # execute command
            echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135 # echo text server port 135
            netcat.py -t 192.168.1.108 -p 5555 # connect to server
            '''))
    #Sets up interactive shell        
    parser.add_argument('-c', '--command', action='store_true', help='command shell')
    #Executes one specific command
    parser.add_argument('-e', '--execute', help='execute specified command')
    #Indicates a listener should be set up
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    #Specifies port on which to communicate
    parser.add_argument('-p', '--port', type=int, default=5555, help='specified port')
    #Specifies target IP
    parser.add_argument('-t', '--target', default='192.168.1.203', help='specified IP')
    #Specifies name of file to upload
    parser.add_argument('-u', '--upload', help='upload file')
    args = parser.parse_args()
    #If a listener is set up, NetCat object is invoked with empty buffer string
    if args.listen:
        buffer = ''
    #Otherwise, buffer is sent content from stdin    
    else:
        buffer = sys.stdin.read()

    nc = NetCat(args, buffer.encode())
    nc.run()
