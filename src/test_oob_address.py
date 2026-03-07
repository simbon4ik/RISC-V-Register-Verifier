from .riscv_reg_block import reg_access
from .config import Note
import random

MIN_VALUE = 0x0000
MAX_VALUE = 0xFFFF
NUM_WRITES = 10

def scan_addr_range(start, end):
    errors = []
    info_of_bug = []
    
    for addr in range(start, end):
        try:
             resp = reg_access(addr, 0, "read")
             reg = Note(addr, resp["reg_value"], resp["ack"])
             if reg.ack:
                    info_of_bug.append({
						"addr": reg.addr,
						"bug_type": "bug with addressing out of address space",
						"trigger_pattern": "incorrect address",
						"description": f"address = {addr}"
		            })
        except Exception as e:
            errors.append((addr, str(e)))
            
    return info_of_bug

def scan_oob_addresses():
    info_of_bug = []
    info_of_bug += scan_addr_range(-0xFFFFF, -1)
    info_of_bug += scan_addr_range(0x10000, 0xFFFF)
    
    return info_of_bug

	