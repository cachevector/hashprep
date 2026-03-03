"""Load HashPrepConfig from YAML, TOML, or JSON files."""

from __future__ import annotations

import json
from pathlib import Path

from ..config import HashPrepConfig, config_from_dict


def load_config(path: str | Path) -> HashPrepConfig:
    """Load a HashPrepConfig from a YAML (.yaml/.yml), TOML (.toml), or JSON (.json) file.

    Only keys present in the file are overridden; all others fall back to defaults.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    suffix = path.suffix.lower()

    if suffix in (".yaml", ".yml"):
        try:
            import yaml
        except ImportError as e:
            raise ImportError("pyyaml is required for YAML config files: pip install pyyaml") from e
        with open(path) as f:
            raw = yaml.safe_load(f) or {}
    elif suffix == ".toml":
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib  # type: ignore[no-redef]
            except ImportError as e:
                raise ImportError(
                    "tomllib (Python 3.11+) or tomli is required for TOML config files: pip install tomli"
                ) from e
        with open(path, "rb") as f:
            raw = tomllib.load(f)
    elif suffix == ".json":
        with open(path) as f:
            raw = json.load(f)
    else:
        raise ValueError(f"Unsupported config file format: {suffix!r}. Use .yaml, .yml, .toml, or .json")

    if not isinstance(raw, dict):
        raise ValueError(f"Config file must contain a mapping at the top level, got {type(raw).__name__}")

    return config_from_dict(raw)
