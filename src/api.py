from .test_dif_v import scan_register_read_after_diff_write as srdw
from .test_r_w_r import scan_register_r_w_r as srwr
from .test_w_before_ffff import scan_register_read_after_diff_write as sdwf


def run_test(START_ADDR, END_ADDR):
    result = srwr(START_ADDR, END_ADDR)
    result += sdwf(START_ADDR, END_ADDR)
    # result + srdw()
    return result
