from riscv_reg_block import reg_access

REGISTER_SPACE_START = 0x0000
REGISTER_SPACE_END = 0xFFFF

MIN_VALUE = 0x000000000
MAX_VALUE = 0xFFFFFFFFF #more than 2^32

class Note:
    def __init__(self, addr, value, ack):
        self.addr = addr
        self.reg_value = value
        self.ack = ack

def scan_register_read_after_diff_write():
    
    reg_with_dif_beh = []
    errors = []
    
    for addr in range(REGISTER_SPACE_START, REGISTER_SPACE_END):
        try:
            for value in range(MIN_VALUE, MAX_VALUE):
                resp = reg_access(addr, value, "write")            
                reg = Note(addr, resp["reg_value"], resp["ack"])
                if (reg.reg_value != value):
                    reg_with_dif_beh.append(reg)

        except Exception as e:
            errors.append((addr, str(e)))
    
    read_to_file("reg_with_dif_beh.txt", reg_with_dif_beh, errors)


def read_to_file(file_name, found_registers, errors):
    with open(file_name, "w") as f:
        f.write("Registers with different behaviour\n")
        for reg in found_registers:        
            if reg.ack: 
                f.write(f"ADDR=0x{reg.addr} VAL={reg.reg_value} ACK={reg.ack}\n")
        f.write("Registers with ack error and different behaviour\n")
        for reg in found_registers:
            if reg.ack == False: 
                f.write(f"ADDR=0x{reg.addr} VAL={reg.reg_value} ACK={reg.ack}\n")
        f.write("Registers with exception\n")
        for addr, err in errors:
            f.write(f"ADDR=0x{addr} ERROR={err}\n")  
        
    return found_registers, errors

def main():
    
    scan_register_read_after_diff_write()

if __name__ == "__main__":
    main()
