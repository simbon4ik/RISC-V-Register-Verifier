from typing import Dict

try:
    from riscv_reg_block import reg_access
except ImportError:
    def reg_access(addr: int, data: int, rw: str, bus_width: int = 32) -> Dict:
        raise NotImplementedError(
            "riscv_reg_block.reg_access недоступен. "
        )


def reg_read(addr: int, bus_width: int = 32) -> Dict:
    return reg_access(addr=addr, data=0, rw="read", bus_width=bus_width)


def reg_write(addr: int, data: int, bus_width: int = 32) -> Dict:
    return reg_access(addr=addr, data=data, rw="write", bus_width=bus_width)
