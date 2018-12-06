from z3 import *
def get_models(F):
	"""
		get_models : Takes an array of z3 arguments to test whether or not there is a solution to the problem
	"""
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
def swap32(val):
	"""
		swap32 : The equivalent of x86 bswap
	"""
	return (((val<<24) & 0xff000000)|
		((val<< 8) & 0x00ff0000)|
		((val>> 8) & 0x0000ff00)|
		((val>>24) & 0x000000ff))
	
def verify(x,y,cl,target):
	"""
		verify: A replica of the algorithm used to calculate the necessary character per character check
	"""
	#xor rsi,rsi
	rsi = 0

	#mov sil, byte x
	rsi = rsi | x

	#shl rsi,0xe
	rsi = rsi << 0xe

	#neg esi
	esi = rsi & 0x00000000ffffffff
	esi = (~esi % 0x100000000)+1
	rsi = esi

	#add si, word ptr [rax+rdi*1] : This just seems to be the current character plus the next one over
	si = rsi & 0x000000000000ffff
	si = (si + y) % 0x10000
	rsi = rsi & 0xffffffffffff0000
	rsi = rsi | si
	
	#bswap esi
	rsi = swap32(rsi)
	
	#shl rsi, 0x9
	rsi = rsi << 0x9
	
	#add sil, cl
	sil = rsi & 0x00000000000000ff
	sil = (sil + cl) % 0x100
	rsi = rsi & 0xffffffffffffff00
	rsi = rsi | sil
	
	#mov dword ptr [rdx+r12*1], esi
	rsi = rsi & 0x00000000ffffffff
	
	
	return (rsi == target)

def xcheck(x):
	#z3 test that the byte argument "x" is within ascii range
	return And(x <= 0x7f,x>=0x0)

def ycheck(y):
	#z3 test that the word argument "y" has both low and high bytes within ascii range
	return And(y <= 0x7f7f,y>=0x0000)

def xycheck(x,y):
	#z3 test that the word argument "y"'s lower byte consists of the byte argument "x"
	z = y & 0x00ff
	return z == x
def backcheck(x,yprev):

	#z3 check and see if the previous word argument "y"'s higher byte consts of the current argument "x"
	check = yprev & 0xff00
	check = check >> 8
	return (x == check)

def calcNeededValue(x,y,z):
	#Calculates the required value to make it so that at each character check the value will be zero and continue the loop.
	return (((y^z) + x) % 0x100000000)

def main():
	
	#Instantiate all the Bit Vectors
	x,y = BitVecs("b1 w1",32)
	x1,y1 = BitVecs("b2 w2",32)
	x2,y2 = BitVecs("b3 w3",32)
	x3,y3 = BitVecs("b4 w4",32)
	x4,y4 = BitVecs("b5 w5",32)
	x5,y5 = BitVecs("b6 w6",32)
	x6,y6 = BitVecs("b7 w7",32)
	x7,y7 = BitVecs("b8 w8",32)
	x8,y8 = BitVecs("b9 w9",32)
	x9,y9 = BitVecs("b10 w10",32)
	x10,y10 = BitVecs("b11 w11",32)
	x11,y11 = BitVecs("b12 w12",32)
	x12,y12 = BitVecs("b13 w13",32)
	x13,y13 = BitVecs("b14 w14",32)
	x14,y14 = BitVecs("b15 w15",32)
	x15,y15 = BitVecs("b16 w16",32)

	print "-"*15

	#Setup all the z3 checks	
	F = [
		#First character/Second char
		xcheck(x),
		ycheck(y),
		xycheck(x,y),
		verify(x,y,16,0x91c7fe10), 

		#Second character/Third char
		xcheck(x1),
		ycheck(y1),
		xycheck(x1,y1),
		backcheck(x1,y),
		verify(x1,y1,15,0x63ddfe0f), 

		#Third char/4th char
		xcheck(x2),
		ycheck(y2),
		xycheck(x2,y2),
		backcheck(x2,y1),
		verify(x2,y2,14,calcNeededValue(0x11ae9151,0x3e1ba44a,0x6822c8f7)),

		#4th/5th char
		xcheck(x3),
		ycheck(y3),
		xycheck(x3,y3),
		backcheck(x3,y2),
		verify(x3,y3,13,calcNeededValue(0x12d43a8c,0xe5d2e1ea,0x2d21226b)),

		#5th/6th char
		xcheck(x4),
		ycheck(y4),
		xycheck(x4,y4),
		backcheck(x4,y3),
		verify(x4,y4,12,calcNeededValue(0x11ab27a8,0x319bafec,0x33a57988)),

		#6th/7th char
		xcheck(x5),
		ycheck(y5),
		xycheck(x5,y5),
		backcheck(x5,y4),
		verify(x5,y5,11,calcNeededValue(0x1bea2566,0x7e2222b7,0xb1d3fa12)),

		#7th/8th char
		xcheck(x6),
		ycheck(y6),
		xycheck(x6,y6),
		backcheck(x6,y5),
		verify(x6,y6,10,calcNeededValue(0x1d1331c8,0xc5936280,0xe741aec2)),

		#8th/9th char
		xcheck(x7),
		ycheck(y7),
		xycheck(x7,y7),
		backcheck(x7,y6),
		verify(x7,y7,9,calcNeededValue(0x1f30813e,0xf89f95e3,0xf03ee928)),

		#9th/10th char
		xcheck(x8),
		ycheck(y8),
		xycheck(x8,y8),
		backcheck(x8,y7),
		verify(x8,y8,8,calcNeededValue(0x18f05025,0x398b0954,0xf16ca4b7)),

		#10th/11th char
		xcheck(x9),
		ycheck(y9),
		xycheck(x9,y9),
		backcheck(x9,y8),
		verify(x9,y9,7,calcNeededValue(0x13d099c3,0x2f13adb2,0x650ac9f6)),

		#11th/12th char
		xcheck(x10),
		ycheck(y10),
		xycheck(x10,y10),
		backcheck(x10,y9),
		verify(x10,y10,6,calcNeededValue(0x15952b84,0xe040b7eb,0x68146569)),

		#12th/13th char
		xcheck(x11),
		ycheck(y11),
		xycheck(x11,y11),
		backcheck(x11,y10),
		verify(x11,y11,5,calcNeededValue(0x12cfe44c,0x9f3e19a0,0xc8340019)),
		
		#13th/14th char
		xcheck(x12),
		ycheck(y12),
		xycheck(x12,y12),
		backcheck(x12,y11),
		verify(x12,y12,4,calcNeededValue(0x1510f74d,0xd5e62512,0x833123a5)),

		#14th/15th char
		xcheck(x13),
		ycheck(y13),
		xycheck(x13,y13),
		backcheck(x13,y12),
		verify(x13,y13,3,calcNeededValue(0x1a779885,0x31ebb46a,0x7e85d114)),

		#15th/16th char
		xcheck(x14),
		ycheck(y14),
		xycheck(x14,y14),
		backcheck(x14,y13),
		verify(x14,y14,2,calcNeededValue(0x1f411bf2,0x65c92edf,0xf14fcccf)),
	
		#16th char
		xcheck(x15),
		ycheck(y15),
		xycheck(x15,y15),
		backcheck(x15,y14),
		verify(x15,y15,1,calcNeededValue(0x20f0dd5d,0xa00dcbf7,0xd4eeeb53))
		
	]
	
	
	for x in get_models(F):
		print(x)
	
	
	pass
main()
