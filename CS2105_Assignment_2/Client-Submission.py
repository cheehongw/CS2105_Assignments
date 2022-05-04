'''
    Module: CS2105
    Semester: AY21/22 S2
    File name: Client-Submission.py
    Author: Wong Chee Hong
    Python Version: 3.7
'''

from socket import *
import os, sys, hashlib, time, struct, zlib

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
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((ip_address, port))
    handshake_message = ("STID_" + student_key + "_C").encode()
    clientSocket.send(handshake_message)
    print("CLIENT: ", handshake_message)
    reply = 99
    while (reply != 0):
        print("Client: Listening to queue num")
        reply = extractNumFromBuffer(clientSocket)
        print("Client queue num:", reply)

    print("Client: Beginning!")
    if (mode == 0):
        recv_file_0(clientSocket, file_name)
    elif (mode == 1):
        recv_file_1(clientSocket, file_name)
    elif (mode == 2):
        recv_file_2(clientSocket, file_name)
    else:
        raise Exception("FATAL ERROR - UNKNOWN MODE")


def recv_file_0(clientSocket, file_name):
    f = open(file_name, "ab+")

    while (True):
        header = readLength(8, clientSocket)
        islastPacket, payload_size = struct.unpack("?I", header)
        payload = readLength(1016, clientSocket)
        f.write(payload[:payload_size])
        if (islastPacket):
            break

    #f.seek(0)
    #print("Client hash: " + hashlib.md5(f.read()).hexdigest())
    f.close()
    clientSocket.close()

def recv_file_1(clientSocket, file_name):
    print("Client: receiving file")
    f = open(file_name, "ab+")
    d = {}
    count = 0
    next_expected_seq_num = 1
    last_seq = -1
    packets_recv = 0

    while (True):
        if (packets_recv < 1000): #keep reading the next 100 packets
            packets_recv += 1
            checksum = readLength(4, clientSocket)
            rest = readLength(1020, clientSocket)

            if (struct.unpack("I", checksum)[0] == zlib.crc32(rest)):
                count += 1 #record receipt of well-formed packet
                header, payload = rest[:20], rest[20:]
                seq_num, last_seq_num, payload_size = struct.unpack("QQi", header)
                #print("Client: ", seq_num, last_seq_num, payload_size)
                if (last_seq == -1): #to get last_seq_num
                    last_seq = last_seq_num
                if (seq_num >= next_expected_seq_num and seq_num <= last_seq):
                    d[seq_num] = payload[:payload_size] #buffer packet
            else :
                pass #ignore corrupt packet
        else:
            while (next_expected_seq_num in d):
                payload = d.pop(next_expected_seq_num)
                f.write(payload)
                next_expected_seq_num += 1
            
            packets_recv = 0
            #print("Client: next expected seq num: ", next_expected_seq_num)
            send_ack(clientSocket, next_expected_seq_num)
            if (next_expected_seq_num == last_seq + 1):
                for i in range(20):
                    send_ack(clientSocket, next_expected_seq_num)
                break

    f.close()
    clientSocket.close()


def send_ack(clientSocket, seq_num):
    header = struct.pack("Q", seq_num)
    padded = pad_to_n(header, 60)
    checksum = struct.pack("I", zlib.crc32(padded))
    clientSocket.sendall(checksum + padded)


def recv_file_2(clientSocket, file_name):
    d = {}
    f = open(file_name, "ab+")
    count = 0
    next_expected_seq_num = 1
    largest_len = len(d)

    while (True):
        count += 1
        header = readLength(20, clientSocket)
        seq_num, last_seq_num, payload_size = struct.unpack("QQi", header)
        payload = readLength(payload_size, clientSocket)
        padding = readLength(1004 - payload_size, clientSocket)
        d[seq_num] = payload
        largest_len = len(d) if len(d) > largest_len else largest_len
        if (next_expected_seq_num == seq_num):
            while (next_expected_seq_num in d):
                payload = d.pop(next_expected_seq_num)
                f.write(payload)
                next_expected_seq_num += 1

        if (count == last_seq_num):
            break

    print("Client: largest length: ", largest_len)
    f.close()
    clientSocket.close()

def pad_to_n(packet, n):
    size = len(packet)
    extra_padding = (n - size % n) % n
    new_packet = packet + (b'c' * extra_padding)
    assert len(new_packet) % n == 0, "FATAL ERROR - packet size not multiple of " + str(n) + " bytes!"
    return new_packet

def readLength(length, clientSocket):
    packetSize = length
    packet = b''
    while (packetSize > 0):
        msg = clientSocket.recv(packetSize)
        packetSize = packetSize - len(msg)
        packet = packet + msg
    
    assert len(packet) == length, len(packet)

    return packet

def extractNumFromBuffer(clientSocket):
    buffer = b''
    while (True):
        msgByte = clientSocket.recv(1)
        if (msgByte == b'_'):
            break
        buffer = buffer + msgByte
    
    return int(buffer.decode())

def extractNum(packet):
    buffer = b''
    while (True):
        msgByte = packet[:1]
        packet = packet[1:]
        if (msgByte == b'_'):
            break
        buffer = buffer + msgByte
    
    return int(buffer.decode()), packet

if __name__ == "__main__":
    main()
