"""
Test module for RISC-V Register Verifier
"""
from . import riscv_reg_block
from .riscv_reg_block import reg_access

def scan_trigger_register(register_space_start, register_space_end):
    """
    Functionm for find trigger register to 0x4
    """
    info_of_bug = []

    for addr in range(register_space_start, register_space_end):
        riscv_reg_block.uart = riscv_reg_block.UARTBlackBox()
        reg_access(addr, 1, "write")
        resp = reg_access(4, 0, "read")

        if not resp["ack"]:
            info_of_bug.append({
                "addr": addr,
                "bug_type": "lock_after_other_reg",
                "trigger_pattern": f"write {addr:04x} -> read 4",
                "description": "Writing this register blocks register 4",
                "FSM": [
                    "Starting test",
                    "WRITE",
                    "READ",
                    f"FIND TRIGGER REGISTER: 0x{addr:04x}"
                ]
            })
    return info_of_bug
