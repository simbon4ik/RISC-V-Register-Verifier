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
            st.dataframe(df_group, width="stretch")

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
    labels: dict[str, str] | None = None,
) -> go.Scatter:
    if labels is None:
        labels = {s: s for s in states}

    node_x, node_y, node_text, node_colors = zip(
        *[
            (
                positions[s][0],
                positions[s][1],
                labels.get(s, s),  # подпись для вершины
                "#d62728" if s in highlighted_states else FSM_NODE_COLOR,
            )
            for s in states
        ]
    )

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
    states=FSM_STATES,
    transitions=FSM_TRANSITIONS,
    positions=FSM_POSITIONS,
    title: str = FSM_TITLE,
    key: str = "fsm_graph",
):
    st.subheader(title)

    labels = {s: s for s in states}
    highlighted_states: set[str] = set()
    highlighted_edges: set[tuple[str, str]] = set()

    if df_bugs is not None and not df_bugs.empty:
        bug_indices = sorted(df_bugs.index.tolist())
        selected_idx = st.selectbox(
            "Bug id for FSM",
            options=bug_indices,
            key="fsm_bug_id_selector",
        )
        row = df_bugs.loc[selected_idx]

        bug_type = row.get("bug_type") or row.get("type")
        trigger = row.get("trigger_pattern")
        addr = row.get("addr")

        # пример: подсвечиваем и переименовываем проблемное состояние
        bug_state = row.get("fsm_bug_state")  # если ты это поле добавишь
        if bug_state in states:
            highlighted_states.add(bug_state)
            extra = f"{bug_type}" if bug_type is not None else "bug"
            labels[bug_state] = f"{bug_state}\n({extra})"

        # можно дополнительно добавить адрес/trigger в подписи других состояний
        if addr is not None:
            labels["IDLE"] = f"IDLE\n(addr {addr})"

        # если есть fsm_path_states — можем подсветить весь путь
        path_states = row.get("fsm_path_states")
        if isinstance(path_states, list):
            highlighted_states.update(path_states)
            # построить highlighted_edges из path_states, как раньше

    node_trace = _build_node_trace(states, positions, highlighted_states, labels)
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
