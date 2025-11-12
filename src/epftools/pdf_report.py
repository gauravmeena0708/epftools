import pdfkit
import os
import logging
import tempfile
from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageBreak, Spacer

logger = logging.getLogger(__name__)

class PDFReport:
    """Generate PDF reports from pandas DataFrames or HTML content."""

    def __init__(self, engine='reportlab', wkhtmltopdf_path=None):
        """
        Initialize PDFReport.

        Args:
            engine (str): The PDF generation engine to use ('reportlab' or 'wkhtmltopdf').
            wkhtmltopdf_path (str, optional): Path to wkhtmltopdf executable. Required for 'wkhtmltopdf' engine.
        """
        if engine not in ['reportlab', 'wkhtmltopdf']:
            raise ValueError("Engine must be 'reportlab' or 'wkhtmltopdf'")

        if engine == 'wkhtmltopdf' and not wkhtmltopdf_path:
            raise ValueError("wkhtmltopdf_path is required for the 'wkhtmltopdf' engine")

        if engine == 'wkhtmltopdf' and not os.path.exists(wkhtmltopdf_path):
            raise FileNotFoundError(f"wkhtmltopdf not found at: {wkhtmltopdf_path}")

        self.engine = engine
        self.wkhtmltopdf_path = wkhtmltopdf_path

    def from_dataframes(self, dataframes, output_path, with_break=False):
        """
        Create a PDF from a list of pandas DataFrames using the reportlab engine.

        Args:
            dataframes (list): List of pandas DataFrames.
            output_path (str): The path for the output PDF file.
            with_break (bool): Add a page break between tables (default: False).
        """
        if self.engine != 'reportlab':
            raise RuntimeError("from_dataframes is only available with the 'reportlab' engine.")

        if not dataframes or not isinstance(dataframes, list):
            raise ValueError("dataframes must be a non-empty list")

        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=landscape(A4),
                title="Report",
                author="EPF Tools",
                subject="pdf via reportlab"
            )

            elements = []
            space = Spacer(width=0, height=7)

            for i, df in enumerate(dataframes):
                if not isinstance(df, pd.DataFrame):
                    logger.warning(f"Item {i} is not a DataFrame, skipping")
                    continue

                table = self._convert_df_to_table(df)
                elements.append(table)
                elements.append(space)

                if i < len(dataframes) - 1 and with_break:
                    elements.append(PageBreak())

            if not elements:
                raise ValueError("No valid tables could be created from dataframes")

            doc.build(elements)
            logger.info(f'PDF saved to {output_path}')
            print(f'PDF saved to {output_path}')

        except Exception as e:
            logger.error(f"Failed to create PDF: {str(e)}")
            raise

    def from_html(self, html_content, output_path):
        """
        Create a PDF from HTML content using the wkhtmltopdf engine.

        Args:
            html_content (str): The HTML content to convert.
            output_path (str): The path for the output PDF file.
        """
        if self.engine != 'wkhtmltopdf':
            raise RuntimeError("from_html is only available with the 'wkhtmltopdf' engine.")

        html_filename = None
        try:
            modified_html = self._modify_html(html_content)

            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(modified_html)
                html_filename = f.name

            config = pdfkit.configuration(wkhtmltopdf=self.wkhtmltopdf_path)
            options = {
                'page-size': 'A4',
                'margin-top': '0.2in',
                'margin-right': '0.2in',
                'margin-bottom': '0.2in',
                'margin-left': '0.2in'
            }
            pdfkit.from_file(html_filename, output_path, options=options, configuration=config)

            logger.info(f'PDF saved to {output_path}')
            print(f'PDF generated successfully: {output_path}')

        except Exception as e:
            logger.error(f"Failed to generate PDF: {str(e)}")
            raise RuntimeError(f"PDF generation failed: {str(e)}")

        finally:
            if html_filename and os.path.exists(html_filename):
                try:
                    os.remove(html_filename)
                except Exception as e:
                    logger.warning(f"Failed to remove temp file {html_filename}: {str(e)}")

    def _convert_df_to_table(self, df):
        data = [df.columns.tolist()] + df.values.tolist()
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BACKGROUND', (1, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ])
        table = Table(data, hAlign='LEFT')
        table.setStyle(table_style)
        return table

    def _modify_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        for table in soup.find_all('table'):
            table["class"] = 'table table-sm table-bordered border-primary d-print-table fs-6'
        for td in soup.find_all('td'):
            td["style"] = "font-size:10px;padding:2px;text-align:center;"
        for th in soup.find_all('th'):
            th["style"] = "font-size:10px;padding:2px;text-align:left;"
        return str(soup)
