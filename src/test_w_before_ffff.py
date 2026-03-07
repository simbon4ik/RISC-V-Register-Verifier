"""
Test module for RISC-V Register Verifier
"""
from .riscv_reg_block import reg_access
from .config import Note

MIN_VALUE = 0x0000
MAX_VALUE = 0xFFFF


def scan_register_read_after_diff_write(
        register_space_start, register_space_end
        ):
    """
    Function for check correct read after diff write
    """
    info_of_bug = []

    for addr in range(register_space_start, register_space_end):
        for value in range(MIN_VALUE, MAX_VALUE):
            resp = reg_access(addr, value, "write")
            resp = reg_access(addr, 0, "read")
            reg = Note(addr, resp["reg_value"], resp["ack"])
            if not reg.ack:
                continue
            if reg.reg_value != value:
                info_of_bug.append({
                    "addr": reg.addr,
                    "bug_type": "bug with write different values",
                    "trigger_pattern": "write random values",
                    "description": f"correct value = {value:04x}, real value = {reg.reg_value:04x}",
                    "FSM": [
                        "Starting Read after Different Correct Write test",
                        "WRITE",
                        "READ",
                        "ERROR WITH READ AFTER WRITE"
                    ]
                    })
    return info_of_bug
