from os import listdir, mkdir
from os.path import isfile, join, exists
import os
import logging
from PyPDF2 import PdfWriter
import pytesseract
from pdf2image import convert_from_path
import PyPDF2
import io

logger = logging.getLogger(__name__)

class PDFOCR:
    """Perform OCR on PDF files and create searchable PDFs."""

    @staticmethod
    def convert_images_to_pdf(input_path, output_path, poppler_path):
        """
        Convert scanned PDFs to searchable PDFs using OCR.

        Args:
            input_path (str): Directory containing input PDF files
            output_path (str): Directory for output searchable PDFs
            poppler_path (str): Path to poppler binaries

        Raises:
            FileNotFoundError: If input_path or poppler_path not found
            RuntimeError: If OCR conversion fails
        """
        if not exists(input_path):
            raise FileNotFoundError(f"Input path not found: {input_path}")

        if not exists(poppler_path):
            raise FileNotFoundError(f"Poppler path not found: {poppler_path}")

        # Create output directory if it doesn't exist
        if not exists(output_path):
            try:
                os.makedirs(output_path)
                logger.info(f"Created output directory: {output_path}")
            except Exception as e:
                raise RuntimeError(f"Failed to create output directory: {str(e)}")

        try:
            pdffiles = [f for f in listdir(input_path)
                       if isfile(join(input_path, f)) and f.lower().endswith('.pdf')]

            if not pdffiles:
                logger.warning(f"No PDF files found in {input_path}")
                return

            print(f'\nFound {len(pdffiles)} PDF file(s):\n')
            success_count = 0
            failed_files = []

            for i, file in enumerate(pdffiles, 1):
                print(f"[{i}/{len(pdffiles)}] Processing: {file}")

                try:
                    input_file_path = join(input_path, file)
                    images = convert_from_path(input_file_path, poppler_path=poppler_path)

                    pdf_writer = PdfWriter()

                    for page_num, image in enumerate(images, 1):
                        try:
                            page = pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
                            pdf = PyPDF2.PdfReader(io.BytesIO(page))
                            pdf_writer.add_page(pdf.pages[0])
                        except Exception as e:
                            logger.warning(f"Failed to OCR page {page_num} of {file}: {str(e)}")

                    output_file_path = join(output_path, file)
                    with open(output_file_path, "wb") as f:
                        pdf_writer.write(f)

                    print(f"✓ Converted and saved: {output_file_path}")
                    success_count += 1

                except Exception as e:
                    logger.error(f"Failed to process {file}: {str(e)}")
                    failed_files.append(file)
                    print(f"✗ Failed: {file} - {str(e)}")

            print(f"\n{'='*50}")
            print(f"Processing complete: {success_count}/{len(pdffiles)} successful")

            if failed_files:
                print(f"Failed files: {', '.join(failed_files)}")

        except Exception as e:
            logger.error(f"OCR conversion failed: {str(e)}")
            raise RuntimeError(f"OCR conversion failed: {str(e)}")

"""
poppler_path = r"<poppler path>"
pytesseract.pytesseract.tesseract_cmd = r"<tessaract path>"
input_path = "<input dir>"
output_path = "<output dir>"
PDFOCR.convert_images_to_pdf(input_path, output_path, poppler_path)
"""