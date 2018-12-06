set height 0
set width 0
set disassembly-flavor intel


b* main+124
commands 1
    x/20x $edx
end

r $(cat test.txt) 
