from plotly.graph_objects import Figure as PlotlyFigure
from matplotlib.figure import Figure as MplFigure

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

df = load_data()
year = get_latest_year(df)
two = ["India", "China"] if {"India", "China"} <= set(df["country"]) else list(df["country"].unique()[:2])

plotly_charts = {
    "1 HDI trend": create_hdi_trend(df),
    "2 Top 10": create_top10_chart(df, year),
    "3 Bottom 10": create_bottom10_chart(df, year),
    "4 Life expectancy": create_life_expectancy_scatter(df, year),
    "5 GNI": create_gni_scatter(df, year),
    "6 Mean schooling": create_mean_schooling_scatter(df, year),
    "7 Expected schooling": create_expected_schooling_scatter(df, year),
}
for name, fig in plotly_charts.items():
    assert isinstance(fig, PlotlyFigure), name
    print("OK Plotly  :", name)

for name, fig in {
    "8 Distribution": create_hdi_distribution(df, year),
    "9 Heatmap": create_correlation_heatmap(df, year),
}.items():
    assert isinstance(fig, MplFigure), name
    assert figure_to_base64(fig).startswith("data:image/png;base64,"), name
    print("OK Seaborn :", name)

# Filter checks
sc = create_life_expectancy_scatter(df, year, countries=two)
assert len(sc.data[0].x) == 2
print("Scatter points with 2 countries:", len(sc.data[0].x), "(expected 2)")

assert len(create_top10_chart(df, 1990).data[0].y) == 10
print("Top 10 rows for 1990:", len(create_top10_chart(df, 1990).data[0].y), "(expected 10)")

assert isinstance(create_top10_chart(df, 1800), PlotlyFigure)
print("Empty-year chart handled:", isinstance(create_top10_chart(df, 1800), PlotlyFigure))

# Trend with selected countries: one line per country + 1 average line
trend = create_hdi_trend(df, countries=two, year=year)
names = [t.name for t in trend.data]
assert len(trend.data) == len(two) + 1, names
assert "All-country average" in names
print("Trend lines with 2 countries:", len(trend.data), "(expected 3):", names)

# Trend without countries still has the single full-period average line
plain = create_hdi_trend(df)
assert len(plain.data) == 1
print("Trend lines with no countries:", len(plain.data), "(expected 1)")

# Continent mapping & aggregation checks
assert df["continent"].isna().sum() == 0, "All 195 countries must map to a continent"
assert set(df["continent"].unique()) == set(CONTINENTS)
cont_latest = aggregate_by_continent(df[df["year"] == year])
assert len(cont_latest) == len(CONTINENTS)
assert cont_latest["country_count"].sum() == df[df["year"] == year]["country"].nunique()
print("All 195 countries mapped across", len(CONTINENTS), "continents")

# Continental chart checks
sample_continents = ["Africa", "Asia", "Europe"]
cont_trend = create_hdi_trend(df, continents=sample_continents, year=year)
cont_names = [t.name for t in cont_trend.data]
assert len(cont_trend.data) == len(sample_continents) + 1, cont_names
assert "All-country average" in cont_names
print("Continental trend lines:", len(cont_trend.data), "(expected 4):", cont_names)

bar_fig = create_continent_hdi_bar(df, year, sample_continents)
assert isinstance(bar_fig, PlotlyFigure)
assert list(bar_fig.layout.yaxis.categoryarray) == ["Africa", "Asia", "Europe"]

spread_fig = create_continent_hdi_spread(df, year, sample_continents)
assert isinstance(spread_fig, PlotlyFigure)
assert list(spread_fig.layout.yaxis.categoryarray) == ["Africa", "Asia", "Europe"]

cont_sc = create_life_expectancy_scatter(df, year, continents=sample_continents)
assert len(cont_sc.data) == len(sample_continents)

cont_dist_multi = create_continent_hdi_distribution(df, year, sample_continents)
assert isinstance(cont_dist_multi, MplFigure)
assert figure_to_base64(cont_dist_multi).startswith("data:image/png;base64,")

cont_dist_single = create_continent_hdi_distribution(df, year, ["Asia"])
assert isinstance(cont_dist_single, MplFigure)
assert figure_to_base64(cont_dist_single).startswith("data:image/png;base64,")

cont_hm = create_correlation_heatmap(df, year, continents=sample_continents)
assert isinstance(cont_hm, MplFigure)
assert figure_to_base64(cont_hm).startswith("data:image/png;base64,")
print("OK Continental charts (Plotly + Seaborn)")

# Data check
row = df.loc[df["Life_Expectancy"].idxmin(), ["country", "year", "Life_Expectancy"]]
print("\nLowest life expectancy row:\n", row.to_string())
print("\nALL CHART TESTS PASSED")