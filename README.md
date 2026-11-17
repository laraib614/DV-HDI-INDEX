# Analysis and Visualisation of the Human Development Index (DV-HDI-INDEX)

An interactive Python dashboard for exploring global human development, built from United Nations Development Programme (UNDP) Human Development Report data for 195 countries from 1990 to 2023.

**Course context:** Data Visualization Lab (BISL504), NIE Mysuru — Dept. of Information Science & Engineering.

---

## Abstract

The Human Development Index (HDI) Analysis Project presents a comprehensive examination of global human development trends using data obtained from the United Nations Development Programme (UNDP). The dataset incorporates HDI values along with its core components: life expectancy, educational attainment (mean and expected years of schooling), and Gross National Income (GNI) per capita. This enables a multidimensional assessment of development across countries and continents. The primary objective of this project is to design and implement an interactive data visualization dashboard that gives users an intuitive platform to explore, compare, and interpret global and continental HDI statistics.

The dashboard combines interactive Plotly visualizations (long-run trend lines, country rankings, continental average & spread comparisons, and indicator scatter plots) with Seaborn statistical charts (HDI distribution and correlation heatmap). Interactive year, continent, and country filters, hover details, and explicit Apply/Reset updates support dynamic analysis across global, country, and continental views.

By transforming a complex dataset into clear, accessible visuals, the project makes it easier to see global development disparities, continental trajectories, progress over time, and the factors most closely associated with human well-being. Ultimately, it demonstrates how data visualization converts raw numerical information into actionable knowledge that can support evidence-based discussion of sustainable human development.

---

## Key features

- **Global, Country, or Continental views:** Start in the global overview across all 195 countries, drill down to compare individual countries, or compare up to six continents (`Africa`, `Asia`, `Europe`, `North America`, `Oceania`, `South America`). Country and continental comparisons are mutually exclusive (selecting one clears the other) so every chart stays clear and comparable.
- **Year filter:** Choose any year from 1990 to 2023. It updates the summary figures, rankings/continental comparisons, scatter plots, distribution, and correlation heatmap.
- **Continents to compare:** Select one, several, or all six continents (`Select All`). All 195 `countryIsoCode` values are mapped via UNSD M49 conventions (`src/continents.py`) and combined per year into continental averages. The dashboard plots continental trend lines (1990–2023), a Continental Average HDI bar chart, a country-level HDI spread box plot, continental averages on the four indicator scatter plots, and Seaborn continental distribution and correlation charts.
- **Country comparison:** Search and select any number of countries. The trend chart shows one line per selected country against the dashed all-country average, and the scatter plots show the selected countries with their names labelled (when 12 or fewer are selected).
- **Context-aware view:** While only countries are selected, the Top 10, Bottom 10, and global HDI Distribution charts are hidden, because they rank or describe all 195 countries and would be misleading for a subset. When continents are selected, the rankings section switches to the Continental Comparison charts. Press **Reset** to restore the global view.
- **Summary figures:** Average, highest, and lowest HDI (or highest/lowest continent when comparing 2+ continents), plus country/continent counts and change since 1990.
- **Clear filter feedback:** Apply and Reset buttons, a status pill showing the current view, a contextual explanation note, and an amber hint when filters have been changed but not yet applied.
- **Accessible design:** Colour-blind-safe Okabe-Ito palette (`CONTINENT_COLOURS` / `PALETTE`), plain white chart areas, direct data labels, visible keyboard focus, alt text on Seaborn images, and a responsive layout.

---

## Tech stack

| Layer | Technology | Used for |
|---|---|---|
| Language | Python 3.10 | All code |
| Data handling | Pandas | Loading, cleaning, reshaping, filtering, aggregation |
| Spreadsheet I/O | openpyxl | Reading the raw `.xlsx` and writing the cleaned `.xlsx` |
| Dashboard framework | Dash (Flask-based) | Layout, filters, and callbacks |
| Interactive charts | Plotly Express / Plotly Graph Objects | Trend, ranking, continental comparison, and scatter charts |
| Statistical charts | Seaborn + Matplotlib | Distribution and correlation heatmap charts |
| Styling | CSS (`dashboard/assets/style.css`) | Layout, filter bar, focus states, responsive design |
| Development | Visual Studio Code, PowerShell, pip | Editing, running, package management |
| Data source | UNDP Human Development Report | Raw dataset |

## Visualization tools and charts

| # | Chart | Type | Library | Responds to |
|---|---|---|---|---|
| 1 | Average / Continental HDI Trend, 1990–2023 | Line | Plotly | Continents, countries (year shown as vertical marker) |
| 2 | Top 10 Countries by HDI *(Global view)* | Horizontal bar | Plotly | Year |
| 3 | Bottom 10 Countries by HDI *(Global view)* | Horizontal bar | Plotly | Year |
| 4 | Life Expectancy vs HDI | Scatter | Plotly | Year, continents, countries |
| 5 | GNI Per Capita vs HDI | Scatter | Plotly | Year, continents, countries |
| 6 | Mean Years of Schooling vs HDI | Scatter | Plotly | Year, continents, countries |
| 7 | Expected Years of Schooling vs HDI | Scatter | Plotly | Year, continents, countries |
| 8 | HDI Distribution *(Global or by Continent)* | Histogram / Box + Strip | Seaborn + Matplotlib | Year, continents |
| 9 | Correlation Heatmap | Heatmap | Seaborn + Matplotlib | Year, continents |
| 10 | Average HDI by Continent *(Continental view)* | Horizontal bar | Plotly | Year, continents |
| 11 | HDI Spread Across Countries by Continent *(Continental view)* | Box plot + country points | Plotly | Year, continents |

Interactive Plotly charts support hover tooltips, zoom, pan, and PNG download. Seaborn charts are rendered on Matplotlib figures and embedded as PNGs whenever filters are applied.

---

## Dataset

- **Source:** UNDP Human Development Report data (`data/raw/hdr-data (3).xlsx`).
- **Cleaned file:** `data/processed/HDI_cleaned.csv` (also saved as `.xlsx`).
- **Size:** 6,630 rows = 195 countries × 34 years (1990–2023), one row per country per year, with no duplicate country-year rows.

| Column | Meaning |
|---|---|
| `countryIsoCode`, `country` | Country identifiers |
| `year` | Observation year |
| `HDI` | Human Development Index (0 to 1) |
| `Life_Expectancy` | Life expectancy at birth (years) |
| `Mean_Years_Schooling` | Mean years of schooling |
| `Expected_Years_Schooling` | Expected years of schooling |
| `GNI_Per_Capita` | Gross national income per capita |
| `HDI_Rank` | Official rank (mostly empty; not used by the dashboard) |

### Preprocessing summary

`src/preprocessin.py` removes unused columns and exact duplicates, converts values to numbers, sets impossible values to missing (for example an HDI outside 0 to 1), pivots the long-format source into one row per country-year, renames the indicators, and fills gaps by linear interpolation within each country (any remaining gaps use the indicator's median).

### Data notes and limitations

- **Interpolated values:** because gaps were filled during preprocessing and the cleaned file does not flag which values were filled, every country appears in every year. The dashboard footer and the country-count card state this.
- **Rwanda, 1994:** the lowest life expectancy (12.158 years) is a genuine historical value and was deliberately left unchanged.
- **Descriptive only:** the scatter plots and correlations show association, not causation. HDI is itself calculated from life expectancy, schooling, and income, so strong correlations are expected.
- **No sub-national or population-weighted data:** `HDI_cleaned.csv` contains country-level records without population weights. To support continental comparison (`src/continents.py`), all 195 `countryIsoCode` values are mapped to six continents (`Africa`, `Asia`, `Europe`, `North America`, `Oceania`, `South America`) using UNSD M49 macro-geographical conventions, and continental scores are calculated as unweighted arithmetic means across each continent's countries (matching how the global average is computed).

---

## Project structure

```text
DV-HDI-INDEX/
│
├── .vscode/
│   └── settings.json
│
├── data/
│   ├── raw/
│   │   └── hdr-data (3).xlsx          # original UNDP dataset
│   └── processed/
│       ├── HDI_cleaned.csv            # dataset used by the dashboard
│       └── HDI_cleaned.xlsx
│
├── src/
│   ├── __init__.py
│   ├── continents.py                  # UN M49 195-country continent mapping & aggregation
│   ├── preprocessin.py                # data cleaning workflow
│   └── visualization.py               # Plotly and Seaborn chart functions
│
├── dashboard/
│   ├── app.py                         # Dash layout and callbacks
│   └── assets/
│       └── style.css                  # dashboard styling
│
├── tests/
│   ├── __init__.py
│   └── test_charts.py                 # chart, filter, and continent checks
│
├── docs/
│   ├── AI_critique_log.md             # 4-criterion AI design critique log
│   ├── HDI_Analysis_and_Visualization_Report.docx
│   ├── HDI_Project_Presentation.pptx
│   └── HDI_Full_Project_Presentation.pptx
├── evidence/                          # before / after / testing screenshots
├── outputs/                           # saved dashboard screenshots and chart PNGs
├── requirements.txt
└── README.md
```

---

## Getting started

### 1. Install dependencies

From the project root in PowerShell:

```powershell
pip install -r requirements.txt
```

### 2. Run the chart tests (optional)

```powershell
python -m tests.test_charts
```

You should see `ALL CHART TESTS PASSED`.

### 3. Launch the dashboard

```powershell
python dashboard\app.py
```

Open **http://127.0.0.1:8050** in your browser. Stop the server with `Ctrl+C`.

> Run the app from the terminal with the command above rather than the editor's Run button, so that project paths resolve correctly.

### Previewing the charts without the dashboard

```powershell
python src\visualization.py
```

This opens charts 1–7 in your browser and saves the two Seaborn charts to `outputs/`.

### Re-running preprocessing

`src/preprocessin.py` currently reads the raw file from a hard-coded path and saves its output in the folder it is run from. Update the input path, and move the output files into `data/processed/`, before re-running it.

---

## How to use the dashboard

1. Choose a **Year** and press **Apply** to update the rankings, scatter plots, distribution, heatmap, and summary figures.
2. Open **Continents to compare**, select one or more continents (or click **Select All** for all six), and press **Apply** to view combined continental trends, Continental Average HDI bars, country-level box spreads, continental indicator scatter plots, and continental distribution/correlation charts. (Selecting continents clears any country selection.)
3. Open **Countries to compare**, type to search, and add one or more countries. Press **Apply** to see their HDI trends against the all-country average. (Selecting countries clears any continent selection.)
4. Hover over any point or bar for exact values. Use the chart toolbar to zoom, pan, or download a chart.
5. Press **Reset** to return to the latest year (`2023`) in the global view.

---

## Deliverables and evidence 

| Deliverable | Location | Status |
|---|---|---|
| Interactive dashboard with global, country, and continental views | `dashboard/`, `src/` | Done |
| Project report & final presentation slides | `docs/HDI_Analysis_and_Visualization_Report.docx`, `docs/HDI_Project_Presentation.pptx` | Done |
| AI design critique against four criteria: data-ink ratio, colour accessibility, layout hierarchy, interactivity affordances | `docs/AI_critique_log.md` | Done |
| "Before" screenshots of the initial dashboard | `evidence/before/` | To add |
| "After" screenshots of the improved dashboard | `evidence/after/` | To add |
| Functional testing evidence | `evidence/testing/` | To add |

Update the status column as each item is completed.

---

## Team & Guidance

- **Course:** Data Visualization Lab (`BISL504`), Dept. of Information Science & Engineering, The National Institute of Engineering (NIE), Mysuru
- **Team Members:** Muhammad Laraib Jamal (`4NI24IS109`), Nadeem Siddique (`4NI24IS113`), Manan Maheshwari (`4NI24IS099`), N Ravi Kiran (`4NI24IS112`)
- **Guides:** Dr. K. Raghuveer (Professor, Dept. of ISE) & Ms. Sandhya N (Assistant Professor, Dept. of ISE)

---

## AI assistance

This project was developed with assistance from AI tools for refactoring the chart code into reusable functions, implementing the Dash application and styling, adding UN M49 continental mapping and comparative charts, conducting design critique, and preparing documentation/presentation materials. All outputs were reviewed and verified locally against the dataset and test suite.

---

## Data source and credits

- UNDP Human Development Report data: <https://hdr.undp.org/data-center>
- Built with [Dash](https://dash.plotly.com/), [Plotly](https://plotly.com/python/), [Seaborn](https://seaborn.pydata.org/), [Matplotlib](https://matplotlib.org/), and [Pandas](https://pandas.pydata.org/).
