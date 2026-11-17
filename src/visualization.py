"""
HDI chart functions.

Charts 1-7 : Plotly Express (interactive)
Charts 8-9 : Seaborn + Matplotlib (rendered as images)

Importing this module does not display anything.
Run it directly (python src/visualization.py) to preview all charts.
"""

import base64
import io
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from matplotlib.figure import Figure

from src.continents import (
    CONTINENTS,
    add_continent_column,
    aggregate_by_continent,
)


# =========================================================
# 1. DATA LOADING
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

file_path = BASE_DIR / "data" / "processed" / "HDI_cleaned.csv"

CORRELATION_COLUMNS = [
    "HDI",
    "Life_Expectancy",
    "Mean_Years_Schooling",
    "Expected_Years_Schooling",
    "GNI_Per_Capita",
]

# Colour-blind-safe palette (Okabe-Ito), used for every chart.
PALETTE = [
    "#0072B2",  # blue
    "#D55E00",  # vermilion
    "#009E73",  # green
    "#CC79A7",  # pink
    "#E69F00",  # orange
    "#56B4E9",  # sky blue
    "#6B7280",  # grey
    "#000000",  # black
]

CONTINENT_COLOURS = {
    "Africa": PALETTE[1],
    "Asia": PALETTE[4],
    "Europe": PALETTE[0],
    "North America": PALETTE[2],
    "Oceania": PALETTE[5],
    "South America": PALETTE[3],
}

AVERAGE_LINE_COLOUR = "#6B7280"
MAX_LABELLED_POINTS = 12


def load_data() -> pd.DataFrame:
    """Read the cleaned HDI dataset and attach the continent column."""
    return add_continent_column(pd.read_csv(file_path))


def get_latest_year(df: pd.DataFrame) -> int:
    return int(df["year"].max())


# =========================================================
# 2. HELPERS
# =========================================================

def _year_slice(df: pd.DataFrame, year: int) -> pd.DataFrame:
    return df[df["year"] == year].copy()


def _apply_white_layout(fig: go.Figure) -> go.Figure:
    """Plain white plot area with dark, readable text."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        font={"color": "#1f2933"},
        title={"font": {"size": 16}},
        margin={"l": 60, "r": 24, "t": 60, "b": 50},
        colorway=PALETTE,
    )
    return fig


def _empty_plotly_figure(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font={"size": 14},
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return _apply_white_layout(fig)


def figure_to_base64(fig: Figure, dpi: int = 150) -> str:
    """Convert a Matplotlib figure to a PNG data URI for Dash html.Img."""
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=dpi, bbox_inches="tight",
                facecolor="white")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def _empty_matplotlib_figure(message: str) -> Figure:
    fig = Figure(figsize=(10, 6))
    ax = fig.subplots()
    ax.text(0.5, 0.5, message, ha="center", va="center", fontsize=12)
    ax.set_axis_off()
    return fig


def _trend_title(countries, continents, first_year: int, last_year: int) -> str:
    period = f"{first_year}–{last_year}"
    if continents:
        if len(continents) == len(CONTINENTS):
            return f"Continental HDI Trend: All {len(CONTINENTS)} Continents ({period})"
        if len(continents) <= 3:
            return f"Continental HDI Trend: {', '.join(continents)} ({period})"
        return f"Continental HDI Trend: {len(continents)} selected continents ({period})"
    if not countries:
        return f"Average HDI Trend ({period})"
    if len(countries) <= 3:
        return f"HDI Trend: {', '.join(countries)} ({period})"
    return f"HDI Trend: {len(countries)} selected countries ({period})"


def _add_global_average_trace(fig: go.Figure, yearly_hdi: pd.DataFrame) -> None:
    fig.add_trace(
        go.Scatter(
            x=yearly_hdi["year"],
            y=yearly_hdi["HDI"],
            mode="lines",
            name="All-country average",
            line={"color": AVERAGE_LINE_COLOUR, "dash": "dash", "width": 2},
            hovertemplate=(
                "<b>All-country average</b><br>"
                "Year: %{x}<br>HDI: %{y:.3f}<extra></extra>"
            ),
        )
    )


def _apply_bottom_legend(fig: go.Figure) -> None:
    fig.update_layout(
        legend={
            "orientation": "h",
            "yanchor": "top", "y": -0.22,
            "xanchor": "left", "x": 0,
            "title": {"text": ""},
        },
        yaxis_title="Human Development Index",
    )


# =========================================================
# 3. CHART 1 - HDI TREND (PLOTLY, FULL 1990-2023)
# =========================================================
# No countries/continents : average HDI of all countries.
# Countries selected      : one line per country + dashed all-country average.
# Continents selected     : one line per continent (mean of its countries)
#                           + dashed all-country average.
# `year` (optional) draws a dotted marker for the selected year.

def create_hdi_trend(
    df: pd.DataFrame, countries=None, year=None, continents=None
) -> go.Figure:
    first_year = int(df["year"].min())
    last_year = int(df["year"].max())

    yearly_hdi = df.groupby("year", as_index=False)["HDI"].mean()

    if continents:
        cont_df = aggregate_by_continent(df, continents)
        if cont_df.empty:
            return _empty_plotly_figure("No data for the selected continents")

        fig = go.Figure()
        for continent in sorted(cont_df["continent"].unique()):
            sub = cont_df[cont_df["continent"] == continent]
            fig.add_trace(
                go.Scatter(
                    x=sub["year"],
                    y=sub["HDI"],
                    mode="lines+markers",
                    name=continent,
                    line={
                        "color": CONTINENT_COLOURS.get(continent, PALETTE[0]),
                        "width": 2.5,
                    },
                    customdata=sub["country_count"],
                    hovertemplate=(
                        "<b>%{fullData.name}</b> (%{customdata} countries)<br>"
                        "Year: %{x}<br>Average HDI: %{y:.3f}<extra></extra>"
                    ),
                )
            )

        _add_global_average_trace(fig, yearly_hdi)
        fig.update_layout(
            title=_trend_title(None, continents, first_year, last_year),
            xaxis_title="Year",
        )
        _apply_bottom_legend(fig)

    elif countries:
        data = df[df["country"].isin(countries)].sort_values(["country", "year"])

        if data.empty:
            return _empty_plotly_figure("No data for the selected countries")

        fig = px.line(
            data,
            x="year",
            y="HDI",
            color="country",
            markers=True,
            title=_trend_title(countries, None, first_year, last_year),
            labels={"year": "Year", "HDI": "HDI", "country": "Country"},
            color_discrete_sequence=PALETTE,
        )

        fig.update_traces(
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "Year: %{x}<br>HDI: %{y:.3f}<extra></extra>"
            )
        )
        _add_global_average_trace(fig, yearly_hdi)
        _apply_bottom_legend(fig)

    else:
        fig = px.line(
            yearly_hdi,
            x="year",
            y="HDI",
            markers=True,
            title=_trend_title(None, None, first_year, last_year),
            labels={"year": "Year", "HDI": "Average HDI"},
            color_discrete_sequence=PALETTE,
        )

        fig.update_traces(
            hovertemplate="Year: %{x}<br>Average HDI: %{y:.3f}<extra></extra>"
        )

    if year is not None:
        fig.add_vline(x=year, line_dash="dot", line_color="#9AA5B1", line_width=1.5)

    return _apply_white_layout(fig)


# =========================================================
# 4. CHARTS 2-3 - TOP / BOTTOM 10 (PLOTLY)
# =========================================================
# Always ranked across ALL countries for the selected year.

def _create_ranking_chart(df, year, smallest: bool) -> go.Figure:
    data = _year_slice(df, year)

    if data.empty:
        return _empty_plotly_figure(f"No data available for {year}")

    if smallest:
        ranked = data.nsmallest(10, "HDI").sort_values("HDI")
        title = f"Bottom 10 Countries by HDI ({year})"
    else:
        ranked = data.nlargest(10, "HDI").sort_values("HDI")
        title = f"Top 10 Countries by HDI ({year})"

    fig = px.bar(
        ranked,
        x="HDI",
        y="country",
        orientation="h",
        title=title,
        labels={"HDI": "Human Development Index", "country": "Country"},
        hover_name="country",
        color_discrete_sequence=PALETTE,
    )

    fig.update_traces(
        hovertemplate="Country: %{y}<br>HDI: %{x:.3f}<extra></extra>",
        texttemplate="%{x:.3f}",
        textposition="outside",
        cliponaxis=False,
    )

    # Fixed 0-1 scale so bars are comparable between years.
    fig.update_xaxes(range=[0, 1.1], dtick=0.2)

    return _apply_white_layout(fig)


def create_top10_chart(df: pd.DataFrame, year: int) -> go.Figure:
    return _create_ranking_chart(df, year, smallest=False)


def create_bottom10_chart(df: pd.DataFrame, year: int) -> go.Figure:
    return _create_ranking_chart(df, year, smallest=True)


# =========================================================
# 4B. CONTINENTAL COMPARISON CHARTS (PLOTLY)
# =========================================================

def create_continent_hdi_bar(
    df: pd.DataFrame, year: int, continents=None
) -> go.Figure:
    year_df = add_continent_column(_year_slice(df, year))
    cont_df = aggregate_by_continent(year_df, continents)

    if cont_df.empty:
        return _empty_plotly_figure(f"No continental data available for {year}")

    cont_df = cont_df.sort_values("HDI", ascending=True)
    ordered_continents = cont_df["continent"].tolist()
    global_avg = float(year_df["HDI"].mean())

    fig = px.bar(
        cont_df,
        x="HDI",
        y="continent",
        color="continent",
        orientation="h",
        title=f"Average HDI by Continent ({year})",
        labels={"HDI": "Average Human Development Index", "continent": "Continent"},
        color_discrete_map=CONTINENT_COLOURS,
        custom_data=["country_count", "Life_Expectancy", "GNI_Per_Capita"],
    )

    fig.update_traces(
        texttemplate="%{x:.3f}",
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{y}</b> (%{customdata[0]} countries)<br>"
            "Average HDI: %{x:.3f}<br>"
            "Avg Life Expectancy: %{customdata[1]:.1f} yrs<br>"
            "Avg GNI Per Capita: %{customdata[2]:,.0f}"
            "<extra></extra>"
        ),
    )

    fig.add_vline(
        x=global_avg,
        line_dash="dash",
        line_color=AVERAGE_LINE_COLOUR,
        line_width=1.5,
    )
    fig.add_annotation(
        x=global_avg,
        y=1.02,
        xref="x",
        yref="paper",
        text=f"Global avg: {global_avg:.3f}",
        showarrow=False,
        yanchor="bottom",
        font={"size": 11, "color": "#3e4c59"},
    )

    fig.update_layout(showlegend=False)
    fig.update_xaxes(range=[0, 1.1], dtick=0.2)
    fig.update_yaxes(categoryorder="array", categoryarray=ordered_continents)
    fig = _apply_white_layout(fig)
    fig.update_layout(margin={"t": 76})
    return fig


def create_continent_hdi_spread(
    df: pd.DataFrame, year: int, continents=None
) -> go.Figure:
    data = add_continent_column(_year_slice(df, year)).dropna(subset=["continent"])
    if continents:
        data = data[data["continent"].isin(continents)]

    if data.empty:
        return _empty_plotly_figure(f"No continental data available for {year}")

    ordered_continents = (
        data.groupby("continent")["HDI"].mean().sort_values(ascending=True).index.tolist()
    )

    fig = px.box(
        data,
        x="HDI",
        y="continent",
        color="continent",
        points="all",
        hover_name="country",
        hover_data={"HDI": ":.3f", "continent": False},
        color_discrete_map=CONTINENT_COLOURS,
        title=f"HDI Spread Across Countries by Continent ({year})",
        labels={"HDI": "Human Development Index", "continent": "Continent"},
    )

    fig.update_traces(marker={"size": 5, "opacity": 0.65})
    fig.update_layout(showlegend=False)
    fig.update_xaxes(range=[0, 1.05], dtick=0.2)
    fig.update_yaxes(categoryorder="array", categoryarray=ordered_continents)

    return _apply_white_layout(fig)


# =========================================================
# 5. CHARTS 4-7 - INDICATOR VS HDI SCATTER PLOTS (PLOTLY)
# =========================================================

_CONTINENT_TEXT_POS = {
    "Europe": "top left",
    "South America": "top left",
    "North America": "bottom right",
    "Asia": "bottom left",
    "Oceania": "middle right",
    "Africa": "top right",
}


def _create_indicator_scatter(
    df: pd.DataFrame,
    year: int,
    x_column: str,
    x_label: str,
    title: str,
    x_hover_format: str,
    unit_suffix: str = "",
    countries=None,
    continents=None,
) -> go.Figure:
    year_df = _year_slice(df, year)

    if continents:
        cont_df = aggregate_by_continent(year_df, continents)
        if cont_df.empty:
            return _empty_plotly_figure("No data for the selected continents")

        fig = go.Figure()
        for continent in sorted(cont_df["continent"].unique()):
            row = cont_df[cont_df["continent"] == continent]
            fig.add_trace(
                go.Scatter(
                    x=row[x_column],
                    y=row["HDI"],
                    mode="markers+text",
                    name=continent,
                    text=[continent],
                    textposition=_CONTINENT_TEXT_POS.get(continent, "top center"),
                    marker={
                        "size": 13,
                        "opacity": 0.9,
                        "color": CONTINENT_COLOURS.get(continent, PALETTE[0]),
                    },
                    customdata=row["country_count"],
                    hovertemplate=(
                        "<b>%{fullData.name}</b> (%{customdata} countries)<br>"
                        f"Avg {x_label}: %{{x:{x_hover_format}}}{unit_suffix}<br>"
                        "Avg HDI: %{y:.3f}"
                        "<extra></extra>"
                    ),
                )
            )

        fig.update_layout(
            title=f"{title} — Continental Averages ({year})",
            xaxis_title=f"Average {x_label}",
            yaxis_title="Average Human Development Index",
            legend={
                "orientation": "h",
                "yanchor": "top", "y": -0.22,
                "xanchor": "left", "x": 0,
                "title": {"text": ""},
            },
        )
        return _apply_white_layout(fig)

    data = year_df
    if countries:
        data = data[data["country"].isin(countries)]

    if data.empty:
        return _empty_plotly_figure("No data for the selected filters")

    # With only a few countries selected, print their names on the points.
    label_points = bool(countries) and len(data) <= MAX_LABELLED_POINTS

    fig = px.scatter(
        data,
        x=x_column,
        y="HDI",
        hover_name="country",
        text="country" if label_points else None,
        title=f"{title} ({year})",
        labels={x_column: x_label, "HDI": "Human Development Index"},
        color_discrete_sequence=PALETTE,
    )

    fig.update_traces(
        marker={"size": 11 if label_points else 8, "opacity": 0.85},
        textposition="top center",
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            f"{x_label}: %{{x:{x_hover_format}}}{unit_suffix}<br>"
            "HDI: %{y:.3f}"
            "<extra></extra>"
        ),
    )

    return _apply_white_layout(fig)


def create_life_expectancy_scatter(df, year, countries=None, continents=None):
    return _create_indicator_scatter(
        df, year,
        x_column="Life_Expectancy",
        x_label="Life Expectancy (years)",
        title="Life Expectancy vs HDI",
        x_hover_format=".2f",
        unit_suffix=" years",
        countries=countries,
        continents=continents,
    )


def create_gni_scatter(df, year, countries=None, continents=None):
    return _create_indicator_scatter(
        df, year,
        x_column="GNI_Per_Capita",
        x_label="GNI Per Capita",
        title="GNI Per Capita vs HDI",
        x_hover_format=",.2f",
        countries=countries,
        continents=continents,
    )


def create_mean_schooling_scatter(df, year, countries=None, continents=None):
    return _create_indicator_scatter(
        df, year,
        x_column="Mean_Years_Schooling",
        x_label="Mean Years of Schooling",
        title="Mean Years of Schooling vs HDI",
        x_hover_format=".2f",
        countries=countries,
        continents=continents,
    )


def create_expected_schooling_scatter(df, year, countries=None, continents=None):
    return _create_indicator_scatter(
        df, year,
        x_column="Expected_Years_Schooling",
        x_label="Expected Years of Schooling",
        title="Expected Years of Schooling vs HDI",
        x_hover_format=".2f",
        countries=countries,
        continents=continents,
    )


# =========================================================
# 6. CHART 8 - HDI DISTRIBUTION (SEABORN + MATPLOTLIB)
# =========================================================

def create_hdi_distribution(df: pd.DataFrame, year: int) -> Figure:
    data = _year_slice(df, year)

    if data.empty:
        return _empty_matplotlib_figure(f"No data available for {year}")

    fig = Figure(figsize=(10, 6))
    ax = fig.subplots()

    sns.histplot(data["HDI"], bins=15, kde=True, color=PALETTE[0], ax=ax)

    ax.set_title(f"HDI Distribution ({year})")
    ax.set_xlabel("Human Development Index")
    ax.set_ylabel("Number of Countries")

    fig.tight_layout()
    return fig


def create_continent_hdi_distribution(
    df: pd.DataFrame, year: int, continents=None
) -> Figure:
    data = add_continent_column(_year_slice(df, year)).dropna(subset=["continent"])
    if continents:
        data = data[data["continent"].isin(continents)]

    if data.empty:
        return _empty_matplotlib_figure(f"No continental data available for {year}")

    selected = sorted(data["continent"].unique())
    fig = Figure(figsize=(10, 6))
    ax = fig.subplots()

    if len(selected) == 1:
        continent = selected[0]
        sns.histplot(
            data["HDI"],
            bins=12,
            kde=True,
            color=CONTINENT_COLOURS.get(continent, PALETTE[0]),
            ax=ax,
        )
        ax.set_title(f"HDI Distribution in {continent} ({year})")
        ax.set_xlabel("Human Development Index")
        ax.set_ylabel("Number of Countries")
    else:
        order = (
            data.groupby("continent")["HDI"]
            .mean()
            .sort_values(ascending=False)
            .index.tolist()
        )
        sns.boxplot(
            data=data,
            x="HDI",
            y="continent",
            hue="continent",
            order=order,
            palette=CONTINENT_COLOURS,
            legend=False,
            showfliers=False,
            boxprops={"alpha": 0.7},
            ax=ax,
        )
        sns.stripplot(
            data=data,
            x="HDI",
            y="continent",
            order=order,
            color="#1b2733",
            alpha=0.55,
            size=4,
            jitter=0.18,
            ax=ax,
        )
        ax.set_xlim(0, 1.02)
        ax.grid(axis="x", linestyle=":", alpha=0.5)
        ax.set_title(f"HDI Distribution by Continent ({year})")
        ax.set_xlabel("Human Development Index")
        ax.set_ylabel("")

    fig.tight_layout()
    return fig


# =========================================================
# 7. CHART 9 - CORRELATION HEATMAP (SEABORN + MATPLOTLIB)
# =========================================================

def get_correlation_matrix(
    df: pd.DataFrame, year: int, continents=None
) -> pd.DataFrame:
    data = add_continent_column(_year_slice(df, year))
    if continents:
        data = data[data["continent"].isin(continents)]
    return data[CORRELATION_COLUMNS].corr()


def create_correlation_heatmap(
    df: pd.DataFrame, year: int, continents=None
) -> Figure:
    data = add_continent_column(_year_slice(df, year))
    scope_label = ""
    if continents:
        scoped_data = data[data["continent"].isin(continents)]
        if len(scoped_data) >= 3:
            data = scoped_data
            if len(continents) < len(CONTINENTS):
                scope_label = (
                    f" — {', '.join(continents)}"
                    if len(continents) <= 2
                    else f" — {len(continents)} Continents"
                )

    if len(data) < 3:
        return _empty_matplotlib_figure(
            f"Not enough data for correlation in {year}"
        )

    correlation = data[CORRELATION_COLUMNS].corr()

    fig = Figure(figsize=(10, 7))
    ax = fig.subplots()

    sns.heatmap(
        correlation,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        linewidths=0.5,
        ax=ax,
    )

    ax.set_title(f"Correlation Between HDI Indicators ({year}{scope_label})")

    fig.tight_layout()
    return fig


# =========================================================
# 8. STANDALONE PREVIEW
# =========================================================

if __name__ == "__main__":
    df = load_data()
    latest_year = get_latest_year(df)

    print("Dataset Path:", file_path)
    print("Dataset Shape:", df.shape)
    print(df.head())
    print("\nLatest Year:", latest_year)
    print("Number of Countries:", df[df["year"] == latest_year]["country"].nunique())

    create_hdi_trend(df).show()
    create_top10_chart(df, latest_year).show()
    create_bottom10_chart(df, latest_year).show()
    create_life_expectancy_scatter(df, latest_year).show()
    create_gni_scatter(df, latest_year).show()
    create_mean_schooling_scatter(df, latest_year).show()
    create_expected_schooling_scatter(df, latest_year).show()

    output_dir = BASE_DIR / "outputs"
    output_dir.mkdir(exist_ok=True)

    create_hdi_distribution(df, latest_year).savefig(
        output_dir / "hdi_distribution.png", dpi=150, bbox_inches="tight"
    )
    create_correlation_heatmap(df, latest_year).savefig(
        output_dir / "correlation_heatmap.png", dpi=150, bbox_inches="tight"
    )

    print("\nCorrelation Matrix:")
    print(get_correlation_matrix(df, latest_year))

    print("\n======================================")
    print("All visualizations completed!")
    print(f"Seaborn charts saved in: {output_dir}")
    print("======================================")