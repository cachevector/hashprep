from enum import Enum

import numpy as np
import pandas as pd


class DiscretizationType(Enum):
    UNIFORM = "uniform"
    QUANTILE = "quantile"


class Discretizer:
    def __init__(self, method=DiscretizationType.UNIFORM, n_bins=10):
        self.method = method
        self.n_bins = n_bins

    def discretize_series(self, series: pd.Series) -> pd.Series:
        if self.method == DiscretizationType.UNIFORM:
            return pd.cut(series, bins=self.n_bins, labels=False)
        elif self.method == DiscretizationType.QUANTILE:
            return pd.qcut(series, q=self.n_bins, labels=False)
        else:
            raise ValueError(f"Unknown discretization method {self.method}")

    def discretize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df_discretized = df.copy()
        for col in df_discretized.select_dtypes(include=np.number):
            df_discretized[col] = self.discretize_series(df_discretized[col])
        return df_discretized
