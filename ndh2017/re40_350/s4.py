from pwn import *
def main():
	p = process(['gdb','step2.bin','-command','test.gdb'])
	print p.recvuntil("Well done :)")
	data = p.recvall(timeout=1)
	fp = open("step3.bin","wb")
	fp.write(data)
	fp.close()

	pass
main()
