import commands
def main():
	alphabet = "abcdefghijklmnopqrstuvwxyz1234567890"
			cmd = '%s %s %s'%("./test",str(x),str(y))
			data = commands.getstatusoutput(cmd)[1]
			if("Found Match:" in data):
				print data
main()
	
