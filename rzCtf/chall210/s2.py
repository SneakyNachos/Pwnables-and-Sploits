from miasm2.analysis.binary import Container
from miasm2.analysis.machine import Machine
from miasm2.analysis.dse import DSEEngine, DSEPathConstraint
from miasm2.expression.expression import ExprId
from miasm2.arch.x86.arch import mn_x86
from miasm2.jitter.jitload import PAGE_READ,PAGE_WRITE
from miasm2.jitter.csts import EXCEPT_INT_XX
from pwn import *
import re
regs = {}
def stop(jitter):
	jitter.run=False
	return False
	pass
def main():
	#Setup Machine
	cont = Container.from_stream(open("./Youre_Not_Welcome"))
	bin_stream = cont.bin_stream
	machine = Machine(cont.arch)
	jitter = machine.jitter(jit_type='python')
	#Memory Load, saves space
	p = process('gdb')
	print p.recvuntil('(gdb)')
	p.sendline("file Youre_Not_Welcome")
	print p.recvuntil('(gdb)')
	p.sendline("source test2.gdb")
	print p.recvuntil('(gdb)')
	p.sendline("r")
	print p.recvuntil("Password:")
	p.sendline("12345678")
	print p.recvuntil("(gdb)")
	p.sendline("i proc map")
	regions = p.recvuntil("(gdb)").split("\n")
	for index,region in enumerate(regions[4:len(regions)-1]):
		lst = re.sub(r"\s+"," ",region).split(" ")
		#print lst
		start = lst[1]
		stop = lst[2]
		dump = "%s.%s"%(index,"dmp")
		p.sendline("dump memory ./%s %s %s"%(dump,start,stop))		
		data = p.recvuntil("(gdb)")
		#print data
		if "Cannot access memory" in data:
			print "Can't access %s-%s"%(start,stop)
			pass
		else:
			with open(dump,"rb") as fp:	
				print "Adding %s"%(start)
				jitter.vm.add_memory_page(int(start,16),PAGE_READ|PAGE_WRITE,fp.read())
	p.read()#Drop extra data 
	p.sendline("i r")
	registers = p.recvuntil("(gdb)").split("\n")
	for register in registers[:len(registers)-1]:
		reg = re.sub(r"\s+"," ",register).split(" ")
		regs.update({reg[0]:int(reg[1],16)})	

	print regs
	gs_n_shit = "\x00"*500
	jitter.vm.add_memory_page(0,PAGE_READ|PAGE_WRITE,gs_n_shit)
	jitter.cpu.RAX = regs['rax']
	jitter.cpu.RBP = regs['rbp']
	jitter.cpu.RBX = regs['rbx']
	jitter.cpu.RCX = regs['rcx']
	jitter.cpu.RDI = regs['rdi']
	jitter.cpu.RDX = regs['rdx']
	jitter.cpu.RSI = regs['rsi']
	jitter.cpu.RSP = regs['rsp']
	jitter.cpu.R8 = regs['r8']
	jitter.cpu.R9 = regs['r9']
	jitter.cpu.R10 = regs['r10']
	jitter.cpu.R11 = regs['r11']
	jitter.cpu.R12 = regs['r12']
	jitter.cpu.R13 = regs['r13']
	jitter.cpu.R14 = regs['r14']
	jitter.cpu.R15 = regs['r15']
	jitter.cpu.DS = regs['ds']
	jitter.cpu.CS = regs['cs']
	jitter.cpu.SS = regs['ss']
	jitter.cpu.FS = regs['fs']
	jitter.cpu.ES = regs['es']
	jitter.cpu.GS = regs['gs']
	jitter.cpu.pf = 1
	jitter.cpu.zf = 1

	p.kill()

	jitter.init_run(0x407be4)
	dse = DSEPathConstraint(machine)
	dse.attach(jitter)
	dse.update_state_from_concrete()
	snapshot = dse.take_snapshot()
	#jitter.jit.log_regs = True
	jitter.jit.log_mn = True	
	jitter.add_breakpoint(0x407c83,stop)
	VAL = ExprId("VAL",64)

	dse.update_state({dse.ir_arch.arch.regs.RDI:VAL,})	
	
	try:
		jitter.continue_run()
	except Exception as ex:
		print ex
	print dse.eval_expr(dse.ir_arch.regs.RDI)
	print "Script Finished"	
main()
