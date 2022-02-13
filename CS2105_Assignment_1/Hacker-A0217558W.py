from http import client
from socket import *
import sys, hashlib, time

targetServer = "137.132.92.111"
serverPort = 4444
student_id = 283974
clientSocket = socket(AF_INET, SOCK_STREAM) 
password = 0

def main():
    
    if (len(sys.argv) != 2):
        print("expected 1 argument!")
        return

    #clientSocket = socket(AF_INET, SOCK_STREAM)
    start_time = time.time()
    clientSocket.connect((targetServer, serverPort))
    print("connection established")
    student_key = sys.argv[1]
    if (handshake(student_key)):
        while (password < 10000):
            try_password()

        print("--------- %s seconds ------------" % (time.time() - start_time))
    else :
        print("handshake failed")
        

def handshake(student_key):
    message = ("STID_" + student_key).encode()
    print("sending message: ", message)
    clientSocket.send(message)
    reply = clientSocket.recv(4).decode()
    print("server:", reply)
    return reply == '200_'

def try_password():
    start_time = time.time()
    for i in range(password, 10000):
        fourDigit = '{0:04}'.format(i)
        m = ('LGIN_' + fourDigit).encode()
        clientSocket.send(m)
        response = getResponseCode()
        if (response == '201_'):
            print('password is: ', fourDigit)
            file = getFile()
            print("file retrieved: ", hashlib.md5(file).hexdigest())
            send_hash(file)
            logoutFile()
            
        elif (response == '403_'):
            continue
        else:
            print("ERR: unexpected response in stage 1: ", response)
            print("ERR: curr iteration: ", i)
            password = i
            break
    print("------------- bruteforced in %s seconds--------------" % (time.time() - start_time)) 

def send_hash(file):
    hash = hashlib.md5(file).hexdigest()
    msg = ('PUT__' + hash).encode()
    clientSocket.send(msg)
    code = getResponseCode()
    if (code == '203_'):
        hashlib.md5(readLength(extractLength())).hexdigest()
    else:
        print("ERR: sent has invalid, server returned ", code)
    

def logoutFile():
    print('logging out')
    clientSocket.send('LOUT_'.encode())
    if (getResponseCode() == '202_'):
        print('server: Logout successful, now in State 1')
    else:
        print('ERR: logout failed')

def getFile():
    clientSocket.send('GET__'.encode())
    print("getting file")
    if (getResponseCode() == '100_'):
        print("server: 100_")
        length = extractLength()
        print("server: file length is", length)
        file = readLength(length)
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

    return packet

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
