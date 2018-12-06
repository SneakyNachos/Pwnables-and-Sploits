set disassembly-flavor intel
set height 0
set width 0

b* main
commands 1
    c
end

b* Print_Shdrs+87
commands 2
end

r test.txt
