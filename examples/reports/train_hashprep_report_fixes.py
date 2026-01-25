"""
Auto-generated data cleaning script by HashPrep.
Review and adapt before production use.
"""

from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from sklearn.preprocessing import RobustScaler
import numpy as np
import pandas as pd


def apply_fixes(df):
    """Apply data quality fixes to DataFrame."""
    df = df.copy()

    # Column 'Cabin' has 77% missing values
    df = df.drop(columns=['Cabin'])

    # Frequency encode high-cardinality column 'Name'
    freq_Name = df['Name'].value_counts(normalize=True)
    df['Name_encoded'] = df['Name'].map(freq_Name)

    # Frequency encode high-cardinality column 'Ticket'
    freq_Ticket = df['Ticket'].value_counts(normalize=True)
    df['Ticket_encoded'] = df['Ticket'].map(freq_Ticket)

    # Clip outliers in 'Fare' using IQR method
    q1_Fare, q3_Fare = df['Fare'].quantile([0.25, 0.75])
    iqr_Fare = q3_Fare - q1_Fare
    lower_Fare, upper_Fare = q1_Fare - 1.5 * iqr_Fare, q3_Fare + 1.5 * iqr_Fare
    df['Fare'] = df['Fare'].clip(lower=lower_Fare, upper=upper_Fare)

    # Clip outliers in 'Parch' using IQR method
    q1_Parch, q3_Parch = df['Parch'].quantile([0.25, 0.75])
    iqr_Parch = q3_Parch - q1_Parch
    lower_Parch, upper_Parch = q1_Parch - 1.5 * iqr_Parch, q3_Parch + 1.5 * iqr_Parch
    df['Parch'] = df['Parch'].clip(lower=lower_Parch, upper=upper_Parch)

    # Clip outliers in 'SibSp' using IQR method
    q1_SibSp, q3_SibSp = df['SibSp'].quantile([0.25, 0.75])
    iqr_SibSp = q3_SibSp - q1_SibSp
    lower_SibSp, upper_SibSp = q1_SibSp - 1.5 * iqr_SibSp, q3_SibSp + 1.5 * iqr_SibSp
    df['SibSp'] = df['SibSp'].clip(lower=lower_SibSp, upper=upper_SibSp)

    # Drop highly correlated column 'Survived,Sex'
    df = df.drop(columns=['Survived,Sex'])

    return df


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print('Usage: python fixes.py <input.csv> [output.csv]')
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'cleaned_data.csv'

    df = pd.read_csv(input_file)
    df_clean = apply_fixes(df)
    df_clean.to_csv(output_file, index=False)
    print(f'Cleaned data saved to {output_file}')