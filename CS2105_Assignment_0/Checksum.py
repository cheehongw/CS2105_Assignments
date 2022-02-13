from tabnanny import check
import zlib, sys

from pip import main

def main():
    with open (sys.argv[1], "rb") as f:
        bytes = f.read()

    checksum = zlib.crc32(bytes)
    print(checksum)


if __name__ == "__main__":
    main()