from .riscv_reg_block import reg_access
from .config import Note

NUM_READS = 10


def scan_register_read_chain(
        REGISTER_SPACE_START, REGISTER_SPACE_END
        ):
    errors = []
    info_of_bug = []

    for addr in range(REGISTER_SPACE_START, REGISTER_SPACE_END):
        try:
            cnt = 0
            resp = reg_access(addr, 0, "read")
            cnt += 1
            initial_reg = Note(addr, resp["reg_value"], resp["ack"])
            if not initial_reg.ack:
                continue
            initial_value = initial_reg.reg_value

            for i in range(1, NUM_READS):
                resp = reg_access(addr, 0, "read")
                cnt += 1
                reg = Note(addr, resp["reg_value"], resp["ack"])
                if not reg.ack:
                    continue
                if reg.reg_value != initial_value:
                    info_of_bug.append({
                        "FSM": [f"READ_{cnt}", "ERROR WITH READ AFTER READ"],
                        "addr": reg.addr,
                        "bug_type": "bug with read after read",
                        "trigger_pattern": "read stability",
                        "description": f"initial value = {initial_value}, read value = {reg.reg_value} on read {i+1}"
                        })
        except Exception as e:
            errors.append((addr, str(e)))
    return info_of_bug