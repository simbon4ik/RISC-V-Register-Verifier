from .riscv_reg_block import reg_access
from .config import Note

MIN_VALUE = 0x0000
MAX_VALUE = 0xFFFF

def scan_register_read_after_diff_write(REGISTER_SPACE_START, REGISTER_SPACE_END):
    
    reg_with_dif_beh = []
    errors = []
    info_of_bug = []
    
    for addr in range(REGISTER_SPACE_START, REGISTER_SPACE_END):
        try:
            for value in range(MIN_VALUE, MAX_VALUE):
                resp = reg_access(addr, value, "write")     
                resp = reg_access(addr, 0, "read")            
                reg = Note(addr, resp["reg_value"], resp["ack"])
                if not reg.ack:
                    continue
                if (reg.reg_value != value):
                    info_of_bug.append({"addr":reg.addr, "bug_type": "bag with write different values", "trigger_pattern": "write random values", "description": f"correct value = {value}, real value = {reg.reg_value}"})
        except Exception as e:
            errors.append((addr, str(e)))
    return info_of_bug
    
'''
#
#     read_to_file("reg_with_dif_beh_before_ffff.txt", reg_with_dif_beh, errors)


def read_to_file(file_name, found_registers, errors):
    with open(file_name, "w") as f:
        f.write("Registers with different behaviour\n")
        for reg in found_registers:        
            if reg.ack: 
                f.write(f"ADDR=0x{reg.addr:04x} VAL=0x{reg.reg_value:04x} ACK={reg.ack} CORRECT VALUE=0x{reg.correct_value:04x}\n")
        f.write("Registers with ack error and different behaviour\n")
        for reg in found_registers:
            if reg.ack == False: 
                f.write(f"A VAL=0x{reg.reg_value:04x} ACK={reg.ack} CORRECT VALUE=0x{reg.correct_value:04x}\n")
        f.write("Registers with exception\n")
        for addr, err in errors:
            f.write(f"ADDR=0x{addr:04x} ERROR={err}\n")  
        
    return found_registers, errors

def main():
    
    scan_register_read_after_diff_write(0x0, 0x16)

if __name__ == "__main__":
    main()
'''