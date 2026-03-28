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
        raise ValueError(
            "Invalid sheet structure. File must contain exactly 3 sheets named: Year1, Year2, Year3."
        )

    dfs = []

    for sheet in expected_sheets:
        df = pd.read_excel(xls, sheet_name=sheet)

        # 🔴 Check if sheet is empty
        if df.empty:
            raise ValueError(f"Sheet '{sheet}' is empty. Please ensure all three sheets contain data.")

        # Normalize column names (handles accidental spacing/case issues)
        df.columns = df.columns.str.strip().str.lower()

        required_cols = {"fund_id", "balance", "spend", "revenue"}

        # 🔴 Check required columns
        if not required_cols.issubset(df.columns):
            missing = required_cols - set(df.columns)
            raise ValueError(
                f"Sheet '{sheet}' is missing required columns: {', '.join(missing)}"
            )

        # 🔴 Convert numeric fields
        df["balance"] = pd.to_numeric(df["balance"], errors="coerce")
        df["spend"] = pd.to_numeric(df["spend"], errors="coerce")
        df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")

        # 🔴 Check for invalid numeric data
        if df[["balance", "spend"]].isnull().any().any():
            raise ValueError(
                f"Sheet '{sheet}' contains invalid or missing numeric values in balance or spend."
            )

        # 🔴 Drop rows missing fund_id
        df = df.dropna(subset=["fund_id"])

        if df.empty:
            raise ValueError(f"Sheet '{sheet}' contains no valid fund records.")

        dfs.append(df)

    # Merge all 3 years on fund_id
    merged = dfs[0]
    merged = merged.merge(dfs[1], on="fund_id", suffixes=("_y1", "_y2"))
    merged = merged.merge(dfs[2], on="fund_id")

    # Rename columns for year 3
    merged = merged.rename(columns={
        "balance": "balance_y3",
        "spend": "spend_y3",
        "revenue": "revenue_y3"
    })

    # 🔴 Ensure merged result is not empty
    if merged.empty:
        raise ValueError(
            "No matching fund_ids found across all three years. Ensure the same fund_id exists in each sheet."
        )

    # Filter valid balances
    valid_mask = (
        (merged["balance_y1"] > 0) &
        (merged["balance_y2"] > 0) &
        (merged["balance_y3"] > 0)
    )
    merged = merged[valid_mask]

    if merged.empty:
        raise ValueError(
            "No funds have positive balances across all three years."
        )

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

    # Available funds
    if include_revenue:
        merged["available"] = merged["avg_balance"] + merged["avg_revenue"]
    else:
        merged["available"] = merged["avg_balance"]

    # Avoid division issues
    merged = merged[merged["available"] > 0]

    if merged.empty:
        raise ValueError(
            "No funds have usable balance data after processing."
        )

    # Spend rate
    merged["spend_rate"] = merged["avg_spend"] / merged["available"]

    # Filter underspent
    underspent = merged[merged["spend_rate"] <= threshold]

    # Return results
    result = underspent[[
        "fund_id",
        "spend_rate",
        "avg_balance",
        "avg_spend"
    ]]

    return result.to_dict(orient="records")