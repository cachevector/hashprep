from typing import Dict, List, Set

from .models import FixSuggestion, FixType
from .strategies import (
    ColumnDropStrategy,
    DuplicateRemovalStrategy,
    EncodingStrategy,
    FixStrategy,
    ImputationStrategy,
    OutlierStrategy,
    ScalingStrategy,
    TransformationStrategy,
)


class CodeGenerator:
    """Generates executable Python code from fix suggestions."""

    STRATEGY_MAP: Dict[FixType, FixStrategy] = {
        FixType.DROP_COLUMN: ColumnDropStrategy(),
        FixType.DROP_DUPLICATES: DuplicateRemovalStrategy(),
        FixType.IMPUTE: ImputationStrategy(),
        FixType.ENCODE: EncodingStrategy(),
        FixType.SCALE: ScalingStrategy(),
        FixType.TRANSFORM: TransformationStrategy(),
        FixType.CLIP_OUTLIERS: OutlierStrategy(),
    }

    def __init__(self, suggestions: List[FixSuggestion]):
        self.suggestions = suggestions

    def generate_pandas_script(self) -> str:
        """Generate a complete, runnable pandas script."""
        imports = self._collect_imports()
        code_blocks: List[str] = []

        code_blocks.append('"""')
        code_blocks.append("Auto-generated data cleaning script by HashPrep.")
        code_blocks.append("Review and adapt before production use.")
        code_blocks.append('"""')
        code_blocks.append("")
        code_blocks.extend(imports)
        code_blocks.append("")
        code_blocks.append("")
        code_blocks.append("def apply_fixes(df):")
        code_blocks.append('    """Apply data quality fixes to DataFrame."""')
        code_blocks.append("    df = df.copy()")
        code_blocks.append("")

        for suggestion in self.suggestions:
            code = self._generate_code_for_suggestion(suggestion)
            if code:
                code_blocks.append(f"    # {suggestion.reason}")
                indented = self._indent(code, 4)
                code_blocks.append(indented)
                code_blocks.append("")

        code_blocks.append("    return df")
        code_blocks.append("")
        code_blocks.append("")
        code_blocks.append("if __name__ == '__main__':")
        code_blocks.append("    import sys")
        code_blocks.append("")
        code_blocks.append("    if len(sys.argv) < 2:")
        code_blocks.append("        print('Usage: python fixes.py <input.csv> [output.csv]')")
        code_blocks.append("        sys.exit(1)")
        code_blocks.append("")
        code_blocks.append("    input_file = sys.argv[1]")
        code_blocks.append("    output_file = sys.argv[2] if len(sys.argv) > 2 else 'cleaned_data.csv'")
        code_blocks.append("")
        code_blocks.append("    df = pd.read_csv(input_file)")
        code_blocks.append("    df_clean = apply_fixes(df)")
        code_blocks.append("    df_clean.to_csv(output_file, index=False)")
        code_blocks.append("    print(f'Cleaned data saved to {output_file}')")

        return "\n".join(code_blocks)

    def _generate_code_for_suggestion(self, suggestion: FixSuggestion) -> str:
        """Generate code for a single suggestion."""
        strategy = self.STRATEGY_MAP.get(suggestion.fix_type)
        if strategy:
            return strategy.generate_pandas_code(suggestion)
        return ""

    def _collect_imports(self) -> List[str]:
        """Collect all required imports."""
        imports: Set[str] = {"import pandas as pd", "import numpy as np"}

        for suggestion in self.suggestions:
            strategy = self.STRATEGY_MAP.get(suggestion.fix_type)
            if strategy:
                imports.update(strategy.get_sklearn_imports())

        return sorted(imports)

    def _indent(self, code: str, spaces: int) -> str:
        """Indent code by specified number of spaces."""
        prefix = " " * spaces
        return "\n".join(prefix + line for line in code.split("\n"))

    def generate_sklearn_pipeline(self) -> str:
        """
        Generate sklearn pipeline code.
        Note: For full pipeline support, use PipelineBuilder.
        """
        from .pipeline_builder import PipelineBuilder

        builder = PipelineBuilder(self.suggestions)
        return builder.generate_pipeline_code()
