from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from riscv_reg_block import reg_access

REGISTER_SPACE_START = 0x0000
REGISTER_SPACE_END = 0xFFFF


@dataclass
class RegisterInfo:
    addr: int
    name: str
    access: str = "rw"


class RegisterModel:
    def __init__(self) -> None:
        self._regs: Dict[int, RegisterInfo] = {}

    def add_reg(self, addr: int, name: str, access: str = "rw") -> None:
        self._regs[addr] = RegisterInfo(addr=addr, name=name, access=access)

    def get_reg(self, addr: int) -> Optional[RegisterInfo]:
        return self._regs.get(addr)

    def all_addrs(self) -> List[int]:
        return sorted(self._regs.keys())


@dataclass
class Note:
    addr: int
    reg_value: int
    status: str
    ack: bool


def reg_relation(addr: int, write_value: int = 0, mode: str = "read") -> Dict:
    try:
        if mode == "read":
            resp = reg_access(addr, 0, "read")
        else:
            resp = reg_access(addr, write_value, "write")

        return {
            "reg_value": resp["reg_value"],
            "status": resp["status"],
            "ack": resp["ack"],
        }

    except Exception as e:
        return {
            "reg_value": 0,
            "status": f"ERROR: {str(e)}",
            "ack": False,
        }


def scan_once(
        mode: str, value_fn=lambda addr: 0
        ) -> Tuple[List[Note], List[Tuple[int, str]]]:
    found_registers: List[Note] = []
    errors: List[Tuple[int, str]] = []

    for addr in range(REGISTER_SPACE_START, REGISTER_SPACE_END + 1):
        resp = reg_relation(addr, value_fn(addr), mode)
        note = Note(
            addr=addr,
            reg_value=resp["reg_value"],
            status=resp["status"],
            ack=resp["ack"],
        )
        if "ERROR:" in resp["status"]:
            errors.append((addr, resp["status"]))
        else:
            found_registers.append(note)

    return found_registers, errors


def scan_register_space() -> None:
    regs_r, errs_r = scan_once(mode="read", value_fn=lambda addr: 0)
    write_to_file("result_after_read.txt", regs_r, errs_r)

    regs_w, errs_w = scan_once(mode="write", value_fn=lambda addr: addr)
    write_to_file("result_after_read_write.txt", regs_w, errs_w)

    regs_rr, errs_rr = scan_once(mode="read", value_fn=lambda addr: 0)
    write_to_file("result_after_read_write_read.txt", regs_rr, errs_rr)


def write_to_file(
    file_name: str,
    found_registers: List[Note],
    errors: List[Tuple[int, str]],
) -> None:
    with open(file_name, "w", encoding="utf-8") as f:
        f.write("Регистры с ACK=True\n")
        for reg in found_registers:
            if reg.ack:
                f.write(
                    f"ADDR=0x{reg.addr:04X} VAL=0x{reg.reg_value:08X} "
                    f"STATUS={reg.status} ACK={reg.ack}\n"
                )

        f.write("\nРегистры с ACK=False\n")
        for reg in found_registers:
            if not reg.ack:
                f.write(
                    f"ADDR=0x{reg.addr:04X} VAL=0x{reg.reg_value:08X} "
                    f"STATUS={reg.status} ACK={reg.ack}\n"
                )

        f.write("\nОшибки протокола/исключения\n")
        for addr, err in errors:
            f.write(f"ADDR=0x{addr:04X} ERROR={err}\n")


def main() -> None:
    scan_register_space()


if __name__ == "__main__":
    main()
