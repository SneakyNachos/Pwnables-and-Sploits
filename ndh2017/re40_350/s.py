from pwn import *
def main():
	p = process(['step1.bin','!!!aLal4rT'])
	print p.recvline()
	data = p.recvall()
	fp = open("output.bin","wb")
	fp.write(data)
	fp.close()
	pass
main()
