import os
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class ExcelMerger:
    """Merge multiple Excel files from a folder into a single file."""

    def __init__(self, folder_path, ext=".xlsx", sheetnum=0):
        """
        Initialize ExcelMerger.

        Args:
            folder_path (str): Path to folder containing Excel files
            ext (str): File extension to match (default: '.xlsx')
            sheetnum (int): Sheet number to extract (default: 0)

        Raises:
            FileNotFoundError: If folder_path does not exist
            ValueError: If no Excel files found in folder
        """
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Folder not found: {folder_path}")

        self.folder_path = folder_path
        self.ext = ext
        self.sheet_num = sheetnum
        self.excel_names = self.get_excel_files()

        if not self.excel_names:
            raise ValueError(f"No {ext} files found in {folder_path}")

        self.excels = self.load_excels()
        self.frames = self.extract_frames()

    def get_excel_files(self):
        """Get list of Excel files in folder."""
        try:
            excel_names = [filename for filename in os.listdir(self.folder_path)
                          if filename.endswith(self.ext)]
            return excel_names
        except PermissionError as e:
            logger.error(f"Permission denied accessing folder: {self.folder_path}")
            raise

    def load_excels(self):
        """Load all Excel files into memory."""
        excels = []
        failed_files = []

        for name in self.excel_names:
            try:
                file_path = os.path.join(self.folder_path, name)
                excels.append(pd.ExcelFile(file_path))
            except Exception as e:
                logger.warning(f"Failed to load {name}: {str(e)}")
                failed_files.append(name)

        if failed_files:
            logger.info(f"Skipped {len(failed_files)} file(s): {', '.join(failed_files)}")

        if not excels:
            raise ValueError("No valid Excel files could be loaded")

        return excels

    def extract_frames(self):
        """Extract dataframes from loaded Excel files."""
        frames = []

        for excel_file in self.excels:
            try:
                if self.sheet_num >= len(excel_file.sheet_names):
                    logger.warning(f"Sheet {self.sheet_num} not found in {excel_file}, skipping")
                    continue

                df = excel_file.parse(excel_file.sheet_names[self.sheet_num],
                                     header=None, index_col=None)
                frames.append(df)
            except Exception as e:
                logger.warning(f"Failed to parse sheet: {str(e)}")

        if not frames:
            raise ValueError("No valid dataframes could be extracted")

        # Delete the first row for all frames except the first
        # i.e. remove the header row -- assumes it's the first
        if len(frames) > 1:
            frames[1:] = [df[1:] for df in frames[1:]]

        return frames

    def merge_and_save(self, output_filename="merged.xlsx"):
        """
        Merge all dataframes and save to Excel file.

        Args:
            output_filename (str): Output file path (default: 'merged.xlsx')

        Raises:
            PermissionError: If cannot write to output file
        """
        try:
            # Concatenate the frames
            combined = pd.concat(self.frames, ignore_index=True)
            # Write it out to Excel
            combined.to_excel(output_filename, header=False, index=False)
            logger.info(f"Merged {len(self.frames)} Excel files saved to {output_filename}")
            print(f"Merged Excel files saved to {output_filename}")
        except PermissionError:
            raise PermissionError(f"Cannot write to {output_filename}. File may be open.")
        except Exception as e:
            logger.error(f"Failed to save merged file: {str(e)}")
            raise

"""
# Example usage:
if __name__ == "__main__":
    folder_path = '<Dir path>'
    merger = ExcelMerger(folder_path)
    merger.merge_and_save()
"""