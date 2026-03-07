import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from .data import addr_to_region
from datetime import datetime
from src.riscv_reg_block import reg_access

def render_register_access():
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
        except Exception as e:
            st.error(str(e))

    if col2.button("WRITE"):
        try:
            addr = int(addr_input, 16)
            value = int(value_input, 16)
            resp = reg_access(addr, value, "write")
            st.write("ACK:", resp["ack"])
            st.write("Value:", hex(resp["reg_value"]))
        except Exception as e:
            st.error(str(e))