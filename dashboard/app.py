from .data import load_register_events, load_bugs_data
from .views import (
    init_page,
    render_sidebar,
    render_kpi,
    render_region_heatmap,
    render_bugs_table,
    render_fsm_graph,
    render_filters,
    render_bug_selector,
)


def render():
    init_page()
    render_sidebar()

    df_events = load_register_events()

    bug_type_filter, region_filter = render_filters(df_events)

    df_filtered = df_events.copy()
    if bug_type_filter:
        df_filtered = df_filtered[
            df_filtered["bug_type"].isin(bug_type_filter)
        ]

    if region_filter:
        df_filtered = df_filtered[df_filtered["region"].isin(region_filter)]

    render_kpi(df_filtered)

    render_region_heatmap(df_filtered)

    # df_bugs = load_bugs_data()
    df_bugs_view = render_bugs_table(df_events, bug_type_filter, region_filter)
    selected_bug_idx = render_bug_selector(df_bugs_view)
    render_fsm_graph(
        df_bugs=df_bugs_view,
        selected_bug_idx=selected_bug_idx,
        key="fsm_graph_selected_bug",
    )
