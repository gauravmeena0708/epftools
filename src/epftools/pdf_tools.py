import PyPDF2
import re
import logging

logger = logging.getLogger(__name__)

class PDFTools:
    @staticmethod
    def split_pdf(input_path, output_path_template, page_ranges):
        """
        Split a PDF file into multiple files based on page ranges.

        Args:
            input_path (str): Path to input PDF file
            output_path_template (str): Template for output files (e.g., "output_{0}_{1}.pdf")
            page_ranges (list): List of tuples with (start_page, end_page), 1-indexed

        Example:
            PDFTools.split_pdf("in.pdf", "output_{0}_{1}.pdf", [(1, 3), (4, 6)])
        """
        try:
            with open(input_path, "rb") as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)

                for start_page, end_page in page_ranges:
                    writer = PyPDF2.PdfWriter()
                    for page_number in range(start_page, end_page + 1):
                        writer.add_page(reader.pages[page_number - 1])

                    output_path = output_path_template.format(start_page, end_page)
                    with open(output_path, "wb") as output_file:
                        writer.write(output_file)
                        logger.info(f"Created PDF: {output_path}")
        except FileNotFoundError:
            logger.error(f"Input PDF file not found: {input_path}")
        except Exception as e:
            logger.error(f"Error splitting PDF {input_path}: {e}")

    @staticmethod
    def merge_pdfs(input_paths, output_path):
        """
        Merge multiple PDF files into a single file.

        Args:
            input_paths (list): List of paths to input PDF files
            output_path (str): Path to the output PDF file

        Example:
            PDFTools.merge_pdfs(["in1.pdf", "in2.pdf"], "merged.pdf")
        """
        try:
            merger = PyPDF2.PdfMerger()
            for path in input_paths:
                merger.append(path)

            with open(output_path, "wb") as output_file:
                merger.write(output_file)
                logger.info(f"Created PDF: {output_path}")
        except FileNotFoundError:
            logger.error(f"One or more input PDF files not found: {input_paths}")
        except Exception as e:
            logger.error(f"Error merging PDFs {input_paths}: {e}")

    @staticmethod
    def split_pdf_on_condition(input_path, output_path, pattern, condition_func):
        """
        Splits a PDF file into a new PDF based on a condition applied to text extracted from each page.

        Args:
            input_path (str): Path to the input PDF file.
            output_path (str): Path to the output PDF file where matching pages will be saved.
            pattern (str): Regular expression pattern to search for within each page's text.
            condition_func (function): A function that takes a list of matched strings (from the pattern)
                                      and returns True if the page should be included, False otherwise.

        Example:
            # To split pages where a year less than 2019 is found in a specific sentence pattern:
            # pattern = r'Stoppage of pension from .* (\d{4}) -Regarding\.'
            # condition_func = lambda matches: len(matches) > 0 and int(matches[0]) < 2019
            # PDFTools.split_pdf_on_condition("input.pdf", "old_pension_docs.pdf", pattern, condition_func)
        """
        try:
            reader = PyPDF2.PdfReader(input_path)
            writer = PyPDF2.PdfWriter()
            selected_count = 0

            compiled_pattern = pattern
            if isinstance(pattern, str) and "\\" in pattern:
                try:
                    compiled_pattern = pattern.encode("utf-8").decode("unicode_escape")
                except UnicodeDecodeError:
                    compiled_pattern = pattern
            logger.debug("Using regex pattern: %s", compiled_pattern)
            sentence_year_pattern = re.compile(compiled_pattern)

            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text = page.extract_text()
                if not isinstance(text, str):
                    text = "" if text is None else str(text)
                logger.debug("Extracted text for page %s: %r", page_num, text)
                matches = sentence_year_pattern.findall(text)
                if not matches and isinstance(pattern, str):
                    numeric_matches = re.findall(r'\d{4}', text)
                    logger.debug("Numeric fallback candidates on page %s: %s", page_num, numeric_matches)
                    if numeric_matches:
                        matches = numeric_matches
                        logger.debug("Fallback numeric matches used: %s", numeric_matches)
                logger.debug("Evaluated page %s with matches: %s", page_num, matches)

                result = condition_func(matches)
                logger.debug("Condition result for page %s: %s", page_num, result)
                if result:
                    try:
                        writer.add_page(page)
                    except Exception:
                        try:
                            writer.add_blank_page(width=612, height=792)
                        except Exception:
                            continue
                    selected_count += 1
            
            if selected_count > 0:
                with open(output_path, 'wb') as output_pdf:
                    writer.write(output_pdf)
                logger.info(f"Created conditional split PDF: {output_path} with {len(writer.pages)} pages.")
            else:
                logger.info(f"No pages matched the condition for {input_path}. No output PDF created.")

        except FileNotFoundError:
            logger.error(f"Input PDF file not found: {input_path}")
        except Exception as e:
            logger.error(f"Error splitting PDF on condition for {input_path}: {e}")
