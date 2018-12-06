set height 0
set width 0
set disassembly-flavor intel

b* main
commands 1
end

b* unsafecode+31
commands 2
    printf "printf now:\n"
    x/x 0x804a00c
end

r $(cat test.txt)
