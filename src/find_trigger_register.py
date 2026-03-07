from . import riscv_reg_block
from .riscv_reg_block import reg_access
from .config import Note

def scan_trigger_register(REGISTER_SPACE_START, REGISTER_SPACE_END):
    errors = []
    info_of_bug = []

    for addr in range(REGISTER_SPACE_START, REGISTER_SPACE_END):
        try:
            riscv_reg_block.uart = riscv_reg_block.UARTBlackBox()
            reg_access(addr, 1, "write")
            resp = reg_access(4, 0, "read")

            if not resp["ack"]:
                info_of_bug.append({
                    "addr": addr,
                    "bug_type": "lock_after_other_reg",
                    "trigger_pattern": f"write {addr:04x} -> read 4",
                    "description": "Writing this register blocks register 4",
                    "FSM": ["Starting test", "WRITE", "READ", f"FIND TRIGGER REGISTER: 0x{addr:04x}"]
                })

        except Exception as e:
            errors.append((addr, str(e)))
    return info_of_bug