"""Tests for dataset sampling module."""

import numpy as np
import pandas as pd
import pytest

from hashprep.utils.sampling import DatasetSampler, SamplingConfig


class TestSampler:
    def test_no_sampling_small_dataset(self):
        df = pd.DataFrame({"col": range(100)})
        config = SamplingConfig(max_rows=1000)
        sampler = DatasetSampler(config)

        result = sampler.sample(df)

        assert len(result) == 100
        assert not sampler.was_sampled
        assert sampler.sample_fraction == 1.0

    def test_sampling_large_dataset(self):
        df = pd.DataFrame({"col": range(10000)})
        config = SamplingConfig(max_rows=1000)
        sampler = DatasetSampler(config)

        result = sampler.sample(df)

        assert len(result) == 1000
        assert sampler.was_sampled
        assert sampler.sample_fraction == 0.1

    def test_random_sampling(self):
        df = pd.DataFrame({"col": range(10000)})
        config = SamplingConfig(max_rows=100, sample_method="random", random_state=42)
        sampler = DatasetSampler(config)

        result = sampler.sample(df)

        assert len(result) == 100
        assert sampler.was_sampled

    def test_systematic_sampling(self):
        df = pd.DataFrame({"col": range(1000)})
        config = SamplingConfig(max_rows=100, sample_method="systematic")
        sampler = DatasetSampler(config)

        result = sampler.sample(df)

        assert len(result) == 100
        assert result["col"].iloc[0] == 0
        assert result["col"].iloc[1] == 10

    def test_head_sampling(self):
        df = pd.DataFrame({"col": range(1000)})
        config = SamplingConfig(max_rows=100, sample_method="head")
        sampler = DatasetSampler(config)

        result = sampler.sample(df)

        assert len(result) == 100
        assert list(result["col"]) == list(range(100))

    def test_stratified_sampling_preserves_proportions(self):
        df = pd.DataFrame(
            {"feature": range(1000), "label": ["A"] * 900 + ["B"] * 100}
        )
        config = SamplingConfig(
            max_rows=100, sample_method="stratified", stratify_column="label"
        )
        sampler = DatasetSampler(config)

        result = sampler.sample(df)

        original_prop = df["label"].value_counts(normalize=True)["A"]
        sampled_prop = result["label"].value_counts(normalize=True)["A"]
        assert abs(original_prop - sampled_prop) < 0.15

    def test_sampling_info_metadata(self):
        df = pd.DataFrame({"col": range(10000)})
        config = SamplingConfig(max_rows=1000)
        sampler = DatasetSampler(config)

        sampler.sample(df)
        info = sampler.get_sampling_info()

        assert info["was_sampled"] is True
        assert info["original_rows"] == 10000
        assert info["sample_fraction"] == 0.1
        assert info["sample_method"] == "random"
        assert info["max_rows"] == 1000

    def test_disabled_sampling(self):
        df = pd.DataFrame({"col": range(10000)})
        config = SamplingConfig(max_rows=100, enabled=False)
        sampler = DatasetSampler(config)

        result = sampler.sample(df)

        assert len(result) == 10000
        assert not sampler.was_sampled

    def test_should_sample_by_row_count(self):
        df = pd.DataFrame({"col": range(10000)})
        config = SamplingConfig(max_rows=1000)
        sampler = DatasetSampler(config)

        assert sampler.should_sample(df) is True

    def test_should_not_sample_small_dataset(self):
        df = pd.DataFrame({"col": range(100)})
        config = SamplingConfig(max_rows=1000)
        sampler = DatasetSampler(config)

        assert sampler.should_sample(df) == False
