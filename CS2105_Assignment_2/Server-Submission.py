'''
    Module: CS2105
    Semester: AY21/22 S2
    File name: Server-Submission.py
    Author: Wong Chee Hong
    Python Version: 3.7
'''

from socket import *
import sys, hashlib, time, struct, os, zlib

def main():

    if (len(sys.argv) != 6):
        print("expected 5 arguments!")
        return -1

    student_key = sys.argv[1]
    mode = int(sys.argv[2])
    ip_address = sys.argv[3]
    port_num = int(sys.argv[4])
    file_name = sys.argv[5]

    connect_to_simulator(student_key, mode, ip_address, port_num, file_name)


def connect_to_simulator(student_key, mode, ip_address, port, file_name):
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.connect((ip_address, port))
    handshake_message = ("STID_" + student_key + "_S").encode()
    serverSocket.send(handshake_message)
    print("SERVER: ", handshake_message)
    reply = 99
    while (reply != 0):
        print("Server: Listening to queue num")
        reply = extractQueueNum(serverSocket)
        print("Server queue num:", reply)

    
    if (mode == 0):
        send_file_0(serverSocket, file_name)
    elif (mode == 1):
        send_file_1(serverSocket, file_name)
    elif (mode == 2):
        send_file_2(serverSocket, file_name)
    else:
        raise Exception("FATAL ERROR - UNKNOWN MODE")

def send_file_0(serverSocket, file_name):
    filesize = os.path.getsize(file_name)
    print("SERVER: Expecting to send " + str(filesize) + " bytes")
    f = open(file_name, "rb")
    last_seq_num = -(filesize // -1016)
    count = 0
    while (filesize > 0):
        count += 1
        islastPacket = count == last_seq_num
        payload = f.read(1016)
        filesize -= len(payload)
        packet = append_header_0(payload, islastPacket, len(payload))
        serverSocket.sendall(packet)
    
    print("Server: Finished sending file")
    f.close()
    serverSocket.close()


def append_header_0(payload, islastPacket, packetSize):
    length_header = struct.pack("?I", islastPacket, packetSize)
    return pad_to_n(length_header + payload, 1024)

def send_file_1(serverSocket, file_name):
    filesize = os.path.getsize(file_name)
    last_seq_num = -(filesize // -1000)
    print("Server: last seq num: ", last_seq_num)

    f = open(file_name, "rb")
    seq_num = 1
    d = {}
    while (filesize > 0 or d):

        if(len(d) < 1000):
            payload = f.read(1000)
            filesize -= len(payload) #something wrong
            packet = append_header_1(payload, seq_num, last_seq_num)
            d[seq_num] = packet
            serverSocket.sendall(packet)
            seq_num += 1
        
        if (len(d) >= 1000):
            result = recv_ack(serverSocket, seq_num)
            if (result == last_seq_num + 1):
                break

            for k in list(d):
                if (k < result and result != -1):
                    d.pop(k)
                else:
                    serverSocket.sendall(d[k])
        
        #print(filesize, len(d))
    
    serverSocket.close()
    f.close()


def recv_ack(serverSocket, seq_num):
    packet = readLength(64, serverSocket)
    checksum, payload = packet[:4], packet[4:]
    if (zlib.crc32(payload) == struct.unpack("I",checksum)[0]):
        return struct.unpack("Q", payload[:8])[0]
    else:
        return -1
    



def append_header_1(payload, seq_num, last_seq_num): #20 bytes header + 4 bytes CRC checksum
    header = struct.pack("QQi", seq_num, last_seq_num, len(payload))
    assert len(header) == 20
    packet = header + payload
    padded = pad_to_n(packet, 1020)
    assert len(padded) == 1020
    checksum = struct.pack("I",zlib.crc32(padded))
    return checksum + padded


def send_file_2(serverSocket, file_name):
    filesize = os.path.getsize(file_name)
    last_seq_num = -(filesize // -1004)

    f = open(file_name, "rb")
    seq_num = 1
    while (filesize > 0):
        payload = f.read(1004)
        filesize -= len(payload)
        packet = append_header_2(payload, seq_num, last_seq_num)
        serverSocket.sendall(packet)
        seq_num += 1
        if (seq_num % 1500 == 0):
            time.sleep(0.08)

    f.close()
    print("Server: Finished sending file")
    serverSocket.close()


def append_header_2(payload, seq_num, last_seq_num): #20 bytes header
    header = struct.pack("QQi", seq_num, last_seq_num, len(payload))
    assert len(header) == 20
    packet = header + payload
    return pad_to_n(packet, 1024)

    
def pad_to_n(packet, n):
    size = len(packet)
    extra_padding = (n - size % n) % n
    new_packet = packet + (b'c' * extra_padding)
    assert len(new_packet) % n == 0, "FATAL ERROR - packet size not multiple of " + str(n) + " bytes!"
    return new_packet

def extractQueueNum(serverSocket):
    buffer = b''
    while (True):
        msgByte = serverSocket.recv(1)
        if (msgByte == b'_'):
            break
        buffer = buffer + msgByte
    
    return int(buffer.decode())

def readLength(length, serverSocket):
    packetSize = length
    packet = b''
    while (packetSize > 0):
        msg = serverSocket.recv(packetSize)
        packetSize = packetSize - len(msg)
        packet = packet + msg
    
    assert len(packet) == length, len(packet)

    return packet


if __name__ == "__main__":
    main()