from results.systemrdl import *

try:
    addr_input = input("Введите адрес в HEX (например, 0x42): ")
    addr = int(addr_input, 16)
    resp = reg_relation(addr, 0, "read")            
    reg = Note(addr, resp["reg_value"], resp["status"], resp["ack"])
    print(f"Регистр ADDR=0x{reg.addr} Значение {reg.reg_value} Статус {reg.status} Ак {reg.ack}\n")

except Exception as e:
    print(f"Error! addr={addr}, error={e}")
