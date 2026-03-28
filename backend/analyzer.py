import pandas as pd

def analyze_funds(file, threshold=0.0, include_revenue=False):
    # Load Excel file
    try:
        xls = pd.ExcelFile(file)
    except Exception:
        raise ValueError("Invalid file. Please upload a valid Excel (.xlsx) file.")

    # Enforce exact sheet names
    expected_sheets = ["Year1", "Year2", "Year3"]
    if sorted(xls.sheet_names) != sorted(expected_sheets):
        raise ValueError("Sheets must be named exactly: Year1, Year2, Year3")

    dfs = []

    # Read and validate each sheet in order
    for sheet in expected_sheets:
        df = pd.read_excel(xls, sheet_name=sheet)

        required_cols = {"fund_id", "balance", "spend", "revenue"}
        if not required_cols.issubset(df.columns):
            raise ValueError(
                f"Sheet '{sheet}' must contain columns: fund_id, balance, spend, revenue"
            )

        # Ensure numeric fields
        df["balance"] = pd.to_numeric(df["balance"], errors="coerce")
        df["spend"] = pd.to_numeric(df["spend"], errors="coerce")
        df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")

        # Drop invalid rows
        df = df.dropna(subset=["fund_id", "balance", "spend"])

        dfs.append(df)

    # Merge all 3 years on fund_id (inner join ensures presence in all years)
    merged = dfs[0]
    merged = merged.merge(dfs[1], on="fund_id", suffixes=("_y1", "_y2"))
    merged = merged.merge(dfs[2], on="fund_id")

    # Rename columns for year 3 (no suffix by default)
    merged = merged.rename(columns={
        "balance": "balance_y3",
        "spend": "spend_y3",
        "revenue": "revenue_y3"
    })

    # Exclude funds with non-positive balance in ANY year
    valid_mask = (
        (merged["balance_y1"] > 0) &
        (merged["balance_y2"] > 0) &
        (merged["balance_y3"] > 0)
    )
    merged = merged[valid_mask]

    # Calculate averages
    merged["avg_balance"] = merged[
        ["balance_y1", "balance_y2", "balance_y3"]
    ].mean(axis=1)

    merged["avg_spend"] = merged[
        ["spend_y1", "spend_y2", "spend_y3"]
    ].mean(axis=1)

    merged["avg_revenue"] = merged[
        ["revenue_y1", "revenue_y2", "revenue_y3"]
    ].mean(axis=1)

    # Define available funds
    if include_revenue:
        merged["available"] = merged["avg_balance"] + merged["avg_revenue"]
    else:
        merged["available"] = merged["avg_balance"]

    # Avoid division issues
    merged = merged[merged["available"] > 0]

    # Calculate spend rate
    merged["spend_rate"] = merged["avg_spend"] / merged["available"]

    # Filter underspent funds
    underspent = merged[merged["spend_rate"] <= threshold]

    # Return required fields
    result = underspent[[
        "fund_id",
        "spend_rate",
        "avg_balance",
        "avg_spend"
    ]]

    return result.to_dict(orient="records")