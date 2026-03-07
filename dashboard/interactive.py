"""Interactive register access controls for the Streamlit dashboard."""

import streamlit as st

from src.riscv_reg_block import reg_access  # pylint: disable=import-error


def render_register_access() -> None:
    """
    Render interactive widgets to read/write registers via reg_access API.
    """
    st.subheader("Interactive register access")
    addr_input = st.text_input("Address (hex)", "0x0")
    value_input = st.text_input("Value (hex)", "0x0")
    col1, col2 = st.columns(2)

    if col1.button("READ"):
        try:
            addr = int(addr_input, 16)
            resp = reg_access(addr, 0, "read")
            st.write("ACK:", resp["ack"])
            st.write("Value:", hex(resp["reg_value"]))
        except (ValueError, KeyError) as exc:
            st.error(str(exc))

    if col2.button("WRITE"):
        try:
            addr = int(addr_input, 16)
            value = int(value_input, 16)
            resp = reg_access(addr, value, "write")
            st.write("ACK:", resp["ack"])
            st.write("Value:", hex(resp["reg_value"]))
        except (ValueError, KeyError) as exc:
            st.error(str(exc))
