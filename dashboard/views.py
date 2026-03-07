import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from .data import addr_to_region
from datetime import datetime

from .config import (
    APP_TITLE,
    PAGE_LAYOUT,
    FSM_TITLE,
    FSM_STATES,
    FSM_TRANSITIONS,
    FSM_POSITIONS,
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

    if bug_type_filter:
        if "bug_type" in df.columns:
            df = df[df["bug_type"].isin(bug_type_filter)]
        elif "type" in df.columns:
            df = df[df["type"].isin(bug_type_filter)]

    st.dataframe(df, width="stretch")
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


def _get_bug_type(
    df_bugs: pd.DataFrame | None,
    selected_bug_idx: int | None,
) -> str | None:
    if (
        df_bugs is None
        or selected_bug_idx is None
        or not (0 <= selected_bug_idx < len(df_bugs))
    ):
        return None

    row = df_bugs.iloc[selected_bug_idx]
    value = row.get("bug_type") or row.get("type")
    return str(value) if value is not None else None


def _get_highlighted_elements(
    bug_type_value: str | None,
) -> tuple[set[str], set[tuple[str, str]]]:
    highlighted_states: set[str] = set()
    highlighted_edges: set[tuple[str, str]] = set()

    if not bug_type_value:
        return highlighted_states, highlighted_edges

    bt = bug_type_value.lower()
    if "deadlock" in bt:
        highlighted_edges.add(("WAIT_ACK", "DEADLOCK"))
        highlighted_states.update({"WAIT_ACK", "DEADLOCK"})
    if "stale" in bt:
        highlighted_states.add("READ")
    if "overflow" in bt or "glitch" in bt:
        highlighted_states.add("WRITE")

    return highlighted_states, highlighted_edges


def _build_node_trace(
    states,
    positions,
    highlighted_states: set[str],
) -> go.Scatter:
    node_x, node_y, node_text, node_colors = zip(*[
        (
            positions[s][0],
            positions[s][1],
            s,
            "#d62728" if s in highlighted_states else FSM_NODE_COLOR,
        )
        for s in states
    ])

    return go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=node_text,
        textposition="top center",
        marker=dict(size=FSM_NODE_SIZE, color=node_colors),
        hoverinfo="text",
        showlegend=False,
    )


def _build_edge_traces(
    transitions,
    positions,
    highlighted_edges: set[tuple[str, str]],
) -> tuple[go.Scatter, go.Scatter, list[tuple[float, float, str]]]:
    edge_x, edge_y, edge_x_hi, edge_y_hi, edge_text = [], [], [], [], []

    for src, dst, label in transitions:
        x0, y0 = positions[src]
        x1, y1 = positions[dst]

        xs, ys = [x0, x1, None], [y0, y1, None]
        if (src, dst) in highlighted_edges:
            edge_x_hi += xs
            edge_y_hi += ys
        else:
            edge_x += xs
            edge_y += ys

        edge_text.append(((x0 + x1) / 2.0, (y0 + y1) / 2.0, label))

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line=dict(color=FSM_EDGE_COLOR, width=FSM_EDGE_WIDTH),
        hoverinfo="none",
        showlegend=False,
    )

    edge_hi_trace = go.Scatter(
        x=edge_x_hi,
        y=edge_y_hi,
        mode="lines",
        line=dict(color="#d62728", width=FSM_EDGE_WIDTH + 1),
        hoverinfo="none",
        showlegend=False,
    )

    return edge_trace, edge_hi_trace, edge_text


def _build_label_trace(
    edge_text: list[tuple[float, float, str]],
) -> go.Scatter:
    if not edge_text:
        return go.Scatter(x=[], y=[], mode="text", text=[])

    label_x, label_y, label_text = zip(*edge_text)
    return go.Scatter(
        x=label_x,
        y=label_y,
        mode="text",
        text=label_text,
        textposition="middle center",
        hoverinfo="none",
        showlegend=False,
    )


def render_fsm_graph(
    df_bugs: pd.DataFrame | None = None,
    selected_bug_idx: int | None = None,
    states=FSM_STATES,
    transitions=FSM_TRANSITIONS,
    positions=FSM_POSITIONS,
    title: str = FSM_TITLE,
    key: str = "fsm_graph",
):
    st.subheader(title)

    bug_type_value = _get_bug_type(df_bugs, selected_bug_idx)
    highlighted_states, highlighted_edges = _get_highlighted_elements(
        bug_type_value
        )

    node_trace = _build_node_trace(states, positions, highlighted_states)
    edge_trace, edge_hi_trace, edge_text = _build_edge_traces(
        transitions, positions, highlighted_edges
    )
    label_trace = _build_label_trace(edge_text)

    fig = go.Figure(data=[edge_trace, edge_hi_trace, node_trace, label_trace])
    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=FSM_MARGIN,
        height=FSM_FIG_HEIGHT,
    )

    st.plotly_chart(fig, width="stretch", key=key)


def render_filters(df_events: pd.DataFrame):
    st.sidebar.subheader("Filters")

    bug_types = sorted(df_events["bug_type"].unique())
    bug_type_filter = st.sidebar.multiselect(
        "Bug types",
        options=bug_types,
        default=bug_types,
    )

    if "region" in df_events.columns:
        regions = sorted(df_events["region"].unique())
        region_filter = st.sidebar.multiselect(
            "Address regions",
            options=regions,
            default=regions,
        )
    else:
        region_filter = []

    return bug_type_filter, region_filter


def render_bug_selector(df_bugs: pd.DataFrame | None) -> int | None:
    if df_bugs is None or df_bugs.empty:
        return None

    st.sidebar.subheader("Bug details")
    bug_indices = df_bugs.index.tolist()
    selected_idx = st.sidebar.selectbox("Bug index", bug_indices)
    return selected_idx
