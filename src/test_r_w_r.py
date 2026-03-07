"""
Test module for RISC-V Register Verifier
"""
from .riscv_reg_block import reg_access
from .config import Note

VALUE = -1


def scan_register_r_w_r(register_space_start, register_space_end):
    """
    Function for check correct read after read and write
    """
    available_registers = []
    info_of_bug = []

    for addr in range(register_space_start, register_space_end):

        resp = reg_access(addr, 0, "read")
        reg = Note(addr, resp["reg_value"], resp["ack"])
        if reg.ack:
            available_registers.append(reg.addr)


    for addr in range(register_space_start, register_space_end):
        resp = reg_access(addr, VALUE, "write")
        reg = Note(addr, resp["reg_value"], resp["ack"])
        if (reg.addr in available_registers and not reg.ack):
            info_of_bug.append({
                "addr": reg.addr,
                "bug_type": "bug with write after read",
                "trigger_pattern": "read_write_bug",
                "description": "After writing reg is not available",
                "FSM": ["Starting RWR test", "READ", "WRITE", "BUG WITH ACCESS AFTER READ"]
                })


    for addr in range(register_space_start, register_space_end):
        resp = reg_access(addr, 0, "read")
        reg = Note(addr, resp["reg_value"], resp["ack"])
        if (reg.addr in available_registers and not reg.ack):
            info_of_bug.append({
                "addr": reg.addr,
                "bug_type": "bug with write after write",
                "trigger_pattern": "read_write_read_bug",
                "description": "After writing reg is not available",
                "FSM": [
                    "Starting RWR test",
                    "READ",
                    "WRITE",
                    "READ",
                    "BUG WITH ACCESS AFTER READ AND WRITE"
                ]
                })
    return info_of_bug
