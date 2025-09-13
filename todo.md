# TODOs:

# Critical & Warning Checks (already exist, unchanged)
[ ] _check_data_leakage()
[ ] _check_high_missing_values()
[ ] _check_empty_columns()
[ ] _check_single_value_columns()
[ ] _check_target_leakage_patterns()
[ ] _check_class_imbalance()
[ ] _check_high_cardinality()
[ ] _check_duplicates()
[ ] _check_mixed_data_types()
[ ] _check_outliers()
[ ] _check_feature_correlation()

# Overview Section
[X] _summarize_dataset_info()
[X] _summarize_variable_types()
[X] _add_reproduction_info()

# Variables Section
[X] _summarize_variables()
    [X] _summarize_numeric_column(col: str):
    [ ] _summarize_categorical_column(col: str):
    [ ] _summarize_text_column(col: str):
    [ ] _summarize_datetime_column(col: str):

# Interactions Section
[ ] _summarize_interactions()
    [ ] _scatter_plots_numeric()
    [ ] _compute_correlation_matrices()
    [ ] _compute_categorical_correlations()
    [ ] _compute_mixed_correlations()

# Correlations Section (extension of _check_feature_correlation?)
[ ] _summarize_correlations()

# Missing Values Section
[ ] _summarize_missing_values()

# Dataset Sample Section
[X] _get_dataset_preview()