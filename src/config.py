"""
Module for definition Note and read_to_file
"""
class Note:
    """
    Class for reg_access
    """
    def __init__(self, addr: int, value: int, ack: bool):
        self.addr = addr
        self.reg_value = value
        self.ack = ack
    def get_addr(self):
        """
        Get addr
        """
        return self.addr
    def get_reg_value(self):
        """
        Get reg_value
        """
        return self.reg_value
    def get_ack(self):
        """
        Get ack
        """
        return self.ack



def read_to_file(file_name, found_registers, errors):
    """
    Function for read to file
    """
    with open(file_name, "w", encoding="utf-8") as f:
        f.write("Registers without ack error\n")
        for reg in found_registers:
            if reg.ack:
                f.write(
                    f"ADDR=0x{reg.addr:04x} VAL={reg.reg_value:04x} ACK={reg.ack}\n"
                    )
        f.write("Registers with ack error\n")
        for reg in found_registers:
            if reg.ack is False:
                f.write(
                    f"ADDR=0x{reg.addr:04x} VAL={reg.reg_value:04x} ACK={reg.ack}\n"
                    )
        f.write("Registers with exception\n")
        for addr, err in errors:
            f.write(f"ADDR=0x{addr:04x} ERROR={err}\n")

    return found_registers, errors
