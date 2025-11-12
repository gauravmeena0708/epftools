import re
import logging
import numpy as np
import pandas as pd
from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)


class PendencyProcessor:
    """
    Process EPFO pendency PDF reports and extract structured data.

    This class parses pendency reports generated from EPFO system,
    extracts claim information, and provides analytics capabilities.
    """

    # Officer mapping based on GROUP_ID
    OFFICER_MAPPING = {
        'OFFICER_A': [110, 111, 112, 113, 199],
        'OFFICER_B': [106, 107, 109, 114],
        'OFFICER_C': [104, 105, 108, 115, 188],
        'OFFICER_D': [101, 102, 103]
    }

    def __init__(self, bins=None, labels=None):
        """
        Initialize PendencyProcessor.

        Args:
            bins (list): Custom bins for pending days categorization
                        Default: [0, 11, 16, 20, 2000]
            labels (list): Labels for bins
                          Default: ['0-10 Days', '11-15 Days', '16-19 Days', '>=20 Days']
        """
        self.bins = bins or [0, 11, 16, 20, 2000]
        self.labels = labels or ['0-10 Days', '11-15 Days', '16-19 Days', '>=20 Days']

    @staticmethod
    def extract_page_header(page_text):
        """
        Extract GROUP_ID, TASK_ID, and NAME from page header.

        Args:
            page_text (list): Cleaned page text lines

        Returns:
            tuple: (group_id, task_id, name) or (None, None, None) if extraction fails
        """
        try:
            group = page_text[20].split(": ")[1]
            taskid = page_text[21].split(":")[1].strip()
            name = page_text[22].split(": ")[1].strip()
            if name.endswith(','):
                name = name[:-1]
            return group, taskid, name
        except (IndexError, AttributeError):
            return None, None, None

    @staticmethod
    def extract_claims_from_page(group, taskid, name, page_text):
        """
        Extract claim records from a single page.

        Args:
            group (str): GROUP_ID
            taskid (str): TASK_ID
            name (str): Officer name
            page_text (list): Cleaned page text lines

        Returns:
            list: List of claim records [group, task, name, sr, claim_id, date, member_id, member_name, form, pending_days]
        """
        rows = []

        for idx, text in enumerate(page_text):
            # Look for CLAIM_ID pattern (12-digit number)
            if re.search(r'\d{12}', text):
                try:
                    claim_id = text
                    pending_days = page_text[idx - 1]
                    date = page_text[idx + 1]
                    member_id = page_text[idx + 2]

                    # Form type can be at different offsets
                    member_name = ' '
                    form_type = None
                    sr_no = None

                    for offset in range(3, 6):
                        if page_text[idx + offset].startswith("Form-"):
                            if offset == 3:
                                member_name = ' '
                            else:
                                member_name = page_text[idx + 3]

                            form_type = page_text[idx + offset]
                            sr_no = page_text[idx + offset + 1]
                            break

                    if form_type and sr_no:
                        row = [group, taskid, name, sr_no, claim_id, date,
                               member_id, member_name, form_type, pending_days]
                        rows.append(row)

                except (IndexError, AttributeError) as e:
                    logger.debug(f"Skipped malformed claim entry at index {idx}: {str(e)}")

        return rows

    def parse_pdf(self, pdf_path):
        """
        Parse pendency PDF and extract all claims.

        Args:
            pdf_path (str): Path to pendency PDF file

        Returns:
            pd.DataFrame: DataFrame with columns:
                         ['group', 'task', 'name', 'sr', 'id', 'date',
                          'memid', 'memname', 'form', 'days']

        Raises:
            FileNotFoundError: If PDF file not found
            RuntimeError: If PDF parsing fails
        """
        try:
            with open(pdf_path, 'rb') as pdf_file:
                reader = PdfReader(pdf_file)
                total_pages = len(reader.pages)

                all_rows = []

                for page_num in range(total_pages):
                    try:
                        page = reader.pages[page_num]
                        text = page.extract_text()
                        cleaned_lines = [line.strip() for line in text.split('\n') if line.strip()]

                        group, taskid, name = self.extract_page_header(cleaned_lines)

                        if group and taskid and name:
                            claims = self.extract_claims_from_page(group, taskid, name, cleaned_lines)
                            all_rows.extend(claims)

                    except Exception as e:
                        logger.warning(f"Failed to parse page {page_num + 1}: {str(e)}")

                if not all_rows:
                    raise RuntimeError(f"No claims found in PDF: {pdf_path}")

                df = pd.DataFrame(all_rows,
                                 columns=['group', 'task', 'name', 'sr', 'id', 'date',
                                         'memid', 'memname', 'form', 'days'])

                logger.info(f"Extracted {len(df)} claims from {pdf_path}")
                return df

        except FileNotFoundError:
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        except Exception as e:
            logger.error(f"Failed to parse PDF: {str(e)}")
            raise RuntimeError(f"PDF parsing failed: {str(e)}")

    def add_categories(self, df):
        """
        Add day categories and officer mapping to dataframe.

        Args:
            df (pd.DataFrame): Input dataframe with 'days' and 'group' columns

        Returns:
            pd.DataFrame: DataFrame with added 'days_cat' and 'officer' columns
        """
        df = df.copy()

        # Convert to numeric
        df['days'] = pd.to_numeric(df['days'], errors='coerce')
        df['group'] = pd.to_numeric(df['group'], errors='coerce')

        # Add day categories
        df['days_cat'] = pd.cut(df['days'], bins=self.bins,
                               labels=self.labels, right=False)

        # Add officer mapping
        df['officer'] = None
        for officer, groups in self.OFFICER_MAPPING.items():
            df.loc[df['group'].isin(groups), 'officer'] = officer

        return df

    @staticmethod
    def create_pivot_summary(df, index_col, column_col, pending_at=None):
        """
        Create pivot table summary.

        Args:
            df (pd.DataFrame): Input dataframe
            index_col (str): Column to use as index
            column_col (str): Column to use for columns
            pending_at (str): Optional filter for 'pending_at' column

        Returns:
            pd.DataFrame: Pivot table with counts
        """
        if pending_at:
            df = df[df['pending_at'] == pending_at]

        pivot = pd.pivot_table(df, values='id', index=index_col,
                              columns=column_col, aggfunc='count',
                              fill_value=0, margins=True)

        return pivot.astype(int)

    def process_files(self, files_to_process):
        """
        Process multiple pendency PDF files.

        Args:
            files_to_process (list): A list of tuples, where each tuple contains the file path and its type (e.g., 'DA', 'SS/Approver').

        Returns:
            pd.DataFrame: Combined dataframe with 'pending_at' column

        Raises:
            FileNotFoundError: If any of the PDF files are not found
        """
        all_dfs = []
        for pdf_path, pending_at_type in files_to_process:
            logger.info(f"Processing {pending_at_type} pendency PDF: {pdf_path}")
            df = self.parse_pdf(pdf_path)
            df = self.add_categories(df)
            df['pending_at'] = pending_at_type
            all_dfs.append(df)

        if not all_dfs:
            return pd.DataFrame()

        merged = pd.concat(all_dfs, ignore_index=True)
        logger.info(f"Total claims processed: {len(merged)}")
        return merged


# Example usage
"""
from epftools import PendencyProcessor

# Initialize processor
processor = PendencyProcessor()

# Process single PDF
df = processor.parse_pdf("Pendency DA.PDF")
df = processor.add_categories(df)

# Or process both PDFs
merged_df = processor.process_pendency_files("Pendency DA.PDF", "Pendency SS.PDF")

# Create summary
summary = processor.create_pivot_summary(merged_df, 'days_cat', 'group')
print(summary)

# Save to Excel
merged_df.to_excel("pendency_summary.xlsx", index=False)
"""
