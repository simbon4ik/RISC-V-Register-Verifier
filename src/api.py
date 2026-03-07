from test_dif_v import scan_register_read_after_diff_write as srdw
from test_r_w_r import scan_register_r_w_r as srwr
from test_w_before_ffff import scan_register_read_after_diff_write as sdwf
#trigger pattern - откуда баг

def run_test():
    result = sdwf(0x0000-0x0020)
    return result