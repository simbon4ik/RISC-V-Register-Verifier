from .riscv_reg_block import reg_access
from .config import Note
import random

MIN_VALUE = 0x0000
MAX_VALUE = 0xFFFF
NUM_WRITES = 10


def scan_register_write_chain(
        REGISTER_SPACE_START, REGISTER_SPACE_END
        ):
    errors = []
    info_of_bug = []

    for addr in range(REGISTER_SPACE_START, REGISTER_SPACE_END):
        try:
            fsm_arr = []
            last_value = None
            for i in range(NUM_WRITES):
                value = random.randint(MIN_VALUE, MAX_VALUE)
                resp = reg_access(addr, value, "write")
                fsm_arr.append("WRITE")
                reg = Note(addr, resp["reg_value"], resp["ack"])
                if not reg.ack:
                    break
                last_value = value

            if last_value is None:
                continue
            
            resp = reg_access(addr, 0, "read")
            fsm_arr.append("READ")
            reg = Note(addr, resp["reg_value"], resp["ack"])
            if not reg.ack:
                continue
            if reg.reg_value != last_value:
                info_of_bug.append({
                    "FSM": fsm_arr,
                    "addr": reg.addr,
                    "bug_type": "bug with write after write",
                    "trigger_pattern": "write overwrite",
                    "description": f"last written value = {last_value}, read value = {reg.reg_value} after {NUM_WRITES} writes"
                    })
        except Exception as e:
            errors.append((addr, str(e)))
    return info_of_bug