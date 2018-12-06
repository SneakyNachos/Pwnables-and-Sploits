from miasm2.analysis.binary import Container
from miasm2.analysis.machine import Machine
from miasm2.analysis.dse import DSEEngine, DSEPathConstraint
from miasm2.expression.expression import ExprId
from miasm2.jitter.jitload import PAGE_READ,PAGE_WRITE
from miasm2.jitter.csts import EXCEPT_INT_XX
def main():
	cont = Container.from_stream(open("./binary"))
	bin_stream = cont.bin_stream
	machine = Machine(cont.arch)
	jitter = machine.jitter(jit_type='python')
	#jitter.init_stack()
	data = ""
	with open("./binary","rb") as fp:
		data = fp.read()
	
	
	segm = "\x00"*500
	stack = "\x00"*(0xffff)
	jitter.vm.add_memory_page(0,PAGE_READ|PAGE_WRITE,segm)
	jitter.vm.add_memory_page(0x400000,PAGE_READ|PAGE_WRITE,data)
	jitter.vm.add_memory_page(0xffffffff-0xffff,PAGE_READ|PAGE_WRITE,stack)
	jitter.vm.add_memory_page(0x410000,PAGE_READ|PAGE_WRITE,"\x00"*0xffff)	
	print dir(jitter.cpu)
	jitter.init_run(0x400670)
	dse = DSEPathConstraint(machine)
	dse.attach(jitter)
	dse.update_state_from_concrete()
	snapshot = dse.take_snapshot()
	jitter.jit.log_mn = True
	
	#jitter.add_breakpoint(0x400948,ignore)
	#jitter.add_breakpoint(0x400954,ignore_2)	
	VAL = ExprId("VAL",32)
		
	jitter.continue_run()
	print dse.new_solutions

	pass
main()
