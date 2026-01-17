from .core import Issue

def _check_class_imbalance(analyzer, threshold: float = 0.9):
    issues = []
    if analyzer.target_col and analyzer.target_col in analyzer.df.columns:
        counts = analyzer.df[analyzer.target_col].value_counts(normalize=True)
        if counts.max() > threshold:
            issues.append(
                Issue(
                    category="class_imbalance",
                    severity="warning",
                    column=analyzer.target_col,
                    description=f"Target '{analyzer.target_col}' is imbalanced ({float(counts.max()):.1%} in one class)",
                    impact_score="medium",
                    quick_fix="Options: \n- Resample data: Use oversampling (e.g., SMOTE) or undersampling (Pros: Balances classes; Cons: May introduce bias or lose data).\n- Use class weights: Adjust model weights for imbalance (Pros: Simple; Cons: Model-dependent).\n- Stratified sampling: Ensure balanced splits in training (Pros: Improves evaluation; Cons: Requires careful implementation).",
                )
            )
    return issues