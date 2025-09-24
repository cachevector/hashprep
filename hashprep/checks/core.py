from dataclasses import dataclass

@dataclass
class Issues:
    category: str
    severity: str  # critical or warning
    column: str
    description: str
    impact_score: str  # high, medium, low
    quick_fix: str