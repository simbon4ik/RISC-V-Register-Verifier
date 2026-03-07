from . import riscv_reg_block
from .riscv_reg_block import reg_access
from .config import Note

VALUE = -1


def scan_register_r_w_r(REGISTER_SPACE_START, REGISTER_SPACE_END):
    available_registers = []
    errors = []
    info_of_bug = []

    for addr in range(REGISTER_SPACE_START, REGISTER_SPACE_END):
        try:
            resp = reg_access(addr, 0, "read")            
            reg = Note(addr, resp["reg_value"], resp["ack"])
            if (reg.ack):
                available_registers.append(reg.addr)
        except Exception as e:
            errors.append((addr, str(e)))

    for addr in range(REGISTER_SPACE_START, REGISTER_SPACE_END):
        try:
            resp = reg_access(addr, VALUE, "write")            
            reg = Note(addr, resp["reg_value"], resp["ack"])
            if (reg.addr in available_registers and not reg.ack):
                info_of_bug.append({
                    "addr": reg.addr,
                    "bug_type": "bug with write after read",
                    "trigger_pattern": "read_write_bug",
                    "description": "After writing reg is not available",
                    "FSM": ["Stating RWR test", "READ", "WRITE", "BUG WITH ACCESS AFTER READ"]
                    })
        except Exception as e:
            errors.append((addr, str(e)))

    for addr in range(REGISTER_SPACE_START, REGISTER_SPACE_END):
        try:
            resp = reg_access(addr, 0, "read")            
            reg = Note(addr, resp["reg_value"], resp["ack"])
            if (reg.addr in available_registers and not reg.ack):
                info_of_bug.append({
                    "addr": reg.addr,
                    "bug_type": "bug with write after write",
                    "trigger_pattern": "read_write_read_bug",
                    "description": ["Stating RWR test", "READ", "WRITE", "READ", "BUG WITH ACCESS AFTER READ AND WRITE"]
                    "FSM": fsm_operations
                    })
        except Exception as e:
            errors.append((addr, str(e)))

    for addr in range(REGISTER_SPACE_START, REGISTER_SPACE_END):
        try:
            riscv_reg_block.uart = riscv_reg_block.UARTBlackBox()
            reg_access(addr, 1, "write")
            resp = reg_access(4, 0, "read")

            if not resp["ack"]:
                info_of_bug.append({
                    "addr": addr,
                    "bug_type": "lock_after_other_reg",
                    "trigger_pattern": f"write {addr} -> read 4",
                    "description": "Writing this register blocks register 4"
                })

        except Exception as e:
            errors.append((addr, str(e)))
    return info_of_bug
