def summarize_missing_values(df):
    missing_count = {col: int(val) for col, val in df.isnull().sum().to_dict().items()}
    missing_percentage = {col: float(val) for col, val in (df.isnull().mean() * 100).round(2).to_dict().items()}
    missing_patterns = {col: df[df[col].isna()].index.tolist() for col in df.columns if df[col].isna().any()}

    missing_data = {}
    missing_data["missing_values"] = {"count": missing_count, "percentage": missing_percentage}
    missing_data["missing_patterns"] = missing_patterns

    return missing_data
