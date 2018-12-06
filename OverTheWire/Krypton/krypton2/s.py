def caesar_cipher(s,i):
	#s is string, i is the shift value
	#A = 0x41, Z = 0x5a
	ret = ""
	for c in s:
		v = chr((((ord(c) - 0x41) + i) % 26) + 0x41)
		ret = ret +  v 
	return ret
def main():
	for i in xrange(27):
		print caesar_cipher("OMQEMUEQMEK",i)
	pass

main()
