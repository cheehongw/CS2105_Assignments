from http import client
from socket import *
import sys

targetServer = "137.132.92.111"
serverPort = 4444

def main():
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((targetServer, serverPort))
    studentId = sys.argv[1]
    clientSocket.send()



if __name__ == "main":
    main()