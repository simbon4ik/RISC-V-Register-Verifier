from .riscv_reg_block import reg_access

MIN_VALUE = 0x00000
MAX_VALUE = 0xFFFFF #more than 2^16

class Note:
    def __init__(self, addr, value, ack):
        self.addr = addr
        self.reg_value = value
        self.ack = ack

def scan_register_read_after_diff_write(REGISTER_SPACE_START, REGISTER_SPACE_END):
    
    errors = []
    info_of_bug = []
    
    for addr in range(REGISTER_SPACE_START, REGISTER_SPACE_END):
        try:
            for value in range(MIN_VALUE, MAX_VALUE):
                resp = reg_access(addr, value, "write")
                resp = reg_access(addr, 0, "read")             
                reg = Note(addr, resp["reg_value"], resp["ack"])
                if (reg.ack and reg.reg_value != value):        
                    info_of_bug.append({
                        "addr":reg.addr,
                        "bug_type": "bug with read after write",
                        "trigger_pattern": "write_bug",
                        "description":  "After writing reg doesn't consist correct value",
                        "FSM": ["Starting Read after Different Write test", "WRITE", "READ", "INCORRECT READ AND WRITE"]
                        })
                    break
        except Exception as e:
            errors.append((addr, str(e)))
    return info_of_bug
