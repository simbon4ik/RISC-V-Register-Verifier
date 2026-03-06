from typing import Dict


def riscv_reg_access(
        addr: int, data: int, rw: str, bus_width: int = 32
        ) -> Dict:
    """
    Stub: заменить на реальный DUT.
    """
    raise NotImplementedError("Connect real riscv_reg_access from DUT package")


def reg_read(addr: int, bus_width: int = 32) -> Dict:
    return riscv_reg_access(addr=addr, data=0, rw="read", bus_width=bus_width)


def reg_write(addr: int, data: int, bus_width: int = 32) -> Dict:
    return riscv_reg_access(
        addr=addr, data=data, rw="write", bus_width=bus_width
        )
