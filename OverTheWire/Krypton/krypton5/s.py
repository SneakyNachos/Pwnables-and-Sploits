def main():
	#
	key = "FREKEY"
	ctext = "HCIKV RJOX"
	ret = ""
	i = 0
	for c in ctext:
		if c == " ":
			ret = ret + " "
		else:
			p = ((ord(c) - 0x41) + (ord(key[i % len(key)]) - 0x41) % 27) + 0x41
			ret = ret + chr(p) 
	print ret
	pass
main()
