"""
Continent mapping and continental aggregation helpers for the HDI dataset.

Uses the six-continent UN M49 / Our World in Data classification:
Africa, Asia, Europe, North America, Oceania, South America.
"""

import pandas as pd

CONTINENTS = [
    "Africa",
    "Asia",
    "Europe",
    "North America",
    "Oceania",
    "South America",
]

# Complete ISO 3166-1 alpha-3 -> continent mapping for all 195 countries
# in data/processed/HDI_cleaned.csv (following UNSD M49 macro-geographical
# conventions: e.g. RUS -> Europe; ARM, AZE, CYP, GEO, KAZ, TUR -> Asia;
# Central America and the Caribbean -> North America).
COUNTRY_TO_CONTINENT = {
    "AFG": "Asia",
    "AGO": "Africa",
    "ALB": "Europe",
    "AND": "Europe",
    "ARE": "Asia",
    "ARG": "South America",
    "ARM": "Asia",
    "ATG": "North America",
    "AUS": "Oceania",
    "AUT": "Europe",
    "AZE": "Asia",
    "BDI": "Africa",
    "BEL": "Europe",
    "BEN": "Africa",
    "BFA": "Africa",
    "BGD": "Asia",
    "BGR": "Europe",
    "BHR": "Asia",
    "BHS": "North America",
    "BIH": "Europe",
    "BLR": "Europe",
    "BLZ": "North America",
    "BOL": "South America",
    "BRA": "South America",
    "BRB": "North America",
    "BRN": "Asia",
    "BTN": "Asia",
    "BWA": "Africa",
    "CAF": "Africa",
    "CAN": "North America",
    "CHE": "Europe",
    "CHL": "South America",
    "CHN": "Asia",
    "CIV": "Africa",
    "CMR": "Africa",
    "COD": "Africa",
    "COG": "Africa",
    "COL": "South America",
    "COM": "Africa",
    "CPV": "Africa",
    "CRI": "North America",
    "CUB": "North America",
    "CYP": "Asia",
    "CZE": "Europe",
    "DEU": "Europe",
    "DJI": "Africa",
    "DMA": "North America",
    "DNK": "Europe",
    "DOM": "North America",
    "DZA": "Africa",
    "ECU": "South America",
    "EGY": "Africa",
    "ERI": "Africa",
    "ESP": "Europe",
    "EST": "Europe",
    "ETH": "Africa",
    "FIN": "Europe",
    "FJI": "Oceania",
    "FRA": "Europe",
    "FSM": "Oceania",
    "GAB": "Africa",
    "GBR": "Europe",
    "GEO": "Asia",
    "GHA": "Africa",
    "GIN": "Africa",
    "GMB": "Africa",
    "GNB": "Africa",
    "GNQ": "Africa",
    "GRC": "Europe",
    "GRD": "North America",
    "GTM": "North America",
    "GUY": "South America",
    "HKG": "Asia",
    "HND": "North America",
    "HRV": "Europe",
    "HTI": "North America",
    "HUN": "Europe",
    "IDN": "Asia",
    "IND": "Asia",
    "IRL": "Europe",
    "IRN": "Asia",
    "IRQ": "Asia",
    "ISL": "Europe",
    "ISR": "Asia",
    "ITA": "Europe",
    "JAM": "North America",
    "JOR": "Asia",
    "JPN": "Asia",
    "KAZ": "Asia",
    "KEN": "Africa",
    "KGZ": "Asia",
    "KHM": "Asia",
    "KIR": "Oceania",
    "KNA": "North America",
    "KOR": "Asia",
    "KWT": "Asia",
    "LAO": "Asia",
    "LBN": "Asia",
    "LBR": "Africa",
    "LBY": "Africa",
    "LCA": "North America",
    "LIE": "Europe",
    "LKA": "Asia",
    "LSO": "Africa",
    "LTU": "Europe",
    "LUX": "Europe",
    "LVA": "Europe",
    "MAR": "Africa",
    "MCO": "Europe",
    "MDA": "Europe",
    "MDG": "Africa",
    "MDV": "Asia",
    "MEX": "North America",
    "MHL": "Oceania",
    "MKD": "Europe",
    "MLI": "Africa",
    "MLT": "Europe",
    "MMR": "Asia",
    "MNE": "Europe",
    "MNG": "Asia",
    "MOZ": "Africa",
    "MRT": "Africa",
    "MUS": "Africa",
    "MWI": "Africa",
    "MYS": "Asia",
    "NAM": "Africa",
    "NER": "Africa",
    "NGA": "Africa",
    "NIC": "North America",
    "NLD": "Europe",
    "NOR": "Europe",
    "NPL": "Asia",
    "NRU": "Oceania",
    "NZL": "Oceania",
    "OMN": "Asia",
    "PAK": "Asia",
    "PAN": "North America",
    "PER": "South America",
    "PHL": "Asia",
    "PLW": "Oceania",
    "PNG": "Oceania",
    "POL": "Europe",
    "PRK": "Asia",
    "PRT": "Europe",
    "PRY": "South America",
    "PSE": "Asia",
    "QAT": "Asia",
    "ROU": "Europe",
    "RUS": "Europe",
    "RWA": "Africa",
    "SAU": "Asia",
    "SDN": "Africa",
    "SEN": "Africa",
    "SGP": "Asia",
    "SLB": "Oceania",
    "SLE": "Africa",
    "SLV": "North America",
    "SMR": "Europe",
    "SOM": "Africa",
    "SRB": "Europe",
    "SSD": "Africa",
    "STP": "Africa",
    "SUR": "South America",
    "SVK": "Europe",
    "SVN": "Europe",
    "SWE": "Europe",
    "SWZ": "Africa",
    "SYC": "Africa",
    "SYR": "Asia",
    "TCD": "Africa",
    "TGO": "Africa",
    "THA": "Asia",
    "TJK": "Asia",
    "TKM": "Asia",
    "TLS": "Asia",
    "TON": "Oceania",
    "TTO": "North America",
    "TUN": "Africa",
    "TUR": "Asia",
    "TUV": "Oceania",
    "TZA": "Africa",
    "UGA": "Africa",
    "UKR": "Europe",
    "URY": "South America",
    "USA": "North America",
    "UZB": "Asia",
    "VCT": "North America",
    "VEN": "South America",
    "VNM": "Asia",
    "VUT": "Oceania",
    "WSM": "Oceania",
    "YEM": "Asia",
    "ZAF": "Africa",
    "ZMB": "Africa",
    "ZWE": "Africa",
}

INDICATOR_COLUMNS = [
    "HDI",
    "Life_Expectancy",
    "Mean_Years_Schooling",
    "Expected_Years_Schooling",
    "GNI_Per_Capita",
]


def add_continent_column(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy (or the frame if already present) with a `continent` column."""
    if "continent" in df.columns:
        return df
    out = df.copy()
    if "countryIsoCode" in out.columns:
        out["continent"] = out["countryIsoCode"].map(COUNTRY_TO_CONTINENT)
    else:
        out["continent"] = pd.NA
    return out


def aggregate_by_continent(
    df: pd.DataFrame, continents=None
) -> pd.DataFrame:
    """Combine country rows into continental averages per continent and year.

    Computes the unweighted arithmetic mean across countries in each continent
    for HDI and its four indicators, matching how the dashboard computes the
    all-country global average.
    """
    data = add_continent_column(df)
    data = data.dropna(subset=["continent"])
    if continents:
        data = data[data["continent"].isin(continents)]
    if data.empty:
        return pd.DataFrame(
            columns=["continent", "year", "country_count", *INDICATOR_COLUMNS]
        )

    agg = (
        data.groupby(["continent", "year"], as_index=False)
        .agg(
            country_count=("country", "nunique"),
            **{col: (col, "mean") for col in INDICATOR_COLUMNS},
        )
        .sort_values(["continent", "year"])
    )
    return agg
