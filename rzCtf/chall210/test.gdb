set height 0
set disassembly-flavor intel

b* 0x407b00
commands 1
	set $eax = 0
	c
end

b* 0x407bdf
commands 2
end

b* 0x4084c3
commands 3

end
