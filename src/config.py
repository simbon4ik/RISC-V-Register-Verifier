class Note:
    def __init__(self, addr : int, value : int, ack : bool):
        self.addr = addr
        self.reg_value = value
        self.ack = ack

def read_to_file(file_name, found_registers, errors):
    with open(file_name, "w") as f:
        f.write("Registers without ack error\n")
        for reg in found_registers:        
            if reg.ack: 
                f.write(f"ADDR=0x{reg.addr:04x} VAL={reg.reg_value:04x} ACK={reg.ack}\n")
        f.write("Registers with ack error\n")
        for reg in found_registers:
            if reg.ack == False: 
                f.write(f"ADDR=0x{reg.addr:04x} VAL={reg.reg_value:04x} ACK={reg.ack}\n")
        f.write("Registers with exception\n")
        for addr, err in errors:
            f.write(f"ADDR=0x{addr:04x} ERROR={err}\n")  
        
    return found_registers, errors