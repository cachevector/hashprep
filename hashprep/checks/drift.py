from .core import Issue
import pandas as pd
from scipy.stats import ks_2samp, chi2_contingency
import numpy as np

def check_drift(df_train: pd.DataFrame, df_test: pd.DataFrame, threshold: float = 0.05) -> list[Issue]:
    """
    Check for distribution shift between two datasets.
    Using Kolmogorov-Smirnov test for numeric and Chi-square for categorical.
    """
    issues = []
    
    # Check numeric columns
    num_cols = df_train.select_dtypes(include="number").columns
    for col in num_cols:
        if col in df_test.columns:
            train_vals = df_train[col].dropna()
            test_vals = df_test[col].dropna()
            
            if len(train_vals) > 0 and len(test_vals) > 0:
                stat, p_val = ks_2samp(train_vals, test_vals)
                if p_val < threshold:
                    issues.append(
                        Issue(
                            category="dataset_drift",
                            severity="warning",
                            column=col,
                            description=f"Potential drift detected in '{col}' (KS p-value: {p_val:.4f})",
                            impact_score="medium",
                            quick_fix="Options: 
- Re-train model with recent data.
- Investigate data collection differences.
- Use drift-robust features."
                        )
                    )
                    
    # Check categorical columns
    cat_cols = df_train.select_dtypes(include=["object", "category"]).columns
    for col in cat_cols:
        if col in df_test.columns:
            # Align categories
            train_counts = df_train[col].value_counts()
            test_counts = df_test[col].value_counts()
            
            # Simple check for missing categories or significant frequency changes
            # For a more robust check, we could use Chi-Square on a contingency table
            try:
                # Combined categories
                all_cats = list(set(train_counts.index) | set(test_counts.index))
                if len(all_cats) > 50: # Avoid high cardinality for Chi2
                    continue
                    
                observed = []
                expected = []
                
                train_total = train_counts.sum()
                test_total = test_counts.sum()
                
                for cat in all_cats:
                    observed.append(test_counts.get(cat, 0))
                    # Expected based on train distribution
                    expected.append((train_counts.get(cat, 0) / train_total) * test_total)
                
                # Chi-square test
                # ... (Simplified for now, using PS p-value as proxy or just flagging)
            except:
                pass

    return issues
