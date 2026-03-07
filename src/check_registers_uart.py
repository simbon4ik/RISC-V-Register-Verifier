from .riscv_reg_block import reg_access

RBR_ADDR = 0x0000
FCR_ADDR = 0x0018
LSR_ADDR = 0x001C
LCR_ADDR = 0x000C
DLL_ADDR = 0x0004
DLM_ADDR = 0x0008 
IIR_ADDR = 0x0014

def test_fifo_enable():
    # Тест бита включения FIFO
    reg_access(FCR_ADDR, 0x1, "write")
    resp = reg_access(FCR_ADDR, 0, "read")
    val = resp["reg_value"]
    if val & 0x1:
        print("Включили FIFO")
    else:
        print("BUG!!!!! FIFO не включён")

def test_fifo_reset():
    # Тест бита reset FIFO
    reg_access(FCR_ADDR, 0x6, "write")
    resp = reg_access(FCR_ADDR, 0, "read")
    val = resp["reg_value"]
    if val & 0x6:
        print("BUG!!! FIFO RESET")
    else:
        print("RESET OK")

def test_trigger_levels():
    # Тест бита trigger levels
    for level in range(4):
        value = level << 6
        reg_access(FCR_ADDR, value, "write")
        resp = reg_access(FCR_ADDR, 0, "read")
        read_val = resp["reg_value"]
        trig = (read_val >> 6) & 0x3
        if trig != level:
            print("BUG!!!")
        else:
            print("OK level")

# LSR

def test_lsr_read_only():
    before = reg_access(LSR_ADDR, 0, "read")["reg_value"]
    reg_access(LSR_ADDR, 0xFF, "write")
    after = reg_access(LSR_ADDR, 0, "read")["reg_value"]
    if before != after:
        print("BUG")
    else:
        print("OK")


def test_lsr_reset_values():
    # Тест LSR RESET
    val = reg_access(LSR_ADDR, 0, "read")["reg_value"]
    thre = (val >> 5) & 1
    temt = (val >> 6) & 1
    if thre != 1:
        print("BUG!")
    if temt != 1:
        print("BUG!")

def test_dr_clear_after_read():
    # Тест DR CLEAR
    lsr = reg_access(LSR_ADDR, 0, "read")["reg_value"]
    dr = lsr & 1
    if dr == 1:
        reg_access(RBR_ADDR, 0, "read")
        lsr2 = reg_access(LSR_ADDR, 0, "read")["reg_value"]
        if lsr2 & 1:
            print("BUG")
        else:
            print("OK")


def test_error_flags_clear():
    # Тест ERROR FLAGS
    val = reg_access(LSR_ADDR, 0, "read")["reg_value"]
    errors = val & 0x1E
    if errors != 0:
        reg_access(RBR_ADDR, 0, "read")
        val2 = reg_access(LSR_ADDR, 0, "read")["reg_value"]
        if val2 & 0x1E:
            print("BUG")
        else:
            print("OK")

def test_thre_temt_consistency():
    # Тест THRE/TEMT
    val = reg_access(LSR_ADDR, 0, "read")["reg_value"]
    thre = (val >> 5) & 1
    temt = (val >> 6) & 1
    if temt == 1 and thre == 0:
        print("BUG")

#LCR and DLL/DLM

DLAB_MASK = 0x80
DLAB_SHIFT = 7

def test_DLL_DLM():
    # Тест DLL/DLM
    val = reg_access(LCR_ADDR, 0, "read")
    dlab_val = (val & DLAB_MASK) >> DLAB_SHIFT
    if not dlab_val:
        if ((reg_access(DLL_ADDR, 0, "read")["ack"]) or (reg_access(DLM_ADDR, 0, "read")["ack"])):
            print("BUG")

IIR_VALUE = 0x8F

def test_ro_IIR():
    #Тест IIR
    result = reg_access(IIR_ADDR, IIR_VALUE, 'write')
    if result['ack']:
        print("BUG")

LSR_VALUE = 0xFF

def test_ro_LSR():
    #Тест LSR
    result = reg_access(LSR_ADDR, LSR_VALUE, 'write')
    if result['ack']:
        print("BUG")
