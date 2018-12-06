from pwn import *
import itertools
def main():
	for i in itertools.permutations([7,4,5,7,8,8,6,5]):
		p = process("./Youre_Not_Welcome")
		p.recvuntil("Password:")
		s = "".join(map(str,i))
		p.sendline(s)
		data = p.recvall()
		if "Access Denied" not in data:
			print i
			break
		p.kill()
	pass
main()
