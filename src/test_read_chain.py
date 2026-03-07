"""
Test module for RISC-V Register Verifier
"""
from .riscv_reg_block import reg_access
from .config import Note

NUM_READS = 10


def scan_register_read_chain(
        register_space_start, register_space_end
        ):
    """
    Test read stability across multiple read operations.

	For each address, performs a first read to get the initial value,
	then does NUM_READS consecutive reads. Reports any read that returns
	a different value than the first one.
	"""
    info_of_bug = []

    for addr in range(register_space_start, register_space_end):
        cnt = 0
        resp = reg_access(addr, 0, "read")
        cnt += 1
        initial_reg = Note(addr, resp["reg_value"], resp["ack"])
        if not initial_reg.ack:
            continue
        init_value = initial_reg.reg_value

        for i in range(1, NUM_READS):
            resp = reg_access(addr, 0, "read")
            cnt += 1
            reg = Note(addr, resp["reg_value"], resp["ack"])
            if not reg.ack:
                continue
            if reg.reg_value != init_value:
                info_of_bug.append({
					"FSM": [f"READ_{cnt}", "ERROR WITH READ AFTER READ"],
					"addr": reg.addr,
					"bug_type": "bug with read after read",
					"trigger_pattern": "read stability",
					"description": f"expected {init_value}, got {reg.reg_value} on read {i+1}"
					})
    return info_of_bug
