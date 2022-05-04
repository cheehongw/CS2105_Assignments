'''
    Module: CS2105
    Semester: AY21/22 S2
    File name: Checksum.py
    Author: Wong Chee Hong
    Python Version: 3.7
'''

import zlib, sys

from pip import main

def main():
    with open (sys.argv[1], "rb") as f:
        bytes = f.read()

    checksum = zlib.crc32(bytes)
    print(checksum)


if __name__ == "__main__":
    main()