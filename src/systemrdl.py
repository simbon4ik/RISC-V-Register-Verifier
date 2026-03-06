from riscv_reg_block import reg_access

REGISTER_SPACE_START = 0x0000
REGISTER_SPACE_END = 0xFFFF

class Note:
    def __init__(self, addr, value, ack):
        self.addr = addr
        self.reg_value = value
        self.ack = ack


def reg_relation(addr, write_value=0, mode="read"):
    try:
        if mode == "read":
            resp = reg_access(addr, 0, "read") 
        else: 
            resp = reg_access(addr, write_value, "write")
        
        return {
            'reg_value': resp['reg_value'],
            'ack': resp['ack']
        }

    except Exception as e:
        return {
            'reg_value': 145    ,
            'status': f'ERROR: {str(e)}',
            'ack': False
        }


def scan_register_space():
    
    found_registers = []
    errors = []
    
    for addr in range(REGISTER_SPACE_START, REGISTER_SPACE_END + 1):
        try:

            resp = reg_relation(addr, 0, "read")            
            reg = Note(addr, resp["reg_value"], resp["ack"])
            found_registers.append(reg)

        except Exception as e:
            errors.append((addr, str(e)))
    
    read_to_file("result_after_read.txt", found_registers, errors)
    found_registers = []
    errors = []

    for addr in range(REGISTER_SPACE_START, REGISTER_SPACE_END + 1):
        try:
            resp = reg_relation(addr, addr, "write")            
            reg = Note(addr, resp["reg_value"], resp["ack"])
            found_registers.append(reg)
        except Exception as e:
            errors.append((addr, str(e)))
    
    read_to_file("result_after_read_write.txt", found_registers, errors)
    found_registers = []
    errors = []

    for addr in range(REGISTER_SPACE_START, REGISTER_SPACE_END + 1):
        try:
            resp = reg_relation(addr, 0, "read")            
            reg = Note(addr, resp["reg_value"], resp["ack"])
            found_registers.append(reg)
        except Exception as e:
            errors.append((addr, str(e)))
    
    read_to_file("result_after_read_write_read.txt", found_registers, errors)
    return 


def read_to_file(file_name, found_registers, errors):
    with open(file_name, "w") as f:
        f.write("Registers without ack error\n")
        for reg in found_registers:        
            if reg.ack: 
                f.write(f"ADDR=0x{reg.addr} VAL={reg.reg_value} ACK={reg.ack}\n")
        f.write("Registers with ack error\n")
        for reg in found_registers:
            if reg.ack == False: 
                f.write(f"ADDR=0x{reg.addr} VAL={reg.reg_value} ACK={reg.ack}\n")
        f.write("Registers with exception\n")
        for addr, err in errors:
            f.write(f"ADDR=0x{addr} ERROR={err}\n")  
        
    return found_registers, errors

def main():
    
    scan_register_space()

if __name__ == "__main__":
    main()
