from z3 import *
def z3abs(x):
	return If(x >= 0,x,-x)
def get_models(F):
    result = []
    s = Solver()
    s.add(F)
    while True:
        if s.check() == sat:
            m = s.model()
            result.append(m)
	    print m
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
def check1(input1,input2,input3):
	return input3 == -.5*input1-0.75*input2+7077.25
	
	pass
def check2(input1,input2,input3):
	return input3 == -4*input1-2*input2+10826
	pass
def check3(input1,input2,input3):
	pass
def main():
	input1 = BitVec('input1',32)
	input2 = BitVec('input2',32)
	input3 = BitVec('input3',32)
	F = [
		check1(input1,input2,input3),
		check2(input1,input2,input3),
		#check3(input1,input2,input3)
	]
	for x in get_models(F):
		print(x)
	pass
main()
