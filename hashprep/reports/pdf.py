from .html import HtmlReport
from weasyprint import HTML

class PdfReport:
    def generate(self, summary, full=False, output_file=None):
        html_generator = HtmlReport()
        html_content = html_generator.generate(summary, full)
        pdf_content = HTML(string=html_content).write_pdf()
        if output_file:
            with open(output_file, "wb") as f:
                f.write(pdf_content)
        return pdf_content  # or save and return path