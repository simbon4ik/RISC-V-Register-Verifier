"""
Run module for RISC-V Register Verifier
"""
from .test_dif_v import scan_register_read_after_diff_write as srdw
from .test_r_w_r import scan_register_r_w_r as srwr
from .test_w_before_ffff import scan_register_read_after_diff_write as sdwf
from .test_fuzz_rw import scan_register_fuzz_rw as frw
from .test_read_chain import scan_register_read_chain as rc
from .test_write_chain import scan_register_write_chain as wc
from .test_oob_address import scan_oob_addresses as soob
from .find_trigger_register import scan_trigger_register as strf


def run_test(start_addr, end_addr):
    """
    Function for run test
    """
    result = strf(start_addr, end_addr)
    result += srwr(start_addr, end_addr)
    result += sdwf(start_addr, end_addr)
    result += srdw(start_addr, end_addr)
    result += frw(start_addr, end_addr)
    result += rc(start_addr, end_addr)
    result += wc(start_addr, end_addr)
    result += soob()
    return result
