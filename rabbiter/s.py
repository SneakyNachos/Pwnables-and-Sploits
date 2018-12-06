from miasm2.analysis.binary import Container
from miasm2.analysis.machine import Machine
from miasm2.analysis.sandbox import Sandbox_Linux_x86_64
from miasm2.core.graph import MatchGraphJoker
from miasm2.core.graph import DiGraphSimplifier
from miasm2.expression.expression import ExprId
from miasm2.core.interval import interval
from miasm2.core.asmbloc import bbl_simplifier, expr_is_label, asm_resolve_final, AsmLabel
import re

#Trackers
pointer_track = {}
jz_track = {}
double_track = []

#Regex for Tracking during disassembly
reg_exp_pat1 = "DWORD\sPTR\s\[RBP\+(.*)\],\s0x([0-9A-Z]*)"
reg_exp_pat2 = "E[A-Z]X,\s0x([A-Z0-9]+)"
reg_exp_pat3 = "loc_[0-9A-Za-f]*:(0x[0-9a-f]*)"
reg_exp_pat4 = "(E[A-Z][IX]),\s0x([A-Z0-9]*)"

def get_counter(mn,attrib,pool_bin,cur_bloc,offsets_to_dis,symbol_pool):
	for line in  cur_bloc.lines:

		#Pattern 1 MOV POINTER to block into variable
		if line.name == "MOV":
			#Inital dispatch tracker check
			match = re.findall(reg_exp_pat1,str(line))
			if match != []:
				#Sanity Check
				if len(match[0][1]) >= 4:
					pointer_track.update({cur_bloc:match[0][1]})

			#Pattern 3
			match = re.findall(reg_exp_pat4,str(line))
			if match != []:
				#Sanity Check
				if len(match[0][1]) >= 4 and match[0][1] != 'FFFFFFFF':
					double_track.append([cur_bloc,match[0][1]])

		#Pattern 2 JZ Block
		if line.name == "JZ":
			tline = line	
			
			#Loop through the lines and hunt down the dispatcher tracker line
			for line in cur_bloc.lines:
				match = re.findall(reg_exp_pat2,str(line))
				if match != []:
					#Grab the offset and the block associated with the match
					dest_offset = re.findall(reg_exp_pat3,str(tline))
					jz_track.update({match[0]:int(dest_offset[0],16)})
		
			
	pass

def main():
	cont = Container.from_stream(open("rabbiter"))
	bin_stream = cont.bin_stream

	#Place Location of starting address to deobfuscate
	#adr = 0xc50  #test4.bin
	#adr = 0x1150 #sub_1150.bin
	#adr = 0x14e0 #sub_14e0.bin
	#adr = 0x1760 #- Done
	#adr = 0x19f0 #sub_19f0.bin
	adr = 0x1cc0 #sub_1cc0.bin
	#adr = 0x25b0 #sub_25b0.bin
	#adr = 0x2800 #sub_2800.bin
	#adr = 0x2a80 #sub_2a80.bin
	#adr = 0x30b0 #main,test5.bin,Done

	#Setup the diassembly machine
	machine = Machine(cont.arch)

	#Get the binary stream and set the disassembly callback to get_counter
	mdis = machine.dis_engine(bin_stream)
	mdis.dis_bloc_callback = get_counter

	#Get the disassembly blocks for the target address
	blocks = mdis.dis_multibloc(adr)

	print jz_track
	print double_track

	open("cfg_before.dot","w").write(blocks.dot())	
	

	def jump_merge(dgs,graph):
		"""
		Kill all of the extra jump blocks that are not needed
		"""

		#Create a Node matcher for blocks that are just 'JMP' instructions that are followed by blocks that end in 'JG'
		jump_end = MatchGraphJoker(name='jump_end',restrict_in=False,filt = lambda block: block.lines[-1].name == 'JMP' and len(block.lines) == 1)
		jump_jg = MatchGraphJoker(name='jump_jg',restrict_in=False,restrict_out=False,filt=lambda block: block.lines[-1].name=='JG')
		jump_matcher = jump_end >> jump_jg
		

		#Loop through all matches found for 'JMP' -> 'JG'
		for sol in jump_matcher.match(graph):
			#Get 'Pred' ->* 'JMP' -> 'JG'
			for pred in graph.predecessors(sol[jump_end]):
				
				#Calculate the constraint between 'Pred' and 'JMP'
				constraint = graph.edges2constraint[(pred,sol[jump_end])]
				
				#Get last line of the 'Pred' block to modify 
				last_instr = pred.lines[-1]
	
				#Check if the last instruction is basically a jump instruction
				if last_instr.breakflow() and last_instr.dstflow():
					new_arg = []

					#Create new expression for the 'jmp' instruction
					for arg in last_instr.args:
						if expr_is_label(arg):
							new_arg.append(ExprId(sol[jump_jg].label,arg.size))
						else:
							new_arg.append(arg)

					#Set the last line of the 'Pred' block to point to the 'JG' block
					last_instr.args = new_arg

				#Sanity check to see if there's a pointer already
				if (pred,sol[jump_jg]) not in graph.edges2constraint:
					#Add 'Pred' -> 'JG'
					graph.add_edge(pred,sol[jump_jg],constraint)

			#Destroy 'JMP' -> 'JG'
			graph.del_node(sol[jump_end])
		pass

	
	
	

	def add_new_shit(dgs,graph):
		"""
		Pointer Track structure {block:master_loop_target_value}
			block: The block that needs to be appended based on master_loop_target_value
			master_loop_target_value: The tracked register value that the dispatcher uses

		JZ Track structure {offset:sub_dispatcher_expected_value}
		"""
		for key,val in pointer_track.iteritems():
			
			#Insert
			#Loop through all blocks
			for block in blocks:
				#See if the block in question is one of the track values
				if block.lines[0].offset == jz_track[val]:
					#Get all the successors and delete they are not needed
					for succ in graph.successors(key):
						graph.del_edge(key,succ)
										
					#Recorrect the block to point to the target block
					last_instr = key.lines[-1]
					if last_instr.breakflow() and last_instr.dstflow():
						new_arg = []

						#Build Expression
						for arg in last_instr.args:
							if expr_is_label(arg):
								new_arg.append(ExprId(block.label,arg.size))
							else:
								new_arg.append(arg)
						last_instr.args = new_arg

					#Create edge to the new block with hard-coded constraint of always jump to
					if (key,block) not in graph.edges2constraint:
						graph.add_edge(key,block,'c_to')

						
							
	def add_new_shit2(dgs,graph):
		"""
		Fix up the blocks that do MOV E[A-Z]X, MOV E[A-Z]X in the first two lines with the master-dispatcher tracker
		Case 1: Repair the bottom jump statement 
		Case 2: Add conditional jump to found fail case, and replace the original CMOV* instruction with the jump
		"""
		#Loop through double_track tracking structure
		for index in xrange(0,len(double_track),2):
			#Grab the {block:value} pair
			item1 = double_track[index]   #JMP case
			item2 = double_track[index+1] #cmovX reg1, reg2
			
			#Loop through all blocks
			for block in blocks:
				#Check if case 1 match
				if block.lines[0].offset == jz_track[item1[1]]:
					print "Test"
					print item1
					last_instr = item1[0].lines[-1]
					if last_instr.breakflow() and last_instr.dstflow():
						new_arg = []
						for arg in last_instr.args:
							if expr_is_label(arg):
								new_arg.append(ExprId(block.label,16))
							else:
								new_arg.append(arg)
						last_instr.args = new_arg
					print hex(item1[0].lines[0].offset)
					print hex(block.lines[0].offset)
					if (item1[0],block) not in graph.edges2constraint:
						graph.add_uniq_edge(item1[0],block,'c_bad')
						continue

				#Check if case 2 match
				found_case_2 = False
				
				if block.lines[0].offset == jz_track[item2[1]]:
					
					#Loop through the blocks lines for the CMOV instruction
					for line in item2[0].lines:
						
						if "CMOV" in line.name:
							found_case_2 = True
							#Replace the CMOV
							new_label = "J"+line.name.split("CMOV")[1]
							arg = line.args
							new_arg = []
							
							val = hex(block.lines[0].offset).lstrip("0x")
							
							new_arg.append(ExprId(AsmLabel("loc_%s%s"%("0"*(16-len(val)),val.upper()), block.lines[0].offset),16))
							del item2[0].lines[-3]
							
							
							last_instr = item2[0].lines[-2]
							last_instr.name = new_label
							last_instr.args = new_arg
							#del item2[0].lines[-2]
							#last_instr = item2[0].lines[-2]
							#last_instr.name = 'NOP'
							#last_instr.args = []
							graph.add_uniq_edge(item2[0],block,'c_to')
							break
							
					
					
	def jz_jg_delete(dgs,graph):
		"""
		Staple the JG -> JZ to the SUCC, JG->SUCC and delete the JZ
		"""
		jump_jg = MatchGraphJoker(name='jump_jg',restrict_in=False,restrict_out=False,filt=lambda block: block.lines[-1].name=='JG')
		jump_jz = MatchGraphJoker(name='jump_jz',restrict_in=False,restrict_out=False,filt=lambda block: block.lines[-1].name=='JZ')
		matcher = jump_jg >> jump_jz
		
		for sol in matcher.match(graph):
			for succ in graph.successors(sol[jump_jz]):
				graph.add_uniq_edge(sol[jump_jg],succ,'c_to')
				graph.del_edge(sol[jump_jz],succ)
				
			graph.del_node(sol[jump_jz])
			
		
			
		pass

	def final_delete(dgs,graph):
		"""
		This is a blanket search for the Master jg dispatcher block
		"""
		top = MatchGraphJoker(name='top',restrict_in=False,restrict_out=False)
		jump_jg = MatchGraphJoker(name='jump_jg',restrict_in=False,restrict_out=False,filt=lambda block: block.lines[-1].name=='JG')
		bottom = MatchGraphJoker(name='bottom',restrict_in=False,restrict_out=False)
		matcher = top >> jump_jg >> bottom
		for sol in matcher.match(graph):
			#Kill the Master JG blocks edges to predecessors
			for pred in graph.predecessors(sol[jump_jg]):
				if (pred,sol[jump_jg]) in graph.edges2constraint:						
					graph.del_edge(pred,sol[jump_jg])
			
			#Kill the Master JG blocks edges to successors
			for succ in graph.successors(sol[jump_jg]):
				if (sol[jump_jg],succ) in graph.edges2constraint:
					graph.del_edge(sol[jump_jg],succ)
			
			#Kill the Master JG node
			graph.del_node(sol[jump_jg])
		pass

	def jg_combine(dgs,graph):
		"""
		Combine N-level of JG blocks and delete left-overs until Master JG is left-over
		"""
		jump_jg = MatchGraphJoker(name='jump_jg',restrict_in=False,restrict_out=False,filt=lambda block: block.lines[-1].name=='JG')
		jump_jg2 = MatchGraphJoker(name='jump_jg2',restrict_in=False,restrict_out=False,filt=lambda block: block.lines[-1].name=='JG')
		matcher = jump_jg >> jump_jg2
		for sol in matcher.match(graph):
			
			if (sol[jump_jg],sol[jump_jg2]) in graph.edges2constraint:
				graph.del_edge(sol[jump_jg],sol[jump_jg2])
			if (sol[jump_jg2],sol[jump_jg]) in graph.edges2constraint:
				graph.del_edge(sol[jump_jg2],sol[jump_jg])

					
		#Kill straggler JG blocks that will now have zero blocks targeting them
		jump_jg = MatchGraphJoker(name='jump_jg',restrict_in=True,restrict_out=False,filt=lambda block: block.lines[-1].name=='JG')
		blk = MatchGraphJoker(name='blk',restrict_out=False,restrict_in=False)
		matcher = jump_jg >> blk

		#This is to prevent constraint copy errors because the matcher.match will grab parent copies
		test_b = []
		for sol in matcher.match(graph):
			
			#Kill edges between 'JG' -> 'BLK'
			for succ in graph.successors(sol[jump_jg]):
				if (sol[jump_jg],sol[blk]) in graph.edges2constraint:
					graph.del_edge(sol[jump_jg],sol[blk])
			
			#Test if the jg block has already been deleted
			if sol[jump_jg] not in test_b:
				graph.del_node(sol[jump_jg])
			
			#Append just because
			test_b.append(sol[jump_jg])
		
			
		pass

	#Start the digraph simplifier to go ahead and destroy simple spaghetti blocks/
	#This might cause un-deterministic walking of the di-graph though, so if it errors re-run until the program completes
	dgs = DiGraphSimplifier()
	blocks = bbl_simplifier(blocks)
	blocks = dgs(blocks)

	#Add the new jump_merge to the digraph simplifier passes
	dgs.enable_passes([jump_merge])
	blocks = dgs(blocks)
	blocks = bbl_simplifier(blocks)
			
	#Add 'add_new_shit' to the digraph simplifier passes
	dgs.enable_passes([add_new_shit])
	blocks = dgs(blocks)
	blocks = bbl_simplifier(blocks)	

	#Add 'jz_jg_delete' to the digraph simplifier passes
	#This will Cut down the jz -> jg components on the graph
	dgs.enable_passes([jz_jg_delete])
	blocks = dgs(blocks)
	blocks = bbl_simplifier(blocks)

	#Add 'jump_merge' to the digraph simplifier passes
	#Cut down on the final phase of protector jg/jmp blocks
	dgs.enable_passes([jump_merge])
	blocks = dgs(blocks)
	blocks = bbl_simplifier(blocks)

	#Kill sub-master jg blocks
	dgs = DiGraphSimplifier()
	dgs.enable_passes([jg_combine])
	blocks = dgs(blocks)
	
	#Fix up the blocks with the cmov* instructions to point/patch to the correct blocks
	dgs = DiGraphSimplifier()
	dgs.enable_passes([add_new_shit2])
	
	#Add some more 
	blocks = dgs(blocks)
	blocks = bbl_simplifier(blocks)
	
	#Kill the final master jg block
	dgs = DiGraphSimplifier()
	dgs.enable_passes([final_delete])
	blocks = dgs(blocks)
	#blocks = bbl_simplifier(blocks)

	#Done
	open("cfg.dot","w").write(blocks.dot())
	#blocks.sanity_check()
	print len(blocks)
	head = blocks.heads()[0]
	"""
	for label in mdis.symbol_pool.items:
		mdis.symbol_pool.del_label_offset(label)
	mdis.symbol_pool.set_offset(head.label, adr)
	"""
	print mdis.symbol_pool
	

	from miasm2.core.asmbloc import asm_resolve_final, assemble_block, conservative_asm # blocks_final is our cleaned and fixed CFG
	dinterval = interval(blk.get_range() for blk in blocks)
	start,end = dinterval.hull()
	dinterval = interval([dinterval.hull()])
	print dinterval
	#patches = asm_resolve_final(mdis.arch, blocks, mdis.symbol_pool,dst_interval=None)
	patches = "\x90"*(end-start+1)
	for blk in blocks:
		blk.size = 0
		"""
		for instr in blk.lines:
			s = conservative_asm(mdis.arch,instr,mdis.symbol_pool,conservative=False)[0]
			blk.size += len(s)
		"""
		assemble_block(mdis.arch,blk,mdis.symbol_pool,conservative=False)
		
		
		for instr in blk.lines:
			stuff = instr.data
			patches = patches[0:(instr.offset-start)] + stuff + patches[(instr.offset-start)+len(stuff):end]
		
	#patches = asm_resolve_final(mdis.arch, blocks, mdis.symbol_pool,dst_interval=None)
	"""
	with open("test.bin","wb") as tp:
		with open("rabbiter","rb") as fp:
			tp.write(fp.read())
	"""
	"""
	with open("test.bin","r+") as fp:
		
		for start, stop in dinterval.intervals:
			fp.seek(start)
			fp.write("\x00"*(stop-start+1))
		for offset, data in patches.iteritems():
			fp.seek(offset)
			fp.write(data)		
	"""
	with open("test.bin","r+") as fp:
		fp.seek(start)
		fp.write(patches)	
	
	
	pass
main()
