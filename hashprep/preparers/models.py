from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class FixType(Enum):
    """Types of fix actions that can be applied to data."""

    DROP_COLUMN = "drop_column"
    DROP_DUPLICATES = "drop_duplicates"
    IMPUTE = "impute"
    ENCODE = "encode"
    SCALE = "scale"
    TRANSFORM = "transform"
    CLIP_OUTLIERS = "clip_outliers"
    CAST_TYPE = "cast_type"


class ImputeMethod(Enum):
    """Imputation strategies for missing values."""

    MEAN = "mean"
    MEDIAN = "median"
    MODE = "most_frequent"
    CONSTANT = "constant"
    KNN = "knn"


class EncodeMethod(Enum):
    """Encoding strategies for categorical variables."""

    ONEHOT = "onehot"
    LABEL = "label"
    ORDINAL = "ordinal"
    FREQUENCY = "frequency"


class ScaleMethod(Enum):
    """Scaling strategies for numeric variables."""

    STANDARD = "standard"
    MINMAX = "minmax"
    ROBUST = "robust"
    MAXABS = "maxabs"


class TransformMethod(Enum):
    """Transformation strategies for skewed distributions."""

    LOG = "log"
    LOG1P = "log1p"
    SQRT = "sqrt"
    BOXCOX = "boxcox"
    YEOJOHNSON = "yeojohnson"


@dataclass
class FixSuggestion:
    """Structured representation of a data fix action."""

    fix_type: FixType
    columns: List[str]
    method: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    reason: str = ""
    source_issue_category: str = ""

    def __post_init__(self):
        if not self.columns:
            raise ValueError("FixSuggestion must have at least one column")
        if not isinstance(self.columns, list):
            self.columns = [self.columns]
