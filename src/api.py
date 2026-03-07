from .test_dif_v import scan_register_read_after_diff_write as srdw
from .test_r_w_r import scan_register_r_w_r as srwr
from .test_w_before_ffff import scan_register_read_after_diff_write as sdwf
from .test_fuzz_rw import scan_register_fuzz_rw as frw
from .test_read_chain import scan_register_read_chain as rc
from .test_write_chain import scan_register_write_chain as wc
from .test_oob_address import scan_oob_addresses as soob
from .find_trigger_register import scan_trigger_register as str


def run_test(START_ADDR, END_ADDR):
    result = str(START_ADDR, END_ADDR)
    result += srwr(START_ADDR, END_ADDR)
    result += sdwf(START_ADDR, END_ADDR)
    result += srdw(START_ADDR, END_ADDR)
    result += frw(START_ADDR, END_ADDR)
    result += rc(START_ADDR, END_ADDR)
    result += wc(START_ADDR, END_ADDR)
    result += soob()
    return result
