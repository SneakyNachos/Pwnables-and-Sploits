from z3 import *
def get_models(F):
    result = []
    s = Solver()
    print F
    s.add(F)
    while True:
        if s.check() == sat:
            m = s.model()
	    print m
            result.append(m)
            block = []
            for d in m:
                if d.arity() > 0:
                    raise Z3Exception("uninterpreted functions are not supported")
                c = d()
                if is_array(c) or c.sort().kind() == Z3_UNINTERPRETED_SORT:
                    raise Z3Exception("arrays and uninterpreted sorts are not supported")
                block.append(c != m[d])
            s.add(Or(block))
        else:
            return result
def abs(x):
	return If(x>=0,x,-x)
def is_range(x):
	return And((x>=32),(x<=0x7f))
def psadbw(a,b):
	r1 = Sum([abs(c1-c2) for c1,c2 in zip(a[:8],b[:8])])
	r2 = Sum([abs(c1-c2) for c1,c2 in zip(a[8:],b[8:])])
	return r1,r2
def main():
	import itertools
	import numpy
	F=[]
	chrs = [BitVec('c%s'%x,8)for x in xrange(0,16)]
	targets = [-72,19,0,-51,16,15,32,-64,-125,-32,-5,-125,-56,2,15,34]
	targets = map(lambda x: BitVec(x % 0x100,8),targets)
	for c in chrs:
		F.append(is_range(c))
	for i in xrange(8):
		a = targets
		b = list(chrs)
		b[i] = 0
		b[i+8] = 0
		h,l = psadbw(a,b)
		F.append(h == targets[i])
		F.append(l == targets[i+8])

							
	
	for x in get_models(F):
		print x	
		
	
	pass
main()
