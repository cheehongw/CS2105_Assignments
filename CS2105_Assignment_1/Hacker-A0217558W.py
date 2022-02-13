from http import client
from socket import *
import sys

targetServer = "137.132.92.111"
serverPort = 4444
student_id = 283974
clientSocket = ''
password = 0

def main():
    
    if (len(sys.argv) != 2):
        print("expected 1 argument!")
        return

    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((targetServer, serverPort))
    print("connection established")
    student_key = sys.argv[1]
    if (handshake(student_key, clientSocket)):
        return #something
        

def handshake(student_key):
    message = ("STID_" + student_key).encode()
    print("sending message: ", message)
    clientSocket.send(message)
    reply = clientSocket.recv(4).decode()
    print("server:", reply)
    return reply == '200_'

def try_password():
    for i in range(password, 10000):
        fourDigit = '{0:04}'.format(i)
        m = ('LGIN_' + fourDigit).encode()
        clientSocket.send(m)
        response = getResponseCode()
        if (response == '201_'):
            print('password is: ', fourDigit)
            file = getFile()

        elif (response == '403_'):
            continue
        else:
            print("unexpected response in stage 1:", response)

def getFile():
    clientSocket.send('GET__'.encode())
    print("getting file")
    if (getResponseCode() == '100_'):
        print("server: 100_")
        length = extractLength()
        print("server: file length is", length)
        file = readLength(length)
        print("file retrieved")
        return file
    else:
        return

def readLength(length):
    packetSize = length
    packet = b''
    while (packetSize > 0):
        msg = clientSocket.recv(length)
        packetSize = packetSize - len(msg)
        packet = packet + msg

    return packet.decode()

def extractLength():
    buffer = b''
    while (True):
        msgByte = clientSocket.recv(1)
        if (msgByte == b'_'):
            break
        buffer = buffer + msgByte
    
    return int(buffer.decode())
        


def getResponseCode():
    m = clientSocket.recv(4)
    if len(m) != 4:
        print('RESPONSE_CODE not length 4')
    
    return m.decode()

if __name__ == "__main__":
    main()
    #try_password()