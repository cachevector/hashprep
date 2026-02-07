from weasyprint import HTML

from .html import HtmlReport


class PdfReport:
    def generate(self, summary, full=False, output_file=None, theme="minimal"):
        html_generator = HtmlReport()
        html_content = html_generator.generate(summary, full, theme=theme, pdf_mode=True)
        pdf_content = HTML(string=html_content).write_pdf()
        if output_file:
            with open(output_file, "wb") as f:
                f.write(pdf_content)
        return pdf_content