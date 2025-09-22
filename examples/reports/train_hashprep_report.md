# Dataset Quality Report

File: datasets/train.csv
Generated: 2025-09-22 23:22:53
HashPrep Version: 1.0.0-MVP

## Executive Summary
- Critical Issues: 13
- Warnings: 38
- Rows: 891
- Columns: 12

## Issues Overview

| Category | Severity | Column | Description | Impact | Quick Fix |
|----------|----------|--------|-------------|--------|-----------|
| missing_values | critical | Cabin | 77.1% missing values in 'Cabin' | high | Options:  • Drop column: Reduces bias from missing data (Pros: Simplifies model; Cons: Loses potential info). • Impute values: Use domain-informed methods (e.g., median, mode, or predictive model) (Pros: Retains feature; Cons: May introduce bias). • Create missingness indicator: Flag missing values as a new feature (Pros: Captures missingness pattern; Cons: Adds complexity). |
| high_cardinality | critical | Name | Column 'Name' has 891 unique values (100.0% of rows) | high | Options:  • Drop column: Avoids overfitting from unique identifiers (Pros: Simplifies model; Cons: Loses potential info). • Engineer feature: Extract patterns (e.g., titles from names) (Pros: Retains useful info; Cons: Requires domain knowledge). • Use hashing: Reduce dimensionality (Pros: Scalable; Cons: May lose interpretability). |
| high_cardinality | warning | Ticket | Column 'Ticket' has 681 unique values (76.4% of rows) | medium | Options:  • Group rare categories: Reduce cardinality (Pros: Simplifies feature; Cons: May lose nuance). • Use feature hashing: Map to lower dimensions (Pros: Scalable; Cons: Less interpretable). • Retain and test: Evaluate feature importance (Pros: Data-driven; Cons: Risk of overfitting). |
| high_cardinality | warning | Cabin | Column 'Cabin' has 147 unique values (16.5% of rows) | medium | Options:  • Group rare categories: Reduce cardinality (Pros: Simplifies feature; Cons: May lose nuance). • Use feature hashing: Map to lower dimensions (Pros: Scalable; Cons: Less interpretable). • Retain and test: Evaluate feature importance (Pros: Data-driven; Cons: Risk of overfitting). |
| outliers | warning | SibSp | Column 'SibSp' has 12 potential outliers (1.3% of non-missing values) | medium | Options:  • Investigate outliers: Verify if valid or errors (Pros: Ensures accuracy; Cons: Time-consuming). • Transform: Use log/sqrt to reduce impact (Pros: Retains data; Cons: Changes interpretation). • Retain and test: Use robust models (e.g., trees) (Pros: Keeps info; Cons: May affect sensitive models). |
| outliers | warning | Parch | Column 'Parch' has 10 potential outliers (1.1% of non-missing values) | medium | Options:  • Investigate outliers: Verify if valid or errors (Pros: Ensures accuracy; Cons: Time-consuming). • Transform: Use log/sqrt to reduce impact (Pros: Retains data; Cons: Changes interpretation). • Retain and test: Use robust models (e.g., trees) (Pros: Keeps info; Cons: May affect sensitive models). |
| outliers | warning | Fare | Column 'Fare' has 11 potential outliers (1.2% of non-missing values) | medium | Options:  • Investigate outliers: Verify if valid or errors (Pros: Ensures accuracy; Cons: Time-consuming). • Transform: Use log/sqrt to reduce impact (Pros: Retains data; Cons: Changes interpretation). • Retain and test: Use robust models (e.g., trees) (Pros: Keeps info; Cons: May affect sensitive models). |
| feature_correlation | critical | Name,Sex | Columns 'Name' and 'Sex' are highly associated (Cramer's V: 1.00) | high | Options:  • Drop one feature: Avoids overfitting from high redundancy (Pros: Simplifies model; Cons: Loses info). • Engineer feature: Extract common patterns (e.g., group categories) (Pros: Retains info; Cons: Requires domain knowledge). • Retain and test: Use robust models (e.g., trees) (Pros: Keeps info; Cons: May affect sensitive models). |
| feature_correlation | critical | Name,Ticket | Columns 'Name' and 'Ticket' are highly associated (Cramer's V: 1.00) | high | Options:  • Drop one feature: Avoids overfitting from high redundancy (Pros: Simplifies model; Cons: Loses info). • Engineer feature: Extract common patterns (e.g., group categories) (Pros: Retains info; Cons: Requires domain knowledge). • Retain and test: Use robust models (e.g., trees) (Pros: Keeps info; Cons: May affect sensitive models). |
| feature_correlation | critical | Name,Cabin | Columns 'Name' and 'Cabin' are highly associated (Cramer's V: 1.00) | high | Options:  • Drop one feature: Avoids overfitting from high redundancy (Pros: Simplifies model; Cons: Loses info). • Engineer feature: Extract common patterns (e.g., group categories) (Pros: Retains info; Cons: Requires domain knowledge). • Retain and test: Use robust models (e.g., trees) (Pros: Keeps info; Cons: May affect sensitive models). |
| feature_correlation | critical | Name,Embarked | Columns 'Name' and 'Embarked' are highly associated (Cramer's V: 1.00) | high | Options:  • Drop one feature: Avoids overfitting from high redundancy (Pros: Simplifies model; Cons: Loses info). • Engineer feature: Extract common patterns (e.g., group categories) (Pros: Retains info; Cons: Requires domain knowledge). • Retain and test: Use robust models (e.g., trees) (Pros: Keeps info; Cons: May affect sensitive models). |
| feature_correlation | warning | Sex,Ticket | Columns 'Sex' and 'Ticket' are highly associated (Cramer's V: 0.86) | medium | Options:  • Drop one feature: If less predictive (Pros: Simplifies model; Cons: Loses info). • Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: Risk of redundancy). • Engineer feature: Group categories or encode differently (Pros: Reduces redundancy; Cons: Adds complexity). |
| feature_correlation | warning | Sex,Cabin | Columns 'Sex' and 'Cabin' are highly associated (Cramer's V: 0.86) | medium | Options:  • Drop one feature: If less predictive (Pros: Simplifies model; Cons: Loses info). • Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: Risk of redundancy). • Engineer feature: Group categories or encode differently (Pros: Reduces redundancy; Cons: Adds complexity). |
| feature_correlation | warning | Ticket,Cabin | Columns 'Ticket' and 'Cabin' are highly associated (Cramer's V: 0.95) | medium | Options:  • Drop one feature: If less predictive (Pros: Simplifies model; Cons: Loses info). • Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: Risk of redundancy). • Engineer feature: Group categories or encode differently (Pros: Reduces redundancy; Cons: Adds complexity). |
| feature_correlation | critical | Ticket,Embarked | Columns 'Ticket' and 'Embarked' are highly associated (Cramer's V: 1.00) | high | Options:  • Drop one feature: Avoids overfitting from high redundancy (Pros: Simplifies model; Cons: Loses info). • Engineer feature: Extract common patterns (e.g., group categories) (Pros: Retains info; Cons: Requires domain knowledge). • Retain and test: Use robust models (e.g., trees) (Pros: Keeps info; Cons: May affect sensitive models). |
| feature_correlation | warning | Cabin,Embarked | Columns 'Cabin' and 'Embarked' are highly associated (Cramer's V: 0.95) | medium | Options:  • Drop one feature: If less predictive (Pros: Simplifies model; Cons: Loses info). • Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: Risk of redundancy). • Engineer feature: Group categories or encode differently (Pros: Reduces redundancy; Cons: Adds complexity). |
| feature_correlation | critical | Sex,Survived | Columns 'Sex' and 'Survived' show strong association (F: 372.41, p: 0.0000) | high | Options:  • Drop one feature: Avoids redundancy (Pros: Simplifies model; Cons: Loses info). • Engineer feature: Transform categorical or numeric feature (Pros: Retains info; Cons: Adds complexity). • Retain and test: Use robust models (e.g., trees) (Pros: Keeps info; Cons: May affect sensitive models). |
| feature_correlation | warning | Sex,Pclass | Columns 'Sex' and 'Pclass' show strong association (F: 15.74, p: 0.0001) | medium | Options:  • Drop one feature: If less predictive (Pros: Simplifies model; Cons: Loses info). • Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: Risk of redundancy). • Engineer feature: Transform or encode differently (Pros: Reduces redundancy; Cons: Adds complexity). |
| feature_correlation | warning | Sex,Age | Columns 'Sex' and 'Age' show strong association (F: 6.25, p: 0.0127) | medium | Options:  • Drop one feature: If less predictive (Pros: Simplifies model; Cons: Loses info). • Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: Risk of redundancy). • Engineer feature: Transform or encode differently (Pros: Reduces redundancy; Cons: Adds complexity). |
| feature_correlation | warning | Sex,SibSp | Columns 'Sex' and 'SibSp' show strong association (F: 11.84, p: 0.0006) | medium | Options:  • Drop one feature: If less predictive (Pros: Simplifies model; Cons: Loses info). • Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: Risk of redundancy). • Engineer feature: Transform or encode differently (Pros: Reduces redundancy; Cons: Adds complexity). |
| feature_correlation | critical | Sex,Parch | Columns 'Sex' and 'Parch' show strong association (F: 57.01, p: 0.0000) | high | Options:  • Drop one feature: Avoids redundancy (Pros: Simplifies model; Cons: Loses info). • Engineer feature: Transform categorical or numeric feature (Pros: Retains info; Cons: Adds complexity). • Retain and test: Use robust models (e.g., trees) (Pros: Keeps info; Cons: May affect sensitive models). |
| feature_correlation | critical | Sex,Fare | Columns 'Sex' and 'Fare' show strong association (F: 30.57, p: 0.0000) | high | Options:  • Drop one feature: Avoids redundancy (Pros: Simplifies model; Cons: Loses info). • Engineer feature: Transform categorical or numeric feature (Pros: Retains info; Cons: Adds complexity). • Retain and test: Use robust models (e.g., trees) (Pros: Keeps info; Cons: May affect sensitive models). |
| feature_correlation | warning | Ticket,Survived | Columns 'Ticket' and 'Survived' show strong association (F: 3.03, p: 0.0000) | medium | Options:  • Drop one feature: If less predictive (Pros: Simplifies model; Cons: Loses info). • Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: Risk of redundancy). • Engineer feature: Transform or encode differently (Pros: Reduces redundancy; Cons: Adds complexity). |
| feature_correlation | warning | Ticket,Age | Columns 'Ticket' and 'Age' show strong association (F: 1.72, p: 0.0007) | medium | Options:  • Drop one feature: If less predictive (Pros: Simplifies model; Cons: Loses info). • Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: Risk of redundancy). • Engineer feature: Transform or encode differently (Pros: Reduces redundancy; Cons: Adds complexity). |
| feature_correlation | warning | Ticket,SibSp | Columns 'Ticket' and 'SibSp' show strong association (F: 9.63, p: 0.0000) | medium | Options:  • Drop one feature: If less predictive (Pros: Simplifies model; Cons: Loses info). • Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: Risk of redundancy). • Engineer feature: Transform or encode differently (Pros: Reduces redundancy; Cons: Adds complexity). |
| feature_correlation | warning | Ticket,Parch | Columns 'Ticket' and 'Parch' show strong association (F: 4.28, p: 0.0000) | medium | Options:  • Drop one feature: If less predictive (Pros: Simplifies model; Cons: Loses info). • Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: Risk of redundancy). • Engineer feature: Transform or encode differently (Pros: Reduces redundancy; Cons: Adds complexity). |
| feature_correlation | critical | Ticket,Fare | Columns 'Ticket' and 'Fare' show strong association (F: 12866198.63, p: 0.0000) | high | Options:  • Drop one feature: Avoids redundancy (Pros: Simplifies model; Cons: Loses info). • Engineer feature: Transform categorical or numeric feature (Pros: Retains info; Cons: Adds complexity). • Retain and test: Use robust models (e.g., trees) (Pros: Keeps info; Cons: May affect sensitive models). |
| feature_correlation | warning | Cabin,PassengerId | Columns 'Cabin' and 'PassengerId' show strong association (F: 1.90, p: 0.0109) | medium | Options:  • Drop one feature: If less predictive (Pros: Simplifies model; Cons: Loses info). • Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: Risk of redundancy). • Engineer feature: Transform or encode differently (Pros: Reduces redundancy; Cons: Adds complexity). |
| feature_correlation | warning | Cabin,Age | Columns 'Cabin' and 'Age' show strong association (F: 2.48, p: 0.0012) | medium | Options:  • Drop one feature: If less predictive (Pros: Simplifies model; Cons: Loses info). • Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: Risk of redundancy). • Engineer feature: Transform or encode differently (Pros: Reduces redundancy; Cons: Adds complexity). |
| feature_correlation | warning | Cabin,SibSp | Columns 'Cabin' and 'SibSp' show strong association (F: 10.23, p: 0.0000) | medium | Options:  • Drop one feature: If less predictive (Pros: Simplifies model; Cons: Loses info). • Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: Risk of redundancy). • Engineer feature: Transform or encode differently (Pros: Reduces redundancy; Cons: Adds complexity). |
| feature_correlation | warning | Cabin,Parch | Columns 'Cabin' and 'Parch' show strong association (F: 11.93, p: 0.0000) | medium | Options:  • Drop one feature: If less predictive (Pros: Simplifies model; Cons: Loses info). • Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: Risk of redundancy). • Engineer feature: Transform or encode differently (Pros: Reduces redundancy; Cons: Adds complexity). |
| feature_correlation | warning | Cabin,Fare | Columns 'Cabin' and 'Fare' show strong association (F: 5.13, p: 0.0000) | medium | Options:  • Drop one feature: If less predictive (Pros: Simplifies model; Cons: Loses info). • Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: Risk of redundancy). • Engineer feature: Transform or encode differently (Pros: Reduces redundancy; Cons: Adds complexity). |
| feature_correlation | warning | Embarked,Survived | Columns 'Embarked' and 'Survived' show strong association (F: 13.61, p: 0.0000) | medium | Options:  • Drop one feature: If less predictive (Pros: Simplifies model; Cons: Loses info). • Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: Risk of redundancy). • Engineer feature: Transform or encode differently (Pros: Reduces redundancy; Cons: Adds complexity). |
| feature_correlation | critical | Embarked,Pclass | Columns 'Embarked' and 'Pclass' show strong association (F: 46.51, p: 0.0000) | high | Options:  • Drop one feature: Avoids redundancy (Pros: Simplifies model; Cons: Loses info). • Engineer feature: Transform categorical or numeric feature (Pros: Retains info; Cons: Adds complexity). • Retain and test: Use robust models (e.g., trees) (Pros: Keeps info; Cons: May affect sensitive models). |
| feature_correlation | warning | Embarked,Parch | Columns 'Embarked' and 'Parch' show strong association (F: 3.23, p: 0.0402) | medium | Options:  • Drop one feature: If less predictive (Pros: Simplifies model; Cons: Loses info). • Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: Risk of redundancy). • Engineer feature: Transform or encode differently (Pros: Reduces redundancy; Cons: Adds complexity). |
| feature_correlation | critical | Embarked,Fare | Columns 'Embarked' and 'Fare' show strong association (F: 38.14, p: 0.0000) | high | Options:  • Drop one feature: Avoids redundancy (Pros: Simplifies model; Cons: Loses info). • Engineer feature: Transform categorical or numeric feature (Pros: Retains info; Cons: Adds complexity). • Retain and test: Use robust models (e.g., trees) (Pros: Keeps info; Cons: May affect sensitive models). |
| high_zero_counts | warning | Survived | Column 'Survived' has 61.6% zero values | medium | Options:  • Transform: Create binary indicator for zeros (Pros: Captures pattern; Cons: Adds complexity). • Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: May skew results). • Investigate zeros: Verify validity (Pros: Ensures accuracy; Cons: Time-consuming). |
| high_zero_counts | warning | SibSp | Column 'SibSp' has 68.2% zero values | medium | Options:  • Transform: Create binary indicator for zeros (Pros: Captures pattern; Cons: Adds complexity). • Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: May skew results). • Investigate zeros: Verify validity (Pros: Ensures accuracy; Cons: Time-consuming). |
| high_zero_counts | warning | Parch | Column 'Parch' has 76.1% zero values | medium | Options:  • Transform: Create binary indicator for zeros (Pros: Captures pattern; Cons: Adds complexity). • Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: May skew results). • Investigate zeros: Verify validity (Pros: Ensures accuracy; Cons: Time-consuming). |
| missing_patterns | warning | Age | Missingness in 'Age' correlates with 'Ticket' (p: 0.0000) | medium | Options:  • Impute values: Use simple or domain-informed methods (Pros: Retains feature; Cons: Risk of bias). • Drop column: If less critical (Pros: Simplifies model; Cons: Loses info). • Test impact: Evaluate model with/without feature (Pros: Data-driven; Cons: Requires computation). |
| missing_patterns | warning | Age | Missingness in 'Age' correlates with 'Embarked' (p: 0.0000) | medium | Options:  • Impute values: Use simple or domain-informed methods (Pros: Retains feature; Cons: Risk of bias). • Drop column: If less critical (Pros: Simplifies model; Cons: Loses info). • Test impact: Evaluate model with/without feature (Pros: Data-driven; Cons: Requires computation). |
| missing_patterns | warning | Age | Missingness in 'Age' correlates with numeric 'Survived' (F: 7.62, p: 0.0059) | medium | Options:  • Impute values: Use simple or domain-informed methods (Pros: Retains feature; Cons: Risk of bias). • Drop column: If less critical (Pros: Simplifies model; Cons: Loses info). • Test impact: Evaluate model with/without feature (Pros: Data-driven; Cons: Requires computation). |
| missing_patterns | warning | Age | Missingness in 'Age' correlates with numeric 'Pclass' (F: 27.41, p: 0.0000) | medium | Options:  • Impute values: Use simple or domain-informed methods (Pros: Retains feature; Cons: Risk of bias). • Drop column: If less critical (Pros: Simplifies model; Cons: Loses info). • Test impact: Evaluate model with/without feature (Pros: Data-driven; Cons: Requires computation). |
| missing_patterns | warning | Age | Missingness in 'Age' correlates with numeric 'Parch' (F: 13.91, p: 0.0002) | medium | Options:  • Impute values: Use simple or domain-informed methods (Pros: Retains feature; Cons: Risk of bias). • Drop column: If less critical (Pros: Simplifies model; Cons: Loses info). • Test impact: Evaluate model with/without feature (Pros: Data-driven; Cons: Requires computation). |
| missing_patterns | warning | Age | Missingness in 'Age' correlates with numeric 'Fare' (F: 9.11, p: 0.0026) | medium | Options:  • Impute values: Use simple or domain-informed methods (Pros: Retains feature; Cons: Risk of bias). • Drop column: If less critical (Pros: Simplifies model; Cons: Loses info). • Test impact: Evaluate model with/without feature (Pros: Data-driven; Cons: Requires computation). |
| missing_patterns | warning | Cabin | Missingness in 'Cabin' correlates with 'Sex' (p: 0.0000) | medium | Options:  • Impute values: Use simple or domain-informed methods (Pros: Retains feature; Cons: Risk of bias). • Drop column: If less critical (Pros: Simplifies model; Cons: Loses info). • Test impact: Evaluate model with/without feature (Pros: Data-driven; Cons: Requires computation). |
| missing_patterns | warning | Cabin | Missingness in 'Cabin' correlates with 'Embarked' (p: 0.0000) | medium | Options:  • Impute values: Use simple or domain-informed methods (Pros: Retains feature; Cons: Risk of bias). • Drop column: If less critical (Pros: Simplifies model; Cons: Loses info). • Test impact: Evaluate model with/without feature (Pros: Data-driven; Cons: Requires computation). |
| missing_patterns | warning | Cabin | Missingness in 'Cabin' correlates with numeric 'Survived' (F: 99.25, p: 0.0000) | medium | Options:  • Impute values: Use simple or domain-informed methods (Pros: Retains feature; Cons: Risk of bias). • Drop column: If less critical (Pros: Simplifies model; Cons: Loses info). • Test impact: Evaluate model with/without feature (Pros: Data-driven; Cons: Requires computation). |
| missing_patterns | warning | Cabin | Missingness in 'Cabin' correlates with numeric 'Pclass' (F: 988.15, p: 0.0000) | medium | Options:  • Impute values: Use simple or domain-informed methods (Pros: Retains feature; Cons: Risk of bias). • Drop column: If less critical (Pros: Simplifies model; Cons: Loses info). • Test impact: Evaluate model with/without feature (Pros: Data-driven; Cons: Requires computation). |
| missing_patterns | warning | Cabin | Missingness in 'Cabin' correlates with numeric 'Age' (F: 47.36, p: 0.0000) | medium | Options:  • Impute values: Use simple or domain-informed methods (Pros: Retains feature; Cons: Risk of bias). • Drop column: If less critical (Pros: Simplifies model; Cons: Loses info). • Test impact: Evaluate model with/without feature (Pros: Data-driven; Cons: Requires computation). |
| missing_patterns | warning | Cabin | Missingness in 'Cabin' correlates with numeric 'Fare' (F: 269.15, p: 0.0000) | medium | Options:  • Impute values: Use simple or domain-informed methods (Pros: Retains feature; Cons: Risk of bias). • Drop column: If less critical (Pros: Simplifies model; Cons: Loses info). • Test impact: Evaluate model with/without feature (Pros: Data-driven; Cons: Requires computation). |

## Dataset Preview

### Head

|   PassengerId |   Survived |   Pclass | Name                                                | Sex    |   Age |   SibSp |   Parch | Ticket           |    Fare | Cabin   | Embarked   |
|--------------:|-----------:|---------:|:----------------------------------------------------|:-------|------:|--------:|--------:|:-----------------|--------:|:--------|:-----------|
|             1 |          0 |        3 | Braund, Mr. Owen Harris                             | male   |    22 |       1 |       0 | A/5 21171        |  7.25   | nan     | S          |
|             2 |          1 |        1 | Cumings, Mrs. John Bradley (Florence Briggs Thayer) | female |    38 |       1 |       0 | PC 17599         | 71.2833 | C85     | C          |
|             3 |          1 |        3 | Heikkinen, Miss. Laina                              | female |    26 |       0 |       0 | STON/O2. 3101282 |  7.925  | nan     | S          |
|             4 |          1 |        1 | Futrelle, Mrs. Jacques Heath (Lily May Peel)        | female |    35 |       1 |       0 | 113803           | 53.1    | C123    | S          |
|             5 |          0 |        3 | Allen, Mr. William Henry                            | male   |    35 |       0 |       0 | 373450           |  8.05   | nan     | S          |

### Tail

|   PassengerId |   Survived |   Pclass | Name                                     | Sex    |   Age |   SibSp |   Parch | Ticket     |   Fare | Cabin   | Embarked   |
|--------------:|-----------:|---------:|:-----------------------------------------|:-------|------:|--------:|--------:|:-----------|-------:|:--------|:-----------|
|           887 |          0 |        2 | Montvila, Rev. Juozas                    | male   |    27 |       0 |       0 | 211536     |  13    | nan     | S          |
|           888 |          1 |        1 | Graham, Miss. Margaret Edith             | female |    19 |       0 |       0 | 112053     |  30    | B42     | S          |
|           889 |          0 |        3 | Johnston, Miss. Catherine Helen "Carrie" | female |   nan |       1 |       2 | W./C. 6607 |  23.45 | nan     | S          |
|           890 |          1 |        1 | Behr, Mr. Karl Howell                    | male   |    26 |       0 |       0 | 111369     |  30    | C148    | C          |
|           891 |          0 |        3 | Dooley, Mr. Patrick                      | male   |    32 |       0 |       0 | 370376     |   7.75 | nan     | Q          |

### Sample

|   PassengerId |   Survived |   Pclass | Name                                                     | Sex    |   Age |   SibSp |   Parch | Ticket     |    Fare | Cabin   | Embarked   |
|--------------:|-----------:|---------:|:---------------------------------------------------------|:-------|------:|--------:|--------:|:-----------|--------:|:--------|:-----------|
|           770 |          0 |        3 | Gronnestad, Mr. Daniel Danielsen                         | male   |    32 |       0 |       0 | 8471       |  8.3625 | nan     | S          |
|           760 |          1 |        1 | Rothes, the Countess. of (Lucy Noel Martha Dyer-Edwards) | female |    33 |       0 |       0 | 110152     | 86.5    | B77     | S          |
|           807 |          0 |        1 | Andrews, Mr. Thomas Jr                                   | male   |    39 |       0 |       0 | 112050     |  0      | A36     | S          |
|            54 |          1 |        2 | Faunthorpe, Mrs. Lizzie (Elizabeth Anne Wilkinson)       | female |    29 |       1 |       0 | 2926       | 26      | nan     | S          |
|           802 |          1 |        2 | Collyer, Mrs. Harvey (Charlotte Annie Tate)              | female |    31 |       1 |       1 | C.A. 31921 | 26.25   | nan     | S          |
|           455 |          0 |        3 | Peduzzi, Mr. Joseph                                      | male   |   nan |       0 |       0 | A/5 2817   |  8.05   | nan     | S          |
|           725 |          1 |        1 | Chambers, Mr. Norman Campbell                            | male   |    27 |       1 |       0 | 113806     | 53.1    | E8      | S          |
|           275 |          1 |        3 | Healy, Miss. Hanora "Nora"                               | female |   nan |       0 |       0 | 370375     |  7.75   | nan     | Q          |
|           419 |          0 |        2 | Matthews, Mr. William John                               | male   |    30 |       0 |       0 | 28228      | 13      | nan     | S          |
|           763 |          1 |        3 | Barah, Mr. Hanna Assi                                    | male   |    20 |       0 |       0 | 2663       |  7.2292 | nan     | C          |

## Variables

### PassengerId

```yaml
count: 891
histogram:
  bin_edges:
  - 0.10999999999999999
  - 90.0
  - 179.0
  - 268.0
  - 357.0
  - 446.0
  - 535.0
  - 624.0
  - 713.0
  - 802.0
  - 891.0
  counts:
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - &id001 !!python/object/apply:numpy.dtype
        args:
        - f8
        - false
        - true
        state: !!python/tuple
        - 3
        - <
        - null
        - null
        - null
        - -1
        - -1
        - 0
      - !!binary |
        gZVDi2znuz8=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAACAVkA=
    - right
    : 90
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAACAVkA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAABgZkA=
    - right
    : 89
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAABgZkA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAADAcEA=
    - right
    : 89
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAADAcEA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAABQdkA=
    - right
    : 89
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAABQdkA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAADge0A=
    - right
    : 89
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAADge0A=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAAC4gEA=
    - right
    : 89
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAAC4gEA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAACAg0A=
    - right
    : 89
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAACAg0A=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAABIhkA=
    - right
    : 89
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAABIhkA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAAAQiUA=
    - right
    : 89
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAAAQiUA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAADYi0A=
    - right
    : 89
max: 891.0
mean: 446.0
min: 1.0
missing: 0
quantiles:
  25%: 223.5
  50%: 446.0
  75%: 668.5
std: 257.3538420152301
zeros: 0

```
### Survived

```yaml
count: 891
histogram:
  bin_edges:
  - -0.001
  - 0.1
  - 0.2
  - 0.30000000000000004
  - 0.4
  - 0.5
  - 0.6000000000000001
  - 0.7000000000000001
  - 0.8
  - 0.9
  - 1.0
  counts:
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - &id001 !!python/object/apply:numpy.dtype
        args:
        - f8
        - false
        - true
        state: !!python/tuple
        - 3
        - <
        - null
        - null
        - null
        - -1
        - -1
        - 0
      - !!binary |
        /Knx0k1iYL8=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        mpmZmZmZuT8=
    - right
    : 549
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        mpmZmZmZuT8=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        mpmZmZmZyT8=
    - right
    : 0
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        mpmZmZmZyT8=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        MzMzMzMz0z8=
    - right
    : 0
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        MzMzMzMz0z8=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        mpmZmZmZ2T8=
    - right
    : 0
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        mpmZmZmZ2T8=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAAAA4D8=
    - right
    : 0
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAAAA4D8=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        MzMzMzMz4z8=
    - right
    : 0
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        MzMzMzMz4z8=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        ZmZmZmZm5j8=
    - right
    : 0
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        ZmZmZmZm5j8=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        mpmZmZmZ6T8=
    - right
    : 0
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        mpmZmZmZ6T8=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        zczMzMzM7D8=
    - right
    : 0
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        zczMzMzM7D8=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAAAA8D8=
    - right
    : 342
max: 1.0
mean: 0.3838383838383838
min: 0.0
missing: 0
quantiles:
  25%: 0.0
  50%: 0.0
  75%: 1.0
std: 0.4865924542648575
zeros: 549

```
### Pclass

```yaml
count: 891
histogram:
  bin_edges:
  - 0.998
  - 1.2
  - 1.4
  - 1.6
  - 1.8
  - 2.0
  - 2.2
  - 2.4000000000000004
  - 2.6
  - 2.8
  - 3.0
  counts:
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - &id001 !!python/object/apply:numpy.dtype
        args:
        - f8
        - false
        - true
        state: !!python/tuple
        - 3
        - <
        - null
        - null
        - null
        - -1
        - -1
        - 0
      - !!binary |
        gZVDi2zn7z8=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        MzMzMzMz8z8=
    - right
    : 216
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        MzMzMzMz8z8=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        ZmZmZmZm9j8=
    - right
    : 0
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        ZmZmZmZm9j8=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        mpmZmZmZ+T8=
    - right
    : 0
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        mpmZmZmZ+T8=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        zczMzMzM/D8=
    - right
    : 0
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        zczMzMzM/D8=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAAAAAEA=
    - right
    : 184
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAAAAAEA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        mpmZmZmZAUA=
    - right
    : 0
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        mpmZmZmZAUA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        MzMzMzMzA0A=
    - right
    : 0
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        MzMzMzMzA0A=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        zczMzMzMBEA=
    - right
    : 0
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        zczMzMzMBEA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        ZmZmZmZmBkA=
    - right
    : 0
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        ZmZmZmZmBkA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAAAACEA=
    - right
    : 491
max: 3.0
mean: 2.308641975308642
min: 1.0
missing: 0
quantiles:
  25%: 2.0
  50%: 3.0
  75%: 3.0
std: 0.836071240977049
zeros: 0

```
### Name

```yaml
avg_length: 26.9652076318743
char_freq:
  ' ': 2735
  M: 1128
  a: 1657
  e: 1703
  i: 1325
  l: 1067
  n: 1304
  o: 1008
  r: 1958
  s: 1297
common_lengths:
  18: 50
  19: 64
  25: 55
  26: 49
  27: 50
count: 891
max_length: 82.0
min_length: 12.0
missing: 0

```
### Sex

```yaml
avg_length: 4.704826038159371
char_freq:
  a: 891
  e: 1205
  f: 314
  l: 891
  m: 891
common_lengths:
  4: 577
  6: 314
count: 891
max_length: 6.0
min_length: 4.0
missing: 0

```
### Age

```yaml
count: 714
histogram:
  bin_edges:
  - 0.34042
  - 8.378
  - 16.336000000000002
  - 24.294000000000004
  - 32.252
  - 40.21
  - 48.168000000000006
  - 56.126000000000005
  - 64.084
  - 72.042
  - 80.0
  counts:
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - &id001 !!python/object/apply:numpy.dtype
        args:
        - f8
        - false
        - true
        state: !!python/tuple
        - 3
        - <
        - null
        - null
        - null
        - -1
        - -1
        - 0
      - !!binary |
        GQRWDi2y1T8=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        qMZLN4nBIEA=
    - right
    : 54
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        qMZLN4nBIEA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        vHSTGARWMEA=
    - right
    : 46
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        vHSTGARWMEA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        JQaBlUNLOEA=
    - right
    : 177
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        JQaBlUNLOEA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        x0s3iUEgQEA=
    - right
    : 169
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        x0s3iUEgQEA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        exSuR+EaREA=
    - right
    : 118
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        exSuR+EaREA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        L90kBoEVSEA=
    - right
    : 70
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        L90kBoEVSEA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        46WbxCAQTEA=
    - right
    : 45
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        46WbxCAQTEA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        TDeJQWAFUEA=
    - right
    : 24
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        TDeJQWAFUEA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        ppvEILACUkA=
    - right
    : 9
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        ppvEILACUkA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAAAAVEA=
    - right
    : 2
max: 80.0
mean: 29.69911764705882
min: 0.42
missing: 177
quantiles:
  25%: 20.125
  50%: 28.0
  75%: 38.0
std: 14.526497332334042
zeros: 0

```
### SibSp

```yaml
count: 891
histogram:
  bin_edges:
  - -0.008
  - 0.8
  - 1.6
  - 2.4000000000000004
  - 3.2
  - 4.0
  - 4.800000000000001
  - 5.6000000000000005
  - 6.4
  - 7.2
  - 8.0
  counts:
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - &id001 !!python/object/apply:numpy.dtype
        args:
        - f8
        - false
        - true
        state: !!python/tuple
        - 3
        - <
        - null
        - null
        - null
        - -1
        - -1
        - 0
      - !!binary |
        PN9PjZdugr8=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        mpmZmZmZ6T8=
    - right
    : 608
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        mpmZmZmZ6T8=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        mpmZmZmZ+T8=
    - right
    : 209
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        mpmZmZmZ+T8=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        MzMzMzMzA0A=
    - right
    : 28
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        MzMzMzMzA0A=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        mpmZmZmZCUA=
    - right
    : 16
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        mpmZmZmZCUA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAAAAEEA=
    - right
    : 18
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAAAAEEA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        MzMzMzMzE0A=
    - right
    : 0
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        MzMzMzMzE0A=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        ZmZmZmZmFkA=
    - right
    : 5
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        ZmZmZmZmFkA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        mpmZmZmZGUA=
    - right
    : 0
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        mpmZmZmZGUA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        zczMzMzMHEA=
    - right
    : 0
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        zczMzMzMHEA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAAAAIEA=
    - right
    : 7
max: 8.0
mean: 0.5230078563411896
min: 0.0
missing: 0
quantiles:
  25%: 0.0
  50%: 0.0
  75%: 1.0
std: 1.1027434322934317
zeros: 608

```
### Parch

```yaml
count: 891
histogram:
  bin_edges:
  - -0.006
  - 0.6
  - 1.2
  - 1.7999999999999998
  - 2.4
  - 3.0
  - 3.5999999999999996
  - 4.2
  - 4.8
  - 5.3999999999999995
  - 6.0
  counts:
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - &id001 !!python/object/apply:numpy.dtype
        args:
        - f8
        - false
        - true
        state: !!python/tuple
        - 3
        - <
        - null
        - null
        - null
        - -1
        - -1
        - 0
      - !!binary |
        eekmMQisfL8=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        MzMzMzMz4z8=
    - right
    : 678
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        MzMzMzMz4z8=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        MzMzMzMz8z8=
    - right
    : 118
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        MzMzMzMz8z8=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        zczMzMzM/D8=
    - right
    : 0
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        zczMzMzM/D8=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        MzMzMzMzA0A=
    - right
    : 80
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        MzMzMzMzA0A=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAAAACEA=
    - right
    : 5
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAAAACEA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        zczMzMzMDEA=
    - right
    : 0
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        zczMzMzMDEA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        zczMzMzMEEA=
    - right
    : 4
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        zczMzMzMEEA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        MzMzMzMzE0A=
    - right
    : 0
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        MzMzMzMzE0A=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        mpmZmZmZFUA=
    - right
    : 5
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        mpmZmZmZFUA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        AAAAAAAAGEA=
    - right
    : 1
max: 6.0
mean: 0.38159371492704824
min: 0.0
missing: 0
quantiles:
  25%: 0.0
  50%: 0.0
  75%: 0.0
std: 0.8060572211299483
zeros: 678

```
### Ticket

```yaml
avg_length: 6.750841750841751
char_freq:
  '0': 406
  '1': 689
  '2': 594
  '3': 746
  '4': 464
  '5': 387
  '6': 422
  '7': 490
  '8': 282
  '9': 328
common_lengths:
  4: 101
  5: 131
  6: 419
  8: 76
  10: 41
count: 891
max_length: 18.0
min_length: 3.0
missing: 0

```
### Fare

```yaml
count: 891
histogram:
  bin_edges:
  - -0.5123292
  - 51.23292
  - 102.46584
  - 153.69876
  - 204.93168
  - 256.1646
  - 307.39752
  - 358.63044
  - 409.86336
  - 461.09628
  - 512.3292
  counts:
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - &id001 !!python/object/apply:numpy.dtype
        args:
        - f8
        - false
        - true
        state: !!python/tuple
        - 3
        - <
        - null
        - null
        - null
        - -1
        - -1
        - 0
      - !!binary |
        0SLb+X5q4L8=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        5/up8dKdSUA=
    - right
    : 732
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        5/up8dKdSUA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        5/up8dKdWUA=
    - right
    : 106
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        5/up8dKdWUA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        7nw/NV42Y0A=
    - right
    : 31
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        7nw/NV42Y0A=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        5/up8dKdaUA=
    - right
    : 2
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        5/up8dKdaUA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        cT0K16MCcEA=
    - right
    : 11
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        cT0K16MCcEA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        7nw/NV42c0A=
    - right
    : 6
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        7nw/NV42c0A=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        rkfhehRqdkA=
    - right
    : 0
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        rkfhehRqdkA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        K4cW2c6deUA=
    - right
    : 0
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        K4cW2c6deUA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        qMZLN4nRfEA=
    - right
    : 0
    ? !!python/object/apply:pandas._libs.interval.Interval
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        qMZLN4nRfEA=
    - !!python/object/apply:numpy._core.multiarray.scalar
      - *id001
      - !!binary |
        EoPAyqECgEA=
    - right
    : 3
max: 512.3292
mean: 32.204207968574636
min: 0.0
missing: 0
quantiles:
  25%: 7.9104
  50%: 14.4542
  75%: 31.0
std: 49.6934285971809
zeros: 15

```
### Cabin

```yaml
count: 204
missing: 687
most_frequent: B96 B98
top_values:
  B96 B98: 4
  C123: 2
  C22 C26: 3
  C23 C25 C27: 4
  C83: 2
  D: 3
  E101: 3
  F2: 3
  F33: 3
  G6: 4
unique: 147

```
### Embarked

```yaml
count: 889
missing: 2
most_frequent: S
top_values:
  C: 168
  Q: 77
  S: 644
unique: 3

```
## Correlations

### Numeric (Pearson)

```json
{json.dumps(summary['summaries'].get('numeric_correlations', {}).get('pearson', {}), indent=2)}
```
### Categorical (Cramer's V)

| Pair | Value |
|------|-------|
| Name__Sex | 1.00 |
| Name__Ticket | 1.00 |
| Name__Cabin | 1.00 |
| Name__Embarked | 1.00 |
| Sex__Ticket | 0.86 |
| Sex__Cabin | 0.86 |
| Sex__Embarked | 0.12 |
| Ticket__Cabin | 0.95 |
| Ticket__Embarked | 1.00 |
| Cabin__Embarked | 0.95 |

### Mixed

| Pair | F-Stat | P-Value |
|------|--------|---------|
| Sex__PassengerId | 1.64 | 0.2004 |
| Sex__Survived | 372.41 | 0.0000 |
| Sex__Pclass | 15.74 | 0.0001 |
| Sex__Age | 6.25 | 0.0127 |
| Sex__SibSp | 11.84 | 0.0006 |
| Sex__Parch | 57.01 | 0.0000 |
| Sex__Fare | 30.57 | 0.0000 |
| Ticket__PassengerId | 1.05 | 0.3676 |
| Ticket__Survived | 3.03 | 0.0000 |
| Ticket__Age | 1.72 | 0.0007 |
| Ticket__SibSp | 9.63 | 0.0000 |
| Ticket__Parch | 4.28 | 0.0000 |
| Ticket__Fare | 12866198.63 | 0.0000 |
| Cabin__PassengerId | 1.90 | 0.0109 |
| Cabin__Survived | 1.26 | 0.2054 |
| Cabin__Age | 2.48 | 0.0012 |
| Cabin__SibSp | 10.23 | 0.0000 |
| Cabin__Parch | 11.93 | 0.0000 |
| Cabin__Fare | 5.13 | 0.0000 |
| Embarked__PassengerId | 0.52 | 0.5941 |
| Embarked__Survived | 13.61 | 0.0000 |
| Embarked__Pclass | 46.51 | 0.0000 |
| Embarked__Age | 0.64 | 0.5294 |
| Embarked__SibSp | 2.18 | 0.1132 |
| Embarked__Parch | 3.23 | 0.0402 |
| Embarked__Fare | 38.14 | 0.0000 |

## Missing Values

| Column | Count | Percentage |
|--------|-------|------------|
| Age | 177 | 19.87 |
| Cabin | 687 | 77.1 |
| Embarked | 2 | 0.22 |

## Missing Patterns

```json
{json.dumps(summary['summaries']['missing_patterns'], indent=2)}
```

## Next Steps
- Address critical issues
- Handle warnings
- Re-analyze dataset

---
Generated by HashPrep