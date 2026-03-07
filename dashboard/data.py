import pandas as pd
from .config import REGION_SIZE_BYTES, DEMO_EVENTS, DEMO_BUGS


def addr_to_region(addr: int, size: int = REGION_SIZE_BYTES) -> str:
    base = (addr // size) * size
    return f"0x{base:04X}-0x{base + size - 1:04X}"


def load_register_events() -> pd.DataFrame:
    df_events = pd.DataFrame(DEMO_EVENTS)
    df_events["region"] = df_events["addr"].apply(addr_to_region)
    return df_events


def load_bugs_data() -> pd.DataFrame:
    return pd.DataFrame(DEMO_BUGS)
