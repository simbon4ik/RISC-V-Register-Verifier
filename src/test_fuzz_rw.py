from .riscv_reg_block import reg_access
from .config import Note
import random

MIN_VALUE = 0x0000
MAX_VALUE = 0xFFFF
NUM_ITERATIONS = 1000


def scan_register_fuzz_rw(
        REGISTER_SPACE_START, REGISTER_SPACE_END
        ):
    errors = []
    info_of_bug = []

    for addr in range(REGISTER_SPACE_START, REGISTER_SPACE_END):
        try:
            fsm_arr = []
            for _ in range(NUM_ITERATIONS):
                value = random.randint(MIN_VALUE, MAX_VALUE)
                resp = reg_access(addr, value, "write")
                fsm_arr.append("WRITE")     
                resp = reg_access(addr, 0, "read")
                fsm_arr.append("READ")            
                reg = Note(addr, resp["reg_value"], resp["ack"])
                if not reg.ack:
                    continue
                if (reg.reg_value != value):
                    info_of_bug.append({
                        "FSM" : fsm_arr,
                        "addr": reg.addr,
                        "bug_type": "bug with write random values",
                        "trigger_pattern": "write random values",
                        "description": f"correct value = {value}, real value = {reg.reg_value}"
                        })
        except Exception as e:
            errors.append((addr, str(e)))
    return info_of_bug