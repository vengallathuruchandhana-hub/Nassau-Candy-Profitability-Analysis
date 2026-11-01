
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Nassau Candy | Profitability Dashboard",
    page_icon="🍫",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "outputs" / "nassau_candy_cleaned.csv"


# --------------------------------------------------
# 2. LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)

    df["Order Date"] = pd.to_datetime(
        df["Order Date"], errors="coerce"
    )

    numeric_columns = [
        "Sales", "Cost", "Gross Profit", "Units",
        "Gross Margin (%)"
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


st.title("🍫 Nassau Candy Distributor")
st.subheader("Product Line Profitability & Margin Performance Analysis")
st.caption("Interactive business intelligence dashboard")

if not DATA_PATH.exists():
    st.error("Cleaned dataset not found. Please run python analysis.py first.")
    st.stop()

df = load_data()

required_columns = [
    "Sales", "Cost", "Gross Profit", "Units",
    "Division", "Product Name", "Order Date"
]

missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    st.error(f"Missing required columns: {missing_columns}")
    st.stop()


# --------------------------------------------------
# 3. SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Dashboard Filters")

min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()

date_range = st.sidebar.date_input(
    "Select Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

divisions = sorted(df["Division"].dropna().unique())

selected_divisions = st.sidebar.multiselect(
    "Select Division",
    divisions,
    default=divisions
)

products = sorted(df["Product Name"].dropna().unique())

selected_products = st.sidebar.multiselect(
    "Select Products",
    products,
    default=products
)

search = st.sidebar.text_input("Search Product Name")

# --------------------------------------------------
# 4. APPLY FILTERS
# --------------------------------------------------

filtered_df = df.copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range

    filtered_df = filtered_df[
        (filtered_df["Order Date"].dt.date >= start_date)
        & (filtered_df["Order Date"].dt.date <= end_date)
    ]

filtered_df = filtered_df[
    filtered_df["Division"].isin(selected_divisions)
]

filtered_df = filtered_df[
    filtered_df["Product Name"].isin(selected_products)
]

if search:
    filtered_df = filtered_df[
        filtered_df["Product Name"].str.contains(
            search, case=False, na=False
        )
    ]

if filtered_df.empty:
    st.warning("No records found for the selected filters.")
    st.stop()


# --------------------------------------------------
# 5. CALCULATE KPIs
# --------------------------------------------------

total_sales = filtered_df["Sales"].sum()
total_cost = filtered_df["Cost"].sum()
total_profit = filtered_df["Gross Profit"].sum()
total_units = filtered_df["Units"].sum()

gross_margin = (
    total_profit / total_sales * 100
    if total_sales else 0
)

unique_products = filtered_df["Product Name"].nunique()

st.markdown("---")
st.header("Business Performance Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Total Revenue", f"${total_sales:,.2f}")
col2.metric("Total Cost", f"${total_cost:,.2f}")
col3.metric("Total Gross Profit", f"${total_profit:,.2f}")

col4, col5, col6 = st.columns(3)

col4.metric("Gross Margin", f"{gross_margin:.2f}%")
col5.metric("Total Units Sold", f"{total_units:,.0f}")
col6.metric("Unique Products", f"{unique_products:,}")

st.markdown("---")


# --------------------------------------------------
# 6. DIVISION PERFORMANCE
# --------------------------------------------------

st.header("1. Division-wise Profitability")

division_data = (
    filtered_df.groupby("Division", as_index=False)
    .agg(
        Revenue=("Sales", "sum"),
        Cost=("Cost", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Units=("Units", "sum")
    )
)

division_data["Gross_Margin"] = (
    division_data["Gross_Profit"]
    / division_data["Revenue"] * 100
)

col1, col2 = st.columns(2)

with col1:
    fig = px.bar(
        division_data,
        x="Division",
        y="Gross_Profit",
        color="Division",
        title="Gross Profit by Division",
        labels={"Gross_Profit": "Gross Profit ($)"}
    )
    st.plotly_chart(fig, width="stretch")

with col2:
    fig = px.pie(
        division_data,
        names="Division",
        values="Revenue",
        title="Revenue Contribution by Division",
        hole=0.45
    )
    st.plotly_chart(fig, width="stretch")

st.dataframe(
    division_data.round(2),
    width="stretch",
    hide_index=True
)


# --------------------------------------------------
# 7. PRODUCT PERFORMANCE
# --------------------------------------------------

st.markdown("---")
st.header("2. Product-wise Profitability")

product_data = (
    filtered_df.groupby("Product Name", as_index=False)
    .agg(
        Revenue=("Sales", "sum"),
        Cost=("Cost", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Units=("Units", "sum")
    )
)

product_data["Gross_Margin"] = (
    product_data["Gross_Profit"]
    / product_data["Revenue"] * 100
)

top_products = product_data.nlargest(10, "Gross_Profit")

fig = px.bar(
    top_products.sort_values("Gross_Profit"),
    x="Gross_Profit",
    y="Product Name",
    orientation="h",
    color="Gross_Profit",
    title="Top 10 Products by Gross Profit",
    labels={"Gross_Profit": "Gross Profit ($)"}
)

st.plotly_chart(fig, width="stretch")

st.subheader("Product Profitability Details")

st.dataframe(
    product_data.sort_values(
        "Gross_Profit", ascending=False
    ).round(2),
    width="stretch",
    hide_index=True
)


# --------------------------------------------------
# 8. REVENUE VS PROFIT ANALYSIS
# --------------------------------------------------

st.markdown("---")
st.header("3. Revenue vs Gross Profit Analysis")

fig = px.scatter(
    product_data,
    x="Revenue",
    y="Gross_Profit",
    size="Units",
    color="Gross_Margin",
    hover_name="Product Name",
    title="Product Revenue vs Gross Profit",
    labels={
        "Revenue": "Revenue ($)",
        "Gross_Profit": "Gross Profit ($)",
        "Gross_Margin": "Gross Margin (%)"
    }
)

st.plotly_chart(fig, width="stretch")


# --------------------------------------------------
# 9. MONTHLY PERFORMANCE
# --------------------------------------------------

st.markdown("---")
st.header("4. Monthly Revenue and Profit Trends")

monthly_data = filtered_df.copy()

monthly_data["Month"] = (
    monthly_data["Order Date"].dt.to_period("M").astype(str)
)

monthly_summary = (
    monthly_data.groupby("Month", as_index=False)
    .agg(
        Revenue=("Sales", "sum"),
        Gross_Profit=("Gross Profit", "sum")
    )
)

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=monthly_summary["Month"],
        y=monthly_summary["Revenue"],
        mode="lines+markers",
        name="Revenue"
    )
)

fig.add_trace(
    go.Scatter(
        x=monthly_summary["Month"],
        y=monthly_summary["Gross_Profit"],
        mode="lines+markers",
        name="Gross Profit"
    )
)

fig.update_layout(
    title="Monthly Revenue and Gross Profit",
    xaxis_title="Month",
    yaxis_title="Amount ($)",
    hovermode="x unified"
)

st.plotly_chart(fig, width="stretch")


# --------------------------------------------------
# 10. PROFIT MARGIN ANALYSIS
# --------------------------------------------------

st.markdown("---")
st.header("5. Gross Margin Analysis")

margin_data = product_data.sort_values(
    "Gross_Margin", ascending=False
)

fig = px.bar(
    margin_data,
    x="Product Name",
    y="Gross_Margin",
    color="Gross_Margin",
    title="Gross Margin by Product",
    labels={"Gross_Margin": "Gross Margin (%)"}
)

fig.update_layout(xaxis_tickangle=-45)

st.plotly_chart(fig, width="stretch")


# --------------------------------------------------
# 11. REGIONAL PERFORMANCE
# --------------------------------------------------

st.markdown("---")
st.header("6. Regional Performance")

if "Region" in filtered_df.columns:

    region_data = (
        filtered_df.groupby("Region", as_index=False)
        .agg(
            Revenue=("Sales", "sum"),
            Gross_Profit=("Gross Profit", "sum")
        )
    )

    fig = px.bar(
        region_data,
        x="Region",
        y="Revenue",
        color="Gross_Profit",
        title="Regional Revenue and Profitability",
        labels={
            "Revenue": "Revenue ($)",
            "Gross_Profit": "Gross Profit ($)"
        }
    )

    st.plotly_chart(fig, width="stretch")

else:
    st.info("Region information is not available.")


# --------------------------------------------------
# 12. DOWNLOAD FILTERED DATA
# --------------------------------------------------

st.markdown("---")
st.header("7. Download Report")

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Dataset (CSV)",
    data=csv_data,
    file_name="nassau_candy_filtered_report.csv",
    mime="text/csv"
)


# --------------------------------------------------
# 13. BUSINESS INSIGHTS
# --------------------------------------------------

st.markdown("---")
st.header("8. Key Business Insights")

best_product = product_data.loc[
    product_data["Gross_Profit"].idxmax()
]

best_margin_product = product_data.loc[
    product_data["Gross_Margin"].idxmax()
]

best_division = division_data.loc[
    division_data["Gross_Profit"].idxmax()
]

st.markdown(
    f"""
    - **Highest profit product:** {best_product['Product Name']}
      with gross profit of ${best_product['Gross_Profit']:,.2f}.
    - **Highest margin product:** {best_margin_product['Product Name']}
      with gross margin of {best_margin_product['Gross_Margin']:.2f}%.
    - **Top division by profit:** {best_division['Division']}
      with gross profit of ${best_division['Gross_Profit']:,.2f}.
    - **Overall gross margin:** {gross_margin:.2f}%.
    """
)

st.markdown("---")
st.caption(
    "Nassau Candy Distributor | Product Line Profitability "
    "& Margin Performance Analysis"
)
