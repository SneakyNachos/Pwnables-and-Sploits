from pwn import *
def main():
	p = process(["step2.bin","W\x11\x54\xc2\x21\x48\xa7\xc0\x32\xa1\xd6\x35\x40\xb0\xdc\x3b\x0e\x6d\\x0a\x73\xf9\x73\xec\x4e\xb3\xac\x0d\x52\xb8\x24\x85\xe2\xe2"])
	print p.recvline()
	pass
main()
