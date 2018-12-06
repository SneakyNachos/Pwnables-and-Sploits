from miasm2.analysis.sandbox import Sandbox_Win_x86_32
from miasm2.jitter.csts import PAGE_READ,PAGE_WRITE
from miasm2.expression.expression import *
from miasm2.expression.simplifications import *
from miasm2.analysis.dse import DSEPathConstraint, DSEEngine
import sys
import z3
from elfesteem import pe_init
def main():
	global dse
	
	ALL_IMP_DLL = [
		"ntdll.dll","kernel32.dll","user32.dll",
		"ole32.dll","urlmon.dll","ws3_32.dll",
		"advapi32.dll","psapi.dll"
	]

	

	parser = Sandbox_Win_x86_32.parser(description="Win Sandbox")
	parser.add_argument("filename",help="Win filename")
	options = parser.parse_args()
	
	sb = Sandbox_Win_x86_32(options.filename,options,globals())
	sb.jitter.init_run(sb.entry_point)
	sb.jitter.ir_arch.do_all_segm=True
	sb.jitter.jit.log_mn=True
	sb.jitter.vm.add_memory_page(0,PAGE_READ|PAGE_WRITE,"\x00"*500)	
	def dump_data(jitter):
		new_data = jitter.vm.get_mem(0x400000,0x411000-0x400000)
		open('dump.bin','wb').write(new_data)
		return False
		pass
	
	raw_input("$")	
	sb.jitter.continue_run()
	pass
main()
