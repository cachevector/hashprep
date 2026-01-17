from .core import Issue

def _check_single_value_columns(analyzer):
    issues = []
    for col in analyzer.df.columns:
        if analyzer.df[col].nunique(dropna=True) == 1:
            impact = "low" if col != analyzer.target_col else "high"
            severity = "warning" if col != analyzer.target_col else "critical"
            quick_fix = (
                "Options: \n- Drop column: Not informative for modeling (Pros: Simplifies model; Cons: None).\n- Verify data: Ensure single value isn't an error (Pros: Validates data; Cons: Time-consuming)."
                if col != analyzer.target_col
                else "Options: \n- Redefine target: Replace with a more variable target (Pros: Enables modeling; Cons: Requires new data).\n- Stop analysis: Constant target prevents meaningful prediction (Pros: Avoids invalid model; Cons: Halts analysis)."
            )
            issues.append(
                Issue(
                    category="single_value",
                    severity=severity,
                    column=col,
                    description=f"Column '{col}' contains only one unique value",
                    impact_score=impact,
                    quick_fix=quick_fix,
                )
            )
    return issues

def _check_high_cardinality(analyzer, threshold: int = 100, critical_threshold: float = 0.9):
    issues = []
    categorical_cols = analyzer.df.select_dtypes(include="object").columns.tolist()
    for col in categorical_cols:
        unique_count = int(analyzer.df[col].nunique())
        unique_ratio = float(unique_count / len(analyzer.df))
        if unique_count > threshold:
            severity = "critical" if unique_ratio > critical_threshold else "warning"
            impact = "high" if severity == "critical" else "medium"
            quick_fix = (
                "Options: \n- Drop column: Avoids overfitting from unique identifiers (Pros: Simplifies model; Cons: Loses potential info).\n- Engineer feature: Extract patterns (e.g., titles from names) (Pros: Retains useful info; Cons: Requires domain knowledge).\n- Use hashing: Reduce dimensionality (Pros: Scalable; Cons: May lose interpretability)."
                if severity == "critical"
                else "Options: \n- Group rare categories: Reduce cardinality (Pros: Simplifies feature; Cons: May lose nuance).\n- Use feature hashing: Map to lower dimensions (Pros: Scalable; Cons: Less interpretable).\n- Retain and test: Evaluate feature importance (Pros: Data-driven; Cons: Risk of overfitting)."
            )
            issues.append(
                Issue(
                    category="high_cardinality",
                    severity=severity,
                    column=col,
                    description=f"Column '{col}' has {unique_count} unique values ({unique_ratio:.1%} of rows)",
                    impact_score=impact,
                    quick_fix=quick_fix,
                )
            )
    return issues

def _check_duplicates(analyzer):
    issues = []
    duplicate_rows = int(analyzer.df.duplicated().sum())
    if duplicate_rows > 0:
        duplicate_ratio = float(duplicate_rows / len(analyzer.df))
        severity = "critical" if duplicate_ratio > 0.1 else "warning"
        impact = "high" if severity == "critical" else "medium"
        quick_fix = (
            "Options: \n- Drop duplicates: Ensures data integrity (Pros: Cleaner data; Cons: May lose valid repeats).\n- Verify duplicates: Check if intentional (e.g., time-series) (Pros: Validates data; Cons: Time-consuming)."
            if severity == "critical"
            else "Options: \n- Drop duplicates: Simplifies dataset (Pros: Cleaner data; Cons: May lose valid repeats).\n- Keep duplicates: If meaningful (e.g., repeated events) (Pros: Retains info; Cons: May bias model).\n- Test impact: Evaluate model performance with/without duplicates (Pros: Data-driven; Cons: Requires computation)."
        )
        issues.append(
            Issue(
                category="duplicates",
                severity=severity,
                column="__all__",
                description=f"Dataset contains {duplicate_rows} duplicate rows ({duplicate_ratio:.1%} of rows)",
                impact_score=impact,
                quick_fix=quick_fix,
            )
        )
    return issues

def _check_mixed_data_types(analyzer):
    issues = []
    for col in analyzer.df.columns:
        types = analyzer.df[col].dropna().map(type).nunique()
        if types > 1:
            issues.append(
                Issue(
                    category="mixed_types",
                    severity="warning",
                    column=col,
                    description=f"Column '{col}' contains mixed data types",
                    impact_score="low",
                    quick_fix="Options: \n- Cast to single type: Ensure consistency (Pros: Simplifies processing; Cons: May lose nuance).\n- Split column: Separate types into new features (Pros: Preserves info; Cons: Adds complexity).\n- Investigate source: Check data collection errors (Pros: Improves quality; Cons: Time-consuming).",
                )
            )
    return issues