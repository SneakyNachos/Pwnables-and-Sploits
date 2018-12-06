set height 0
set disassembly-flavor intel
set logging on
set logging file what.log

b* 0x400881
commands 1
	set $pc = 0x4008dd
	c
end

b* 0x4007c9
commands 2
	set $pc = 0x400843
	c
end


b* 0x4008d8
commands 3 
	c
end

b* 0x4008eb
commands 4
	set {int}0x634021 = 0xf9730a6d
	set {int}0x63402d = 0xe2e28524
	c
end

b* 0x400856
commands 5
	c
end


r `echo -ne 'W\x11\x54\xc2\x21\x48\xa7\xc0\x32\xa1\xd6\x35\x40\xb0\xdc\x3b\x0e\x6d\x0b\x73\xf9\x73\xec\x4e\xb3\xac\x0d\x52\xb8\x24\x85\xe2'`
