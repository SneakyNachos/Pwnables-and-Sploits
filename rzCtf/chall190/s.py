import urllib
def main():
	"""
	0x10 - op_PRINT
	0x11 - op_size - op_PUSH
	0x12 - op_POP
	0x13 - op_ADD
	0x14 - op_SUB
	0x15 - op_XCHG
	0x16 - op_CLEAR
	0x17 - op_DEBUG
	0x18 - op_JUMP - not implemented?
	0x19 - op_PUT
	0x20 - op_MOVE
	registers
	f0
	f1
	f2
	f3
	"""
	data1 = "\x11 EM EVIG"
	data2 = "\x11GALF EHT"
	data3 = "\x11!ESAELP "
	with open("test.txt","wb") as fp:
		fp.write(data1+"\n")
		fp.write(data2+"\n")
		fp.write(data3+"\n")
		fp.write("\x17"+"\n")
		fp.write("\x13\xf3\xf0"+"\n")
		fp.write("\x17"+"\n")
		fp.write("\x10"+"\n")
	with open("test.txt","rb") as fp:
		lines = fp.read()
		print urllib.quote(lines)
main()
