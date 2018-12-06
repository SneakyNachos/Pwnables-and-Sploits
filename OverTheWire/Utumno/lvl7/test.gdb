set disassembly-flavor intel
set height 0
set follow-fork-mode child


b* main
commands 1
    x/i $pc
    c
end

r
