"""
Interactive module for RISC-V Register Verifier
"""
from .config import Note
from .riscv_reg_block import reg_access


addr_input = input("Введите адрес в HEX (например, 0x42): ")
addr = int(addr_input, 16)
resp = reg_access(addr, 0, "read")
reg = Note(addr, resp["reg_value"],resp["ack"])
print(f"Регистр ADDR=0x{reg.addr} Значение {reg.reg_value} Ак {reg.ack}\n")
