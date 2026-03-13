from abc import ABC, abstractmethod


class ReportGenerator(ABC):
    @abstractmethod
    def generate(self, summary, full=False, output_file=None):
        pass


def _load_generators():
    """
    Lazily load report generators.

    PDF generation relies on WeasyPrint and system libraries that may not be
    available in all environments. We treat the PDF generator as optional and
    only enable it when its dependencies import cleanly.
    """
    from .html import HtmlReport
    from .json import JsonReport
    from .markdown import MarkdownReport

    generators = {
        "md": MarkdownReport(),
        "json": JsonReport(),
        "html": HtmlReport(),
    }

    try:
        from .pdf import PdfReport  # type: ignore
    except Exception:
        # PDF generation is unavailable (missing WeasyPrint or system deps)
        generators["pdf"] = None
    else:
        generators["pdf"] = PdfReport()

    return generators


# get generators dictionary
def get_generators():
    if not hasattr(get_generators, "cache"):
        get_generators.cache = _load_generators()
    return get_generators.cache


def generate_report(summary, format="md", full=False, output_file=None, theme="minimal"):
    generators = get_generators()
    if format not in generators:
        raise ValueError(f"Unsupported format: {format}")

    if format == "pdf":
        pdf_generator = generators.get("pdf")
        if pdf_generator is None:
            raise RuntimeError(
                "PDF report generation is unavailable. "
                "Install WeasyPrint and its system dependencies to enable PDF output."
            )
        return pdf_generator.generate(summary, full, output_file, theme=theme)

    if format == "html":
        return generators["html"].generate(summary, full, output_file, theme=theme)

    return generators[format].generate(summary, full, output_file)
