from systemrdl import RDLCompiler  # см. в документации systemrdl-compiler
from systemrdl.node import AddrmapNode


def load_addrmap(path: str) -> AddrmapNode:
    """
    Парсит SystemRDL и возвращает корневой addrmap.
    """
    rdlc = RDLCompiler()
    rdlc.compile_file(path)
    root = rdlc.elaborate()
    # предполагаем, что верхний объект — addrmap
    return next(root.top.children())
