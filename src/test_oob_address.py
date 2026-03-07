"""
Test module for RISC-V Register Verifier
"""
from .riscv_reg_block import reg_access
from .config import Note

MIN_VALUE = 0x0000
MAX_VALUE = 0xFFFF
NUM_WRITES = 10

def scan_addr_range(start, end):
    """
    Check read access for a range of addresses.

	Reads each address in the specified range and reports any that
	return a positive acknowledgment (ack=True) when they shouldn't.
	"""
    info_of_bug = []

    for addr in range(start, end):
        resp = reg_access(addr, 0, "read")
        reg = Note(addr, resp["reg_value"], resp["ack"])
        if reg.ack:
            info_of_bug.append({
                "FSM": ["READ", "ERROR: READING FROM INVALID ADDRESS"],
                "addr": reg.addr,
                "bug_type": "bug with addressing out of address space",
                "trigger_pattern": "incorrect address",
                "description": f"address = {addr}"
            })
    return info_of_bug

def scan_oob_addresses():
    """
    Test out-of-bounds address access.

	Reads addresses below 0 and above 0xFFFF to verify that invalid
	addresses are properly rejected (ack=False). Uses scan_addr_range
	for both negative and high address ranges.
	"""
    info_of_bug = []
    info_of_bug += scan_addr_range(-0xFFFFF, -1)
    info_of_bug += scan_addr_range(0x10000, 0xFFFF)

    return info_of_bug
