import sys
from elfesteem import pe_init
def main():
        global dse

        data = open(sys.argv[1]).read()

        pe = pe_init.PE(wsize=32)
        s_text = pe.SHList.add_section(name=".text",addr=0xe000,data=data)
        pe.Opthdr.AddressOfEntryPoint = s_text.addr
        open('sc_pe.exe',"wb").write(str(pe))
main()
