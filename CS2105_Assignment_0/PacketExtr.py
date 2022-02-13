import sys

def main():
    flag = True
    while (flag):
        packet_size = get_packet_size()
        if (packet_size < 0):
            flag = False
            break

        while (packet_size > 0):
            data = sys.stdin.buffer.read1(packet_size)
            packet_size = packet_size - len(data)
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()

def get_packet_size():
    flag = True
    byte_array = bytearray()
    while(flag):
        data = sys.stdin.buffer.read(1)
        
        if (data == b"B"): #end of header
            flag = False
        elif (len(data) == 0): #EOF reached
            return -1
        else:
            byte_array += bytearray(data)
    
    header = bytes(byte_array).decode()
    packet_size = int(header.split()[1])
    return packet_size

if __name__ == "__main__":
    main()
