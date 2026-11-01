# Nassau Candy Distributor – Product Line Profitability & Margin Performance Analysis

## Project Overview

This project analyzes sales, costs, gross profit, and gross margins for Nassau Candy Distributor. The objective is to identify profitable products, evaluate division-wise performance, understand revenue contributions, and generate actionable business insights.

An interactive dashboard was developed using Python and Streamlit to help users explore business performance through visualizations and filters.

## Business Objectives

- Analyze overall sales and profitability.
- Identify the highest-profit products.
- Compare profitability across product divisions.
- Evaluate gross margin performance.
- Analyze monthly revenue and profit trends.
- Understand regional business performance.
- Provide interactive visual reports for business decision-making.

## Dataset Overview

- Total Records: 10,194
- Original Columns: 18
- Unique Products: 15
- Key Fields: Order Date, Ship Date, Division, Region, Product Name, Sales, Units, Gross Profit, and Cost.

Dataset file: `data/Nassau Candy Distributor.csv`

## Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Plotly
- Streamlit
- VS Code

## Project Structure

```text
Nassau-Candy-Profitability-Analysis/
│
├── data/
│   └── Nassau Candy Distributor.csv
│
├── notebooks/
│
├── outputs/
│   ├── division_profitability.csv
│   ├── monthly_profitability.csv
│   ├── product_profitability.csv
│   ├── nassau_candy_cleaned.csv
│   └── nassau_candy_all_records_with_flags.csv
│
├── analysis.py
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Data Cleaning and Preparation

The following steps were performed:

1. Loaded and inspected the dataset using Pandas.
2. Checked missing values and duplicate records.
3. Converted date columns into appropriate date formats.
4. Validated sales, cost, units, and gross profit values.
5. Checked shipping dates against order dates.
6. Calculated gross margin and profit-related metrics.
7. Generated cleaned datasets and profitability summary files.

## Key Performance Indicators (KPIs)

- Total Revenue
- Total Cost
- Total Gross Profit
- Gross Margin Percentage
- Total Units Sold
- Unique Products

**Gross Margin Formula:**

Gross Margin (%) = (Gross Profit / Revenue) × 100

## Key Business Findings

Based on the dataset analysis:

- Total Revenue: $141,783.63
- Total Cost: $48,340.83
- Total Gross Profit: $93,442.80
- Overall Gross Margin: 65.91%
- Total Valid Records: 10,194

### Division Performance

- Chocolate generated the highest revenue and gross profit.
- Chocolate recorded $88,824.62 in gross profit.
- Other division recorded $4,333.45 in gross profit.
- Sugar division recorded $284.73 in gross profit.

### Product Performance

- Wonka Bar - Scrumdiddlyumptious generated the highest gross profit of $19,357.50.
- Wonka Bar - Nutty Crunch Surprise achieved a gross margin of 71.35%.
- Kazookles recorded a comparatively low gross margin of 7.69%, indicating an opportunity for further cost and pricing analysis.

## Interactive Dashboard Features

The Streamlit dashboard provides:

- Interactive KPI cards.
- Date, division, and product filters.
- Division-wise profitability charts.
- Top 10 products by gross profit.
- Revenue versus gross profit analysis.
- Monthly revenue and profit trends.
- Product-wise gross margin analysis.
- Regional performance analysis.
- Filtered dataset download in CSV format.

## How to Run the Project

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the data analysis

```bash
python analysis.py
```

### 3. Launch the Streamlit dashboard

```bash
streamlit run app.py
```

## Conclusion

This project provides a comprehensive view of Nassau Candy Distributor's product profitability and margin performance. The analysis helps identify high-performing products, understand division contributions, and highlight products that may require pricing or cost optimization.

The interactive dashboard makes business performance easier to explore and supports data-driven decision-making.

---

**Project:** Product Line Profitability & Margin Performance Analysis  
**Domain:** Data Science |