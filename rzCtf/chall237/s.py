def main():
	with open("trivia.fun","rb") as fp:
		data = fp.read()  
		output=""
		for c in data:
			output+="\\x%s"%hex(ord(c)).replace("0x","")
		print output
main()
