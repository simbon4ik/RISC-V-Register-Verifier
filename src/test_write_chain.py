"""
Test module for RISC-V Register Verifier
"""
import random
from .riscv_reg_block import reg_access
from .config import Note

MIN_VALUE = 0x0000
MAX_VALUE = 0xFFFF
NUM_WRITES = 10


def scan_register_write_chain(
        register_space_start, register_space_end
        ):
    """
    Test write stability across multiple write operations.

	Performs NUM_WRITES random writes to each address, then reads back
	the last written value. Reports if the read value doesn't match the
	last written value.
	"""
    info_of_bug = []

    for addr in range(register_space_start, register_space_end):
        last_val = None
        for _ in range(NUM_WRITES):
            value = random.randint(MIN_VALUE, MAX_VALUE)
            resp = reg_access(addr, value, "write")
            reg = Note(addr, resp["reg_value"], resp["ack"])
            if not reg.ack:
                break
            last_val = value

        if last_val is None:
            continue

        resp = reg_access(addr, 0, "read")
        reg = Note(addr, resp["reg_value"], resp["ack"])
        if not reg.ack:
            continue
        if reg.reg_value != last_val:
            info_of_bug.append({
				"FSM": [f"WRITE_{NUM_WRITES}", "READ", "ERROR WITH READ AFTER WRITE"],
				"addr": reg.addr,
				"bug_type": "bug with write after write",
				"trigger_pattern": "write overwrite",
				"description": f"expected {last_val}, got {reg.reg_value}"
				})
    return info_of_bug
