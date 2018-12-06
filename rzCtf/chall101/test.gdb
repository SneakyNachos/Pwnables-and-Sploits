set width 0
set height 0
set disassembly-flavor intel

b* rz_function
commands 1
end

b* rz_function+12
commands 2
	set $pc = rz_function+21
end

r
call rz_function()
