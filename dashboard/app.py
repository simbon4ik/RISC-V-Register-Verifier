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
    render_register_access,
)


def render():
    init_page()
    render_sidebar()

    df_events = load_register_events()

    all_bug_types = sorted(df_events["bug_type"].unique())
    all_regions = sorted(df_events["region"].unique())

    bug_type_filter, region_filter = render_filters(
        all_bug_types,
        all_regions,
    )

    df_filtered = df_events.copy()
    if bug_type_filter:
        df_filtered = df_filtered[df_filtered["bug_type"].isin(bug_type_filter)]

    if region_filter:
        df_filtered = df_filtered[df_filtered["region"].isin(region_filter)]

    render_kpi(df_filtered)
    render_region_heatmap(df_filtered)

    df_bugs_view = render_bugs_table(df_events, bug_type_filter, region_filter)
    selected_bug_idx = render_bug_selector(df_bugs_view)
    render_fsm_graph(
        df_bugs=df_bugs_view,
        selected_bug_idx=selected_bug_idx,
        key="fsm_graph_selected_bug",
    )

    render_register_access()


if __name__ == "__main__":
    render()
