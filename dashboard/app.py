import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, ctx, no_update

from src.continents import CONTINENTS, aggregate_by_continent
from src.visualization import (
    load_data, get_latest_year, figure_to_base64,
    create_hdi_trend, create_top10_chart, create_bottom10_chart,
    create_continent_hdi_bar, create_continent_hdi_spread,
    create_life_expectancy_scatter, create_gni_scatter,
    create_mean_schooling_scatter, create_expected_schooling_scatter,
    create_hdi_distribution, create_continent_hdi_distribution,
    create_correlation_heatmap,
)

# =========================================================
# DATA
# =========================================================

df = load_data()
LATEST = get_latest_year(df)
FIRST = int(df["year"].min())
YEARS = sorted(df["year"].unique(), reverse=True)
COUNTRIES = sorted(df["country"].unique())
TOTAL_COUNTRIES = df["country"].nunique()

app = Dash(
    __name__,
    assets_folder=str(Path(__file__).resolve().parent / "assets"),
    title="HDI Dashboard",
)

GRAPH_CONFIG = {"displaylogo": False, "responsive": True}
LOADING_COLOUR = "#0077c8"


# =========================================================
# LAYOUT HELPERS
# =========================================================

def graph(graph_id, figure=None):
    # Start from an empty figure so the chart has a valid layout before the
    # first callback fills it in.
    figure = figure if figure is not None else go.Figure()
    return dcc.Loading(
        dcc.Graph(id=graph_id, figure=figure, config=GRAPH_CONFIG, className="graph"),
        type="circle",
        color=LOADING_COLOUR,
    )


def image(image_id):
    return dcc.Loading(
        html.Img(id=image_id, className="seaborn-img", alt=""),
        type="circle",
        color=LOADING_COLOUR,
    )


def kpi(label_id, value_id, sub_id):
    return html.Div(
        [
            html.Div(id=label_id, className="kpi-label"),
            html.Div(id=value_id, className="kpi-value"),
            html.Div(id=sub_id, className="kpi-sub"),
        ],
        className="kpi",
    )


def section(title, description, children, desc_id=None):
    desc_el = html.P(description, id=desc_id) if desc_id else html.P(description)
    return html.Section(
        [
            html.Div(
                [html.H2(title), desc_el],
                className="section-head",
            ),
            html.Div(children, className="chart-grid"),
        ],
        className="section",
    )


def rankings_section(top10_fig, bottom10_fig):
    """Built fresh on every global view, so the charts always size correctly.
    (Plotly cannot size a chart that is drawn inside a hidden container.)"""
    return section(
        "Rankings",
        f"The 10 highest and 10 lowest HDI scores among all "
        f"{TOTAL_COUNTRIES} countries in the selected year.",
        [
            html.Div(graph("top10-chart", top10_fig), className="chart-card"),
            html.Div(graph("bottom10-chart", bottom10_fig), className="chart-card"),
        ],
    )


def continental_section(bar_fig, spread_fig):
    """Built fresh whenever continents are selected so charts size cleanly."""
    return section(
        "Continental comparison",
        "Combined average HDI across all countries in each selected continent, "
        "alongside country-level spread in the selected year.",
        [
            html.Div(graph("continent-bar-chart", bar_fig), className="chart-card"),
            html.Div(graph("continent-spread-chart", spread_fig), className="chart-card"),
        ],
    )


app.layout = html.Div(
    [
        html.Header(
            html.Div(
                [
                    html.Div(
                        [
                            html.H1("Human Development Index Dashboard"),
                            html.P(
                                f"Human Development Report data for "
                                f"{TOTAL_COUNTRIES} countries, {FIRST}–{LATEST}"
                            ),
                        ]
                    ),
                    # html.Span("DV Lab project", className="project-tag"),
                ],
                className="header-inner",
            ),
            className="header",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Label("Year", htmlFor="year-dropdown"),
                                dcc.Dropdown(
                                    id="year-dropdown",
                                    options=[
                                        {"label": str(y), "value": int(y)}
                                        for y in YEARS
                                    ],
                                    value=LATEST,
                                    clearable=False,
                                ),
                            ],
                            className="filter year-filter",
                        ),
                        html.Div(
                            [
                                html.Label(
                                    "Continents to compare",
                                    htmlFor="continent-dropdown",
                                ),
                                dcc.Dropdown(
                                    id="continent-dropdown",
                                    options=[
                                        {"label": c, "value": c}
                                        for c in CONTINENTS
                                    ],
                                    value=[],
                                    multi=True,
                                    searchable=True,
                                    placeholder="Select continents to compare (clears countries).",
                                ),
                            ],
                            className="filter continent-filter",
                        ),
                        html.Div(
                            [
                                html.Label(
                                    "Countries to compare",
                                    htmlFor="country-dropdown",
                                ),
                                dcc.Dropdown(
                                    id="country-dropdown",
                                    options=[
                                        {"label": c, "value": c}
                                        for c in COUNTRIES
                                    ],
                                    value=[],
                                    multi=True,
                                    searchable=True,
                                    placeholder="All countries. Select countries to compare (clears continents).",
                                ),
                            ],
                            className="filter country-filter",
                        ),
                        html.Div(
                            [
                                html.Button(
                                    "Apply", id="apply-btn", n_clicks=0,
                                    className="btn primary",
                                ),
                                html.Button(
                                    "Reset", id="reset-btn", n_clicks=0,
                                    className="btn",
                                ),
                            ],
                            className="filter-actions",
                        ),
                    ],
                    className="filter-bar",
                ),
                html.Div(
                    [
                        html.Span(id="view-pill", className="pill"),
                        html.Span(
                            "You changed a filter. Press Apply to update the charts.",
                            id="pending-hint",
                            className="pending hidden",
                            role="status",
                        ),
                    ],
                    className="status-row",
                ),
            ],
            className="filter-wrap",
        ),
        html.Div(
            [
                html.P(id="filter-note", className="filter-note"),
                html.Div(
                    [
                        kpi("kpi-avg-label", "kpi-avg", "kpi-avg-sub"),
                        kpi("kpi-high-label", "kpi-high", "kpi-high-sub"),
                        kpi("kpi-low-label", "kpi-low", "kpi-low-sub"),
                        kpi("kpi-count-label", "kpi-count", "kpi-count-sub"),
                    ],
                    className="kpi-strip",
                ),
                section(
                    "HDI over time",
                    "Average HDI of all countries. Select continents or countries "
                    "to see their trends against the all-country average.",
                    [html.Div(graph("trend-chart"), className="chart-card wide")],
                ),
                html.Div(id="rankings-wrap"),
                section(
                    "Development indicators and HDI",
                    "Each point is one country in the selected year. "
                    "Hover over a point for exact values.",
                    [
                        html.Div(graph("life-chart"), className="chart-card"),
                        html.Div(graph("gni-chart"), className="chart-card"),
                        html.Div(graph("mean-school-chart"), className="chart-card"),
                        html.Div(graph("exp-school-chart"), className="chart-card"),
                    ],
                    desc_id="scatter-desc",
                ),
                section(
                    "Distribution and correlation",
                    "How HDI is spread across countries, and how closely the "
                    "indicators move together.",
                    [
                        html.Div(image("distribution-img"), id="distribution-card"),
                        html.Div(image("heatmap-img"), id="heatmap-card"),
                    ],
                    desc_id="dist-corr-desc",
                ),
                html.Footer(
                    "Source: UNDP Human Development Report. Some missing "
                    "values in the source data were filled by interpolation "
                    "during preprocessing.",
                    className="footer",
                ),
            ],
            className="page",
        ),
        dcc.Store(id="applied-filters"),
    ],
    className="app-shell",
)


# =========================================================
# CALLBACK HELPERS
# =========================================================

HIDDEN = "hidden"


def scoped(year, countries, continents=None):
    """Rows for the selected year, limited to chosen countries or continents."""
    data = df[df["year"] == year]
    if countries:
        chosen = data[data["country"].isin(countries)]
        if not chosen.empty:
            return chosen
    elif continents:
        chosen = data[data["continent"].isin(continents)]
        if not chosen.empty:
            return chosen
    return data


def mean_hdi(year, countries, continents=None):
    data = df[df["year"] == year]
    if countries:
        data = data[data["country"].isin(countries)]
    elif continents:
        data = data[data["continent"].isin(continents)]
    return data["HDI"].mean() if not data.empty else None


def _build_kpis(year, data, countries, continents):
    """Compute labels, values, and subtitles for the four KPI cards."""
    avg_now = data["HDI"].mean()
    avg_first = mean_hdi(FIRST, countries, continents)
    scope_word = (
        "selected continents"
        if continents
        else ("selected countries" if countries else "all countries")
    )
    avg_sub = (
        f"Average of {scope_word}"
        if year == FIRST or avg_first is None
        else f"{avg_now - avg_first:+.3f} since {FIRST}"
    )

    if continents:
        if len(continents) >= 2:
            cont_year = aggregate_by_continent(data, continents)
            top_c = cont_year.loc[cont_year["HDI"].idxmax()]
            bot_c = cont_year.loc[cont_year["HDI"].idxmin()]
            labels = (
                "Average HDI (continents)",
                "Highest continent",
                "Lowest continent",
                "Continents selected",
            )
            high_val = f"{top_c['HDI']:.3f}"
            high_sub = f"{top_c['continent']} ({int(top_c['country_count'])} countries)"
            low_val = f"{bot_c['HDI']:.3f}"
            low_sub = f"{bot_c['continent']} ({int(bot_c['country_count'])} countries)"
        else:
            high = data.loc[data["HDI"].idxmax()]
            low = data.loc[data["HDI"].idxmin()]
            labels = (
                "Continent average HDI",
                f"Highest in {continents[0]}",
                f"Lowest in {continents[0]}",
                "Continents selected",
            )
            high_val, high_sub = f"{high['HDI']:.3f}", high["country"]
            low_val, low_sub = f"{low['HDI']:.3f}", low["country"]
        count_val = f"{len(continents)}"
        count_sub = f"{data['country'].nunique()} of {TOTAL_COUNTRIES} countries combined"
        return labels, f"{avg_now:.3f}", avg_sub, high_val, high_sub, low_val, low_sub, count_val, count_sub

    high = data.loc[data["HDI"].idxmax()]
    low = data.loc[data["HDI"].idxmin()]
    if countries:
        labels = (
            "Average HDI (selected)",
            "Highest HDI (selected)",
            "Lowest HDI (selected)",
            "Countries selected",
        )
        count_sub = f"of {TOTAL_COUNTRIES} in the dataset"
    else:
        labels = ("Average HDI", "Highest HDI", "Lowest HDI", "Countries in dataset")
        count_sub = "Includes interpolated values"
    return (
        labels,
        f"{avg_now:.3f}",
        avg_sub,
        f"{high['HDI']:.3f}",
        high["country"],
        f"{low['HDI']:.3f}",
        low["country"],
        f"{data['country'].nunique()}",
        count_sub,
    )


def _build_view_text(year, countries, continents, country_count):
    """Return status pill text/class, filter note, and dynamic section captions."""
    default_scatter = (
        "Each point is one country in the selected year. "
        "Hover over a point for exact values."
    )
    default_dist_corr = (
        "How HDI is spread across countries, and how closely the "
        "indicators move together."
    )

    if continents:
        pill = (
            f"Comparing all {len(CONTINENTS)} continents"
            if len(continents) == len(CONTINENTS)
            else f"Comparing {len(continents)} "
                 f"{'continent' if len(continents) == 1 else 'continents'}"
        )
        note = (
            f"Showing continental comparisons for {year}. Each continent's "
            f"HDI and indicator averages are calculated by combining "
            f"{country_count} of {TOTAL_COUNTRIES} countries across "
            f"{', '.join(continents)} (UN M49 continent grouping, unweighted "
            f"country mean). Press Reset to return to the global view."
        )
        return (
            pill,
            "pill comparing",
            note,
            "Each point is one continent's combined average in the selected year. "
            "Hover over a point for exact values.",
            "How HDI is spread across countries within the selected continents, "
            "and how closely the indicators move together.",
        )

    if countries:
        pill = (
            f"Comparing {len(countries)} "
            f"{'country' if len(countries) == 1 else 'countries'}"
        )
        note = (
            f"Showing the trend and the four indicator plots for the "
            f"selected countries. Rankings and the HDI distribution compare "
            f"all {TOTAL_COUNTRIES} countries, so they are hidden while "
            f"countries are selected. The correlation heatmap still uses all "
            f"{TOTAL_COUNTRIES} countries. Press Reset to bring everything back."
        )
        return pill, "pill comparing", note, default_scatter, default_dist_corr

    return (
        f"Global view: all {TOTAL_COUNTRIES} countries, {year}",
        "pill",
        f"Showing all countries for {year}. The trend line always covers "
        f"{FIRST}–{LATEST}. Select either continents or countries to compare HDI trends.",
        default_scatter,
        default_dist_corr,
    )


# =========================================================
# EXCLUSIVE FILTER SYNC: either continents OR countries
# =========================================================

@app.callback(
    Output("continent-dropdown", "value", allow_duplicate=True),
    Output("country-dropdown", "value", allow_duplicate=True),
    Input("continent-dropdown", "value"),
    Input("country-dropdown", "value"),
    prevent_initial_call=True,
)
def sync_exclusive_filters(continents, countries):
    if not continents or not countries:
        return no_update, no_update
    if ctx.triggered_id == "continent-dropdown":
        return no_update, []
    if ctx.triggered_id == "country-dropdown":
        return [], no_update
    return no_update, no_update


# =========================================================
# MAIN CALLBACK: Apply / Reset
# =========================================================

@app.callback(
    Output("year-dropdown", "value"),
    Output("continent-dropdown", "value"),
    Output("country-dropdown", "value"),
    Output("applied-filters", "data"),
    Output("view-pill", "children"),
    Output("view-pill", "className"),
    Output("filter-note", "children"),
    Output("kpi-avg-label", "children"),
    Output("kpi-avg", "children"),
    Output("kpi-avg-sub", "children"),
    Output("kpi-high-label", "children"),
    Output("kpi-high", "children"),
    Output("kpi-high-sub", "children"),
    Output("kpi-low-label", "children"),
    Output("kpi-low", "children"),
    Output("kpi-low-sub", "children"),
    Output("kpi-count-label", "children"),
    Output("kpi-count", "children"),
    Output("kpi-count-sub", "children"),
    Output("trend-chart", "figure"),
    Output("rankings-wrap", "children"),
    Output("scatter-desc", "children"),
    Output("life-chart", "figure"),
    Output("gni-chart", "figure"),
    Output("mean-school-chart", "figure"),
    Output("exp-school-chart", "figure"),
    Output("dist-corr-desc", "children"),
    Output("distribution-card", "className"),
    Output("distribution-img", "src"),
    Output("distribution-img", "alt"),
    Output("heatmap-card", "className"),
    Output("heatmap-img", "src"),
    Output("heatmap-img", "alt"),
    Input("apply-btn", "n_clicks"),
    Input("reset-btn", "n_clicks"),
    State("year-dropdown", "value"),
    State("continent-dropdown", "value"),
    State("country-dropdown", "value"),
)
def update_dashboard(apply_clicks, reset_clicks, year, continents, countries):
    if ctx.triggered_id == "reset-btn" or year is None:
        year, continents, countries = LATEST, [], []
    continents = sorted(continents or [])
    countries = sorted(countries or [])

    # Never combine continents and countries in a single view.
    if continents and countries:
        continents = []

    data = scoped(year, countries, continents)
    (
        labels,
        avg_val,
        avg_sub,
        high_val,
        high_sub,
        low_val,
        low_sub,
        count_val,
        count_sub,
    ) = _build_kpis(year, data, countries, continents)
    pill, pill_class, note, scatter_desc, dist_corr_desc = _build_view_text(
        year, countries, continents, data["country"].nunique()
    )

    trend = create_hdi_trend(df, countries, year, continents)
    life = create_life_expectancy_scatter(df, year, countries, continents)
    gni = create_gni_scatter(df, year, countries, continents)
    mean_school = create_mean_schooling_scatter(df, year, countries, continents)
    exp_school = create_expected_schooling_scatter(df, year, countries, continents)

    if continents:
        rankings = continental_section(
            create_continent_hdi_bar(df, year, continents),
            create_continent_hdi_spread(df, year, continents),
        )
        dist_class = "chart-card"
        dist_src = figure_to_base64(
            create_continent_hdi_distribution(df, year, continents)
        )
        dist_alt = f"HDI distribution across selected continents in {year}"
        heatmap_class = "chart-card"
        heatmap_src = figure_to_base64(
            create_correlation_heatmap(df, year, continents)
        )
        heatmap_alt = (
            f"Correlation heatmap of HDI indicators for selected continents in {year}"
        )
    elif countries:
        rankings = None
        dist_class = "hidden"
        dist_src = dist_alt = no_update
        heatmap_class = "chart-card wide centered"
        heatmap_src = figure_to_base64(create_correlation_heatmap(df, year))
        heatmap_alt = f"Correlation heatmap of HDI indicators in {year}"
    else:
        rankings = rankings_section(
            create_top10_chart(df, year), create_bottom10_chart(df, year)
        )
        dist_class = "chart-card"
        dist_src = figure_to_base64(create_hdi_distribution(df, year))
        dist_alt = f"Histogram of HDI values across countries in {year}"
        heatmap_class = "chart-card"
        heatmap_src = figure_to_base64(create_correlation_heatmap(df, year))
        heatmap_alt = f"Correlation heatmap of HDI indicators in {year}"

    return (
        year,
        continents,
        countries,
        {"year": year, "continents": continents, "countries": countries},
        pill,
        pill_class,
        note,
        labels[0], avg_val, avg_sub,
        labels[1], high_val, high_sub,
        labels[2], low_val, low_sub,
        labels[3], count_val, count_sub,
        trend,
        rankings,
        scatter_desc,
        life,
        gni,
        mean_school,
        exp_school,
        dist_corr_desc,
        dist_class,
        dist_src,
        dist_alt,
        heatmap_class,
        heatmap_src,
        heatmap_alt,
    )


# =========================================================
# HINT CALLBACK: filters changed but not applied yet
# =========================================================

@app.callback(
    Output("pending-hint", "className"),
    Input("year-dropdown", "value"),
    Input("continent-dropdown", "value"),
    Input("country-dropdown", "value"),
    State("applied-filters", "data"),
)
def show_pending_hint(year, continents, countries, applied):
    if not applied:
        return "pending hidden"
    same = (
        year == applied["year"]
        and sorted(continents or []) == sorted(applied.get("continents", []))
        and sorted(countries or []) == sorted(applied["countries"])
    )
    return "pending hidden" if same else "pending"


if __name__ == "__main__":
    app.run(debug=True)