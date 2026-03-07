"""
Test module for RISC-V Register Verifier
"""
import random
from .riscv_reg_block import reg_access
from .config import Note

MIN_VALUE = 0x0000
MAX_VALUE = 0xFFFF
NUM_ITERATIONS = 1000


def scan_register_fuzz_rw(
        register_space_start, register_space_end
        ):
    """
    Fuzz test for register read/write operations.

	For each address in the range, performs NUM_ITERATIONS of random value writes
	followed by reads. Compares written and read values to detect inconsistencies.
	"""
    info_of_bug = []

    for addr in range(register_space_start, register_space_end):
        cnt = 0
        for _ in range(NUM_ITERATIONS):
            value = random.randint(MIN_VALUE, MAX_VALUE)
            resp = reg_access(addr, value, "write")
            resp = reg_access(addr, 0, "read")
            cnt += 1
            reg = Note(addr, resp["reg_value"], resp["ack"])
            if not reg.ack:
                continue
            if reg.reg_value != value:
                info_of_bug.append({
					"FSM" : [f"WRITE_READ_{cnt}", "ERROR WITH READ AFTER WRITE"],
					"addr": reg.addr,
					"bug_type": "bug with write random values",
					"trigger_pattern": "write random values",
					"description": f"correct value = {value}, real value = {reg.reg_value}"
					})
    return info_of_bug
