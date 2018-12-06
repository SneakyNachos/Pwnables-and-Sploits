set height 0
set disassembly-flavor intel

b* 0x8048fcc
commands 1
c
end

b* 0x8048fe2
commands 2
c
end

b* 0x8048f8e
commands 3
end

r < test.txt
