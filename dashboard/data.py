import pandas as pd
from .config import REGION_SIZE_BYTES, DEMO_BUGS
from src.api import run_test
from .config import (
    REGISTER_SPACE_START,
    REGISTER_SPACE_END,
)


def addr_to_region(addr: int, size: int = REGION_SIZE_BYTES) -> str:
    base = (addr // size) * size
    return f"0x{base:04X}-0x{base + size - 1:04X}"


def load_register_events() -> pd.DataFrame:
    events = run_test(REGISTER_SPACE_START, REGISTER_SPACE_END)
    df_events = pd.DataFrame(events)
    df_events["region"] = df_events["addr"].apply(addr_to_region)
    cols = ["region"] + [c for c in df_events.columns if c != "region"]
    df_events = df_events[cols]
    return df_events


def load_bugs_data() -> pd.DataFrame:
    return pd.DataFrame(DEMO_BUGS)
