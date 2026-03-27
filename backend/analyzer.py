import pandas as pd

def analyze_funds(file, threshold=0.0, include_revenue=False):
    # Load single sheet
    df = pd.read_excel(file)

    # Required columns
    required_cols = {"fund_id", "year", "balance", "spend", "revenue"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"File must contain columns: {required_cols}")

    # Ensure numeric fields
    df["balance"] = pd.to_numeric(df["balance"], errors="coerce")
    df["spend"] = pd.to_numeric(df["spend"], errors="coerce")
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")

    # Drop invalid rows
    df = df.dropna(subset=["fund_id", "year", "balance", "spend"])

    # Ensure exactly 3 years per fund
    counts = df.groupby("fund_id")["year"].nunique()
    valid_funds = counts[counts == 3].index
    df = df[df["fund_id"].isin(valid_funds)]

    # Exclude funds with non-positive balance in any year
    valid_balance = df.groupby("fund_id")["balance"].min() > 0
    valid_balance_funds = valid_balance[valid_balance].index
    df = df[df["fund_id"].isin(valid_balance_funds)]

    # Aggregate
    grouped = df.groupby("fund_id").agg(
        avg_balance=("balance", "mean"),
        avg_spend=("spend", "mean"),
        avg_revenue=("revenue", "mean")
    ).reset_index()

    # Define available funds
    if include_revenue:
        grouped["available"] = grouped["avg_balance"] + grouped["avg_revenue"]
    else:
        grouped["available"] = grouped["avg_balance"]

    # Avoid division issues
    grouped = grouped[grouped["available"] > 0]

    # Calculate spend rate
    grouped["spend_rate"] = grouped["avg_spend"] / grouped["available"]

    # Filter underspent funds
    underspent = grouped[grouped["spend_rate"] <= threshold]

    # Return required fields
    result = underspent[[
        "fund_id",
        "spend_rate",
        "avg_balance",
        "avg_spend"
    ]]

    return result.to_dict(orient="records")