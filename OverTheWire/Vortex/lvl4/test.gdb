set height 0
set width 0
set disassembly-flavor intel

set follow-fork-mode child

b* main
commands 1
    c
end

b* main+38
commands 2
    x/x 0x804a014
    c
end

b* main+43
commands 3
    x/x 0x804a014
end

r
