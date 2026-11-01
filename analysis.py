
from pathlib import Path

import numpy as np
import pandas as pd

# Project folders
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "Nassau Candy Distributor.csv"
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print("\n" + "=" * 60)
    print("NASSAU CANDY - PROFITABILITY ANALYSIS")
    print("=" * 60)

    # 1. Load the dataset
    df = pd.read_csv(DATA_FILE)

    print("\n1. DATASET OVERVIEW")
    print("-" * 40)
    print(f"Rows: {df.shape[0]:,}")
    print(f"Columns: {df.shape[1]}")
    print("\nColumn names:")
    print(df.columns.tolist())

    # 2. Clean column names and text fields
    df.columns = df.columns.str.strip()

    for column in ["Division", "Product Name", "Product ID", "Region"]:
        if column in df.columns:
            df[column] = df[column].astype("string").str.strip()

    # 3. Check data quality
    print("\n2. DATA QUALITY")
    print("-" * 40)
    print("\nMissing values:")
    print(df.isnull().sum().sort_values(ascending=False).to_string())
    print(f"\nExact duplicate rows: {df.duplicated().sum():,}")

    # 4. Convert data types
    date_columns = ["Order Date", "Ship Date"]

    for column in date_columns:
        if column in df.columns:
            df[column] = pd.to_datetime(
               df[column],
               errors="coerce",
               dayfirst=True
        )

    numeric_columns = ["Sales", "Units", "Gross Profit", "Cost"]
    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    required_columns = [
        "Sales", "Units", "Gross Profit", "Cost",
        "Order Date", "Division", "Product Name"
    ]
    missing_columns = [
        column for column in required_columns if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Required columns not found: {missing_columns}. "
            "Check the dataset column names."
        )

    # 5. Validate profit calculation
    df["Calculated Profit"] = df["Sales"] - df["Cost"]
    df["Profit Difference"] = (
        df["Gross Profit"] - df["Calculated Profit"]
    )

    profit_mismatches = (
        df["Profit Difference"].abs() > 0.02
    ).sum()

    print("\n3. PROFIT VALIDATION")
    print("-" * 40)
    print(f"Rows where Gross Profit differs from Sales - Cost: "
          f"{profit_mismatches:,}")

    # 6. Flag invalid or incomplete records
    invalid = (
        df[required_columns].isna().any(axis=1)
        | (df["Sales"] <= 0)
        | (df["Cost"] < 0)
        | (df["Units"] <= 0)
        | (df["Gross Profit"] < 0)
    )

    # Keep the original records for review; do not silently delete them.
    df["Data Quality Issue"] = invalid

    # Flag suspicious shipping dates separately.
    df["Ship Date Issue"] = (
        df["Ship Date"].isna()
        | (df["Ship Date"] < df["Order Date"])
    )

    clean_df = df.loc[~invalid].copy()

    if clean_df.empty:
        raise ValueError(
            "No valid rows remain. Review the data quality checks."
        )

    # 7. Calculate business KPIs
    clean_df["Gross Margin (%)"] = (
        clean_df["Gross Profit"] / clean_df["Sales"] * 100
    )
    clean_df["Profit per Unit"] = (
        clean_df["Gross Profit"] / clean_df["Units"]
    )
    clean_df["Revenue Contribution (%)"] = (
        clean_df["Sales"] / clean_df["Sales"].sum() * 100
    )

    total_profit = clean_df["Gross Profit"].sum()

    if total_profit != 0:
        clean_df["Profit Contribution (%)"] = (
            clean_df["Gross Profit"] / total_profit * 100
        )
    else:
        clean_df["Profit Contribution (%)"] = np.nan

    # 8. Product profitability
    product_summary = (
        clean_df.groupby(
            ["Product ID", "Product Name", "Division"],
            dropna=False
        )
        .agg(
            Revenue=("Sales", "sum"),
            Total_Cost=("Cost", "sum"),
            Total_Profit=("Gross Profit", "sum"),
            Total_Units=("Units", "sum"),
            Orders=("Order ID", "nunique")
        )
        .reset_index()
    )

    product_summary["Gross_Margin_Pct"] = (
        product_summary["Total_Profit"]
        / product_summary["Revenue"] * 100
    )

    product_summary["Profit_Per_Unit"] = (
        product_summary["Total_Profit"]
        / product_summary["Total_Units"]
    )

    product_summary["Revenue_Contribution_Pct"] = (
        product_summary["Revenue"]
        / product_summary["Revenue"].sum() * 100
    )

    if product_summary["Total_Profit"].sum() != 0:
        product_summary["Profit_Contribution_Pct"] = (
            product_summary["Total_Profit"]
            / product_summary["Total_Profit"].sum() * 100
        )
    else:
        product_summary["Profit_Contribution_Pct"] = np.nan

    # Pareto-style cumulative profit contribution.
    # This is most interpretable when profits are non-negative.
    product_summary = product_summary.sort_values(
        "Total_Profit", ascending=False
    )
    product_summary["Cumulative_Profit_Contribution_Pct"] = (
        product_summary["Profit_Contribution_Pct"].cumsum()
    )

    # 9. Division profitability
    division_summary = (
        clean_df.groupby("Division", dropna=False)
        .agg(
            Revenue=("Sales", "sum"),
            Total_Cost=("Cost", "sum"),
            Total_Profit=("Gross Profit", "sum"),
            Total_Units=("Units", "sum")
        )
        .reset_index()
    )

    division_summary["Gross_Margin_Pct"] = (
        division_summary["Total_Profit"]
        / division_summary["Revenue"] * 100
    )

    # 10. Monthly profitability
    clean_df["Order Month"] = (
        clean_df["Order Date"].dt.to_period("M").astype(str)
    )

    monthly_summary = (
        clean_df.groupby("Order Month")
        .agg(
            Revenue=("Sales", "sum"),
            Total_Profit=("Gross Profit", "sum")
        )
        .reset_index()
    )

    monthly_summary["Gross_Margin_Pct"] = (
        monthly_summary["Total_Profit"]
        / monthly_summary["Revenue"] * 100
    )

    # 11. Save results
    clean_df.to_csv(
        OUTPUT_DIR / "nassau_candy_cleaned.csv", index=False
    )
    product_summary.to_csv(
        OUTPUT_DIR / "product_profitability.csv", index=False
    )
    division_summary.to_csv(
        OUTPUT_DIR / "division_profitability.csv", index=False
    )
    monthly_summary.to_csv(
        OUTPUT_DIR / "monthly_profitability.csv", index=False
    )

    # 12. Print results
    print("\n4. OVERALL BUSINESS KPIs")
    print("-" * 40)
    print(f"Valid rows: {len(clean_df):,}")
    print(f"Rows flagged for review: {int(invalid.sum()):,}")
    print(f"Rows with suspicious shipping dates: "
          f"{int(clean_df['Ship Date Issue'].sum()):,}")
    print(f"Total Revenue: {clean_df['Sales'].sum():,.2f}")
    print(f"Total Cost: {clean_df['Cost'].sum():,.2f}")
    print(f"Total Gross Profit: {total_profit:,.2f}")
    print(
        "Overall Gross Margin: "
        f"{total_profit / clean_df['Sales'].sum() * 100:.2f}%"
    )
    print(
        "Unique Products: "
        f"{clean_df['Product ID'].nunique():,}"
    )

    print("\n5. DIVISION PERFORMANCE")
    print("-" * 40)
    print(
        division_summary.sort_values(
            "Total_Profit", ascending=False
        ).to_string(index=False, formatters={
            "Revenue": "{:,.2f}".format,
            "Total_Cost": "{:,.2f}".format,
            "Total_Profit": "{:,.2f}".format,
            "Gross_Margin_Pct": "{:.2f}%".format
        })
    )

    print("\n6. TOP 10 PRODUCTS BY GROSS PROFIT")
    print("-" * 40)
    print(
        product_summary[
            [
                "Product Name", "Division", "Revenue",
                "Total_Profit", "Gross_Margin_Pct"
            ]
        ].head(10).to_string(index=False, formatters={
            "Revenue": "{:,.2f}".format,
            "Total_Profit": "{:,.2f}".format,
            "Gross_Margin_Pct": "{:.2f}%".format
        })
    )

    print("\n7. OUTPUT FILES")
    print("-" * 40)
    for path in sorted(OUTPUT_DIR.glob("*.csv")):
        print(path.name)

    print("\nAnalysis completed successfully!")


if __name__ == "__main__":
    main()
