import itertools
import hashlib
def main():
	alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
	hKnown = "652664be1cfc2bf7c12f2e1a4f2d84c7"
	uname_guess = "3.5.0-4-generic"
	data_ca1 = "gzPeHmq3DWjWgBq66MtZ"
	for val in itertools.permutations(alphabet,6):
		guess = ''.join(val)+uname_guess+data_ca1
		hGuess = hashlib.md5(guess).hexdigest()
		if hGuess == hKnown:
			print "Found"
			print guess
			break	
	
	pass
main()
