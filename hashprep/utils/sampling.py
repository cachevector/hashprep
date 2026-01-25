from dataclasses import dataclass, field
from typing import Dict, Literal, Optional, Tuple

import pandas as pd

DEFAULT_MAX_ROWS = 100_000
DEFAULT_MEMORY_THRESHOLD_MB = 500.0


@dataclass
class SamplingConfig:
    """Configuration for dataset sampling."""

    max_rows: int = DEFAULT_MAX_ROWS
    sample_method: Literal["random", "stratified", "systematic", "head"] = "random"
    random_state: Optional[int] = 42
    stratify_column: Optional[str] = None
    memory_threshold_mb: float = DEFAULT_MEMORY_THRESHOLD_MB
    enabled: bool = True


class DatasetSampler:
    """Handles sampling of large datasets for efficient analysis."""

    def __init__(self, config: Optional[SamplingConfig] = None):
        self.config = config or SamplingConfig()
        self.original_shape: Optional[Tuple[int, int]] = None
        self.sample_fraction: Optional[float] = None
        self.was_sampled: bool = False

    def should_sample(self, df: pd.DataFrame) -> bool:
        """Determine if dataset needs sampling based on size/memory."""
        if not self.config.enabled:
            return False

        row_threshold_exceeded = len(df) > self.config.max_rows
        memory_mb = df.memory_usage(deep=True).sum() / (1024**2)
        memory_threshold_exceeded = memory_mb > self.config.memory_threshold_mb

        return row_threshold_exceeded or memory_threshold_exceeded

    def sample(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sample the dataset according to configuration."""
        self.original_shape = df.shape

        if not self.should_sample(df):
            self.was_sampled = False
            self.sample_fraction = 1.0
            return df

        target_rows = min(self.config.max_rows, len(df))
        self.sample_fraction = target_rows / len(df)
        self.was_sampled = True

        method = self.config.sample_method

        if method == "random":
            return df.sample(n=target_rows, random_state=self.config.random_state)

        if method == "stratified":
            stratify_col = self.config.stratify_column
            if stratify_col and stratify_col in df.columns:
                return self._stratified_sample(df, target_rows)
            return df.sample(n=target_rows, random_state=self.config.random_state)

        if method == "systematic":
            step = max(1, len(df) // target_rows)
            return df.iloc[::step].head(target_rows)

        if method == "head":
            return df.head(target_rows)

        return df.sample(n=target_rows, random_state=self.config.random_state)

    def _stratified_sample(self, df: pd.DataFrame, target_rows: int) -> pd.DataFrame:
        """Stratified sampling preserving class distribution."""
        col = self.config.stratify_column
        if col is None or col not in df.columns:
            return df.sample(n=target_rows, random_state=self.config.random_state)

        groups = df.groupby(col, group_keys=False)
        proportions = df[col].value_counts(normalize=True)

        samples = []
        remaining = target_rows

        for name, group in groups:
            n_samples = max(1, int(proportions[name] * target_rows))
            n_samples = min(n_samples, len(group), remaining)
            if n_samples > 0:
                samples.append(
                    group.sample(n=n_samples, random_state=self.config.random_state)
                )
                remaining -= n_samples
            if remaining <= 0:
                break

        if not samples:
            return df.sample(n=target_rows, random_state=self.config.random_state)

        result = pd.concat(samples)

        if len(result) < target_rows and len(result) < len(df):
            additional_needed = min(target_rows - len(result), len(df) - len(result))
            remaining_indices = df.index.difference(result.index)
            additional = df.loc[remaining_indices].sample(
                n=additional_needed, random_state=self.config.random_state
            )
            result = pd.concat([result, additional])

        return result.sample(frac=1, random_state=self.config.random_state)

    def get_sampling_info(self) -> Dict:
        """Return metadata about sampling performed."""
        return {
            "was_sampled": self.was_sampled,
            "original_rows": self.original_shape[0] if self.original_shape else None,
            "original_cols": self.original_shape[1] if self.original_shape else None,
            "sample_fraction": self.sample_fraction,
            "sample_method": self.config.sample_method,
            "max_rows": self.config.max_rows,
        }
