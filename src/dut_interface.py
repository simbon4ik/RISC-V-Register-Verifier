from typing import Dict

try:
    from riscv_reg_block import reg_access
except ImportError:
    def reg_access(addr: int, data: int, rw: str) -> Dict:
        raise NotImplementedError(
            "riscv_reg_block.reg_access недоступен. "
        )


def reg_read(addr: int, data: int) -> Dict:
    return reg_access(addr=addr, data=0, rw="read")


def reg_write(addr: int, data: int) -> Dict:
    return reg_access(addr=addr, data=data, rw="write")
