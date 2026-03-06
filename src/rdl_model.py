from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class RegisterInfo:
    addr: int
    name: str
    width: int = 32
    access: str = "rw"


class RegisterModel:
    """
    Простая модель карты регистров в духе SystemRDL.
    В реальности вы будете наполнять её по результатам тестирования DUT.
    """

    def __init__(self) -> None:
        self._regs: Dict[int, RegisterInfo] = {}

    def add_reg(self, addr: int, name: str, width: int = 32, access: str = "rw") -> None:
        self._regs[addr] = RegisterInfo(addr=addr, name=name, width=width, access=access)

    def get_reg(self, addr: int) -> Optional[RegisterInfo]:
        return self._regs.get(addr)

    def all_addrs(self) -> List[int]:
        return sorted(self._regs.keys())
