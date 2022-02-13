from socket import *
import sys

targetServer = "137.132.92.111"
serverPort = 4444

def main():
    print('test')
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((targetServer, serverPort))
    print("connection established")
    student_key = sys.argv[1]
    handshake(student_key, clientSocket)

def handshake(student_key, clientSocket):
    message = ("STID_" + student_key).encode()
    print("sending message: ", message)
    clientSocket.send(message)
    reply = clientSocket.recv(1024)
    print("server:", reply)
    

if __name__ == "__main__":
    main()