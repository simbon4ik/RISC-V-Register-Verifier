from typing import Iterable
from .dut_interface import reg_read, reg_write


def sweep_read_all(addrs: Iterable[int], bus_width: int = 32):
    """
    Простейший проход по адресам: read на каждый addr.
    Это зачаток Test Sequencer'а под метрику coverage.
    """
    results = {}
    for addr in addrs:
        resp = reg_read(addr, bus_width=bus_width)
        results[addr] = resp
    return results
