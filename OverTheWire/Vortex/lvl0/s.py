import struct
import socket

def main():
	
	host = "vortex.labs.overthewire.org"
	port = 5842

	s = socket.socket()
	s.connect((host,port))
	i1 = s.recv(1024)
	print i1
	i2 = s.recv(1024)
	print i2

	i3 = i1+i2
	i3_unpacked = struct.unpack("<4I",i3)
	print i3_unpacked
	ret = 0
	for c in i3_unpacked:
		ret = ret + c
	ret_packed = struct.pack("<I",ret)
	s.send(ret_packed)
	print s.recv(1024)
main()
