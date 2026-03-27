import pandas as pd

def analyze_funds(file, threshold=0.0, include_revenue=False):
    # Load Excel file
    xls = pd.ExcelFile(file)

    # Validate number of sheets
    if len(xls.sheet_names) != 3:
        raise ValueError("File must contain exactly 3 sheets (one per year)")

    dfs = []

    # Read and validate each sheet
    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet)

        required_cols = {"fund_id", "balance", "spend", "revenue"}
        if not required_cols.issubset(df.columns):
            raise ValueError(f"Sheet '{sheet}' is missing required columns: {required_cols}")

        dfs.append(df)

    # Merge all 3 years on fund_id
    merged = dfs[0]
    merged = merged.merge(dfs[1], on="fund_id", suffixes=("_y1", "_y2"))
    merged = merged.merge(dfs[2], on="fund_id")

    # Rename columns for clarity
    merged = merged.rename(columns={
        "balance": "balance_y3",
        "spend": "spend_y3",
        "revenue": "revenue_y3"
    })

    # Drop funds not present in all 3 years (inner merge already handles this)

    # Exclude invalid funds (balance <= 0 in ANY year)
    valid_mask = (
        (merged["balance_y1"] > 0) &
        (merged["balance_y2"] > 0) &
        (merged["balance_y3"] > 0)
    )

    merged = merged[valid_mask]

    # Calculate averages
    merged["avg_balance"] = merged[["balance_y1", "balance_y2", "balance_y3"]].mean(axis=1)
    merged["avg_spend"] = merged[["spend_y1", "spend_y2", "spend_y3"]].mean(axis=1)
    merged["avg_revenue"] = merged[["revenue_y1", "revenue_y2", "revenue_y3"]].mean(axis=1)

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

    # Return only needed fields
    result = underspent[[
        "fund_id",
        "spend_rate",
        "avg_balance",
        "avg_spend"
    ]]

    return result.to_dict(orient="records")