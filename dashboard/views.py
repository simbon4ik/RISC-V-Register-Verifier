import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from .data import addr_to_region
from datetime import datetime
from src.riscv_reg_block import reg_access

from .config import (
    APP_TITLE,
    PAGE_LAYOUT,
    FSM_TITLE,
    FSM_NODE_SIZE,
    FSM_NODE_COLOR,
    FSM_EDGE_COLOR,
    FSM_EDGE_WIDTH,
    FSM_FIG_HEIGHT,
    SIDEBAR_HEADER,
    SIDEBAR_RUN_BUTTON,
    SIDEBAR_RUN_MESSAGE,
    KPI_LABEL_REGS_WITH_BUGS,
    KPI_LABEL_BUG_PATTERNS,
    KPI_LABEL_BUGS_FOUND,
    BUGS_TABLE_TITLE,
    REGION_HEATMAP_TITLE,
    REGION_HEATMAP_X_TITLE,
    REGION_HEATMAP_Y_TITLE,
    REGION_HEATMAP_COLORBAR_TITLE,
    REGION_HEATMAP_COLOR_SCALE,
    FSM_MARGIN,
)


def init_page():
    st.set_page_config(page_title=APP_TITLE, layout=PAGE_LAYOUT)
    st.title(APP_TITLE)


def render_sidebar():
    st.sidebar.header(SIDEBAR_HEADER)
    if st.sidebar.button(SIDEBAR_RUN_BUTTON):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.sidebar.write(f"{SIDEBAR_RUN_MESSAGE} {now}")


def render_kpi(df_events: pd.DataFrame):
    unique_regs = df_events["addr"].nunique()
    bugs_total = len(df_events)
    bug_patterns = df_events["bug_type"].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric(KPI_LABEL_REGS_WITH_BUGS, str(unique_regs))
    col2.metric(KPI_LABEL_BUG_PATTERNS, str(bug_patterns))
    col3.metric(KPI_LABEL_BUGS_FOUND, str(bugs_total))


def render_bugs_table(
    df_bugs: pd.DataFrame,
    bug_type_filter: list[str] | None = None,
    region_filter: list[str] | None = None,
) -> pd.DataFrame:
    st.subheader(BUGS_TABLE_TITLE)

    df = df_bugs.copy()

    if "region" not in df.columns and "addr" in df.columns:
        def addr_hex_to_region(addr_str: str) -> str:
            first_addr = str(addr_str).split("/")[0]
            addr_int = int(first_addr, 16)
            return addr_to_region(addr_int)

        region_series = df["addr"].apply(addr_hex_to_region)
        df.insert(0, "region", region_series)

    if region_filter and "region" in df.columns:
        df = df[df["region"].isin(region_filter)]

    bug_type_col = None
    if "bug_type" in df.columns:
        bug_type_col = "bug_type"
    elif "type" in df.columns:
        bug_type_col = "type"

    if bug_type_filter and bug_type_col is not None:
        df = df[df[bug_type_col].isin(bug_type_filter)]

    if bug_type_col is None:
        st.dataframe(df, width="stretch")
        return df

    sort_cols = [bug_type_col]
    if "region" in df.columns:
        sort_cols.append("region")
    if "addr" in df.columns:
        sort_cols.append("addr")
    df = df.sort_values(by=sort_cols)

    for bt_value, df_group in df.groupby(bug_type_col):
        total = len(df_group)

        with st.expander(f"{bug_type_col} = {bt_value} ({total} bugs)"):

            if "addr" in df_group.columns:
                agg = (
                    df_group.groupby("addr")
                    .size()
                    .reset_index(name="count")
                    .sort_values("count", ascending=False)
                )
                agg_total = agg["count"].sum()
                agg["share"] = (agg["count"] / agg_total * 100).round(1)

                agg = agg.rename(
                    columns={
                        "addr": "Address",
                        "count": "Occurrences",
                        "share": "Share, %",
                    }
                )

                st.markdown("**Summary by address**")
                st.dataframe(agg, width="stretch")

            st.markdown("**Details**")

            cols_to_show = [c for c in df_group.columns if c != "FSM"]
            st.dataframe(df_group[cols_to_show], width="stretch")

    return df


def render_region_heatmap(df_events: pd.DataFrame):
    df = df_events.copy()
    df_counts = (
        df.groupby(["region", "bug_type"])
        .size()
        .reset_index(name="count")
    )

    fig = px.density_heatmap(
        df_counts,
        x="bug_type",
        y="region",
        z="count",
        color_continuous_scale=REGION_HEATMAP_COLOR_SCALE,
    )

    fig.update_layout(
        xaxis_title=REGION_HEATMAP_X_TITLE,
        yaxis_title=REGION_HEATMAP_Y_TITLE,
        coloraxis_colorbar_title=REGION_HEATMAP_COLORBAR_TITLE,
        yaxis=dict(autorange="reversed"),
    )

    st.subheader(REGION_HEATMAP_TITLE)
    st.plotly_chart(fig, width="stretch", key="region_heatmap")


def _build_node_trace_for_path(path: list[str]) -> go.Scatter:
    states = list(dict.fromkeys(path))
    positions = {s: (i, 0.0) for i, s in enumerate(states)}

    node_x, node_y, node_colors, node_text = [], [], [], []
    n = len(states)

    for idx, s in enumerate(states):
        x, y = positions[s]
        node_x.append(x)
        node_y.append(y)
        node_text.append(s)

        if idx == 0:
            color = "#2ca02c"
        elif idx == n - 1:
            color = "#d62728"
        else:
            color = FSM_NODE_COLOR

        node_colors.append(color)

    return go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers",
        marker=dict(size=FSM_NODE_SIZE, color=node_colors),
        text=node_text,
        hoverinfo="text",
        showlegend=False,
    ), positions


def _build_edge_trace_for_path(
        path: list[str], positions: dict[str, tuple[float, float]]
        ) -> go.Scatter:
    edge_x, edge_y = [], []
    for s0, s1 in zip(path, path[1:]):
        x0, y0 = positions[s0]
        x1, y1 = positions[s1]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    return go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line=dict(color=FSM_EDGE_COLOR, width=FSM_EDGE_WIDTH),
        hoverinfo="none",
        showlegend=False,
    )


def render_fsm_graph(
    df_bugs: pd.DataFrame | None = None,
    title: str = FSM_TITLE,
    key: str = "fsm_graph",
):
    st.subheader(title)

    if df_bugs is None or df_bugs.empty or "FSM" not in df_bugs.columns:
        st.info("No FSM data for bugs")
        return

    bug_indices = sorted(df_bugs.index.tolist())
    selected_idx = st.selectbox(
        "Bug id for FSM",
        options=bug_indices,
        key="fsm_bug_id_selector",
    )
    row = df_bugs.loc[selected_idx]

    fsm_path = row.get("FSM")
    if not isinstance(fsm_path, list) or len(fsm_path) < 2:
        st.info("FSM path is empty or too short")
        return

    node_trace, positions = _build_node_trace_for_path(fsm_path)
    edge_trace = _build_edge_trace_for_path(fsm_path, positions)

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=FSM_MARGIN,
        height=FSM_FIG_HEIGHT,
    )

    st.plotly_chart(fig, width="stretch", key=key)


def render_filters(
    all_bug_types: list[str],
    all_regions: list[str],
):
    st.sidebar.subheader("Filters")

    bug_type_filter = st.sidebar.multiselect(
        "Bug types",
        options=all_bug_types,
        default=all_bug_types,
    )

    region_filter = st.sidebar.multiselect(
        "Address regions",
        options=all_regions,
        default=all_regions,
    )

    return bug_type_filter, region_filter


def render_bug_selector(df_bugs: pd.DataFrame | None) -> int | None:
    if df_bugs is None or df_bugs.empty:
        return None

    st.sidebar.subheader("Bug details")
    bug_indices = df_bugs.index.tolist()
    selected_idx = st.sidebar.selectbox("Bug index", bug_indices)
    return selected_idx


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
