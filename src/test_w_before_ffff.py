from .riscv_reg_block import reg_access
from .config import Note

MIN_VALUE = 0x0000
MAX_VALUE = 0xFFFF


def scan_register_read_after_diff_write(
        REGISTER_SPACE_START, REGISTER_SPACE_END
        ):
    errors = []
    info_of_bug = []

    for addr in range(REGISTER_SPACE_START, REGISTER_SPACE_END):
        try:
            for value in range(MIN_VALUE, MAX_VALUE):
                resp = reg_access(addr, value, "write")     
                resp = reg_access(addr, 0, "read")            
                reg = Note(addr, resp["reg_value"], resp["ack"])
                if not reg.ack:
                    continue
                if (reg.reg_value != value):
                    info_of_bug.append({
                        "addr": reg.addr,
                        "bug_type": "bag with write different values",
                        "trigger_pattern": "write random values",
                        "description": f"correct value = {value}, real value = {reg.reg_value}",
                        "FSM": ["Stating Read after Different Correct Write test", "WRITE", "READ", "ERROR WITH READ AFTER WRITE"]
                        })
        except Exception as e:
            errors.append((addr, str(e)))
    return info_of_bug