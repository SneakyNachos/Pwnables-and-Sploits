set follow-fork-mode child
set disassembly-flavor intel

b* main
commands 1
 c
end
b* main+39
commands 2
 c
end
b* main+47
commands 3
 x/i $pc
 x/s $eax
end
