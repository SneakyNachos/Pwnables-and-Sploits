set height 0
set width 0
set disassembly-flavor intel

b* 0x40091c 
commands 1
end

b* 0x40093d
commands 2
	print "Malloc location\n"
	x/x $rax
	c
end

b* 0x4009cb
commands 3
	
end

b* 0x400a1b
command 4
	print "User Malloc location\n"
	x/20x $rax
	c
end

b* 0x400a97
commands 5
	print "MD5_UPDATE args\n"
	print "arg1\n"
	x/20x $rdi
	print "arg2\n"
	x/s $rsi
	c
end

b* 0x400a9c
commands 6
	c	
end

b* 0x400ab3
commands 7
	print "After MD5_FINAL\n"
	set $x=$rbp-0x48
	x/20x *(int*)$x
end

b* 0x400a6b
commands 8
	print "ARGS to STRCPY\n"
	print "arg1\n"
	x/20x $rdi
	print "arg2\n"
	x/s $rsi
end

b* 0x4009f7 
commands 9
	print "ARGS to MD5_INIT\n"
	set $x=$rdi
	x/20x $rdi
end

B* 0x4009fc
commands 10
	print "AFTER MD5_INIT\n"
	x/20x $x
end
