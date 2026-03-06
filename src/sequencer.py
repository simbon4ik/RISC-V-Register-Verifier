from typing import Iterable, Dict
from .dut_interface import reg_read, reg_write


def sweep_read(addrs: Iterable[int], bus_width: int = 32) -> Dict[int, Dict]:
    """
    Простейший проход: read по набору адресов.
    Возвращает словарь addr -> ответ DUT.
    """
    results: Dict[int, Dict] = {}
    for addr in addrs:
        resp = reg_read(addr, bus_width=bus_width)
        results[addr] = resp
    return results


def simple_smoke_sweep(start: int = 0x0000, end: int = 0x00FF, bus_width: int = 32) -> Dict[int, Dict]:
    """
    Минимальный smoke-проход по небольшому диапазону адресов.
    Удобно для первого запуска и проверки подключения к DUT.
    """
    addrs = range(start, end + 1)
    return sweep_read(addrs, bus_width=bus_width)
