set height 0
set width 0
set disassembly-flavor intel
set follow-fork-mode child
b* main
commands 1
end

b* main+160
commands 2
end

b* unsafecode+31
commands 3
end

r $(cat test.txt)
