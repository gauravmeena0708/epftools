import unittest
import pandas as pd
import os
from unittest.mock import patch, MagicMock
from src.epftools.daily_reporter import DailyReporter

class TestDailyReporter(unittest.TestCase):

    def setUp(self):
        self.download_dir = "test_downloads"
        self.temp_dir = os.path.join(self.download_dir, "TEMP")
        os.makedirs(self.temp_dir, exist_ok=True)

        # Create dummy data files
        self.create_dummy_csv(os.path.join(self.download_dir, "Claim.csv"), {
            'CLAIM ID': [1, 2, 3],
            'TASK ID': [10101, 10102, 10201],
            'PENDING DAYS': [5, 15, 25],
            'STATUS': ['Pending at DA Accounts', 'Pending at SS/AO/AC Accounts', 'Pending at DA Pension [Worksheet Generation]'],
            'GROUP ID': [101, 101, 102]
        })
        self.create_dummy_excel(os.path.join(self.download_dir, "dsc.xlsx"), {
            'EST ID': ['E1', 'E2'],
            'ACC TASK ID': [10101, 10201],
            'PENDING AT (DESIG)': ['RPFC', 'APFC'],
            'GROUP ID': [101, 102]
        })
        self.create_dummy_excel(os.path.join(self.download_dir, "esign.xlsx"), {
            'EST ID': ['E3', 'E4'],
            'ACC TASK ID': [10301, 10401],
            'PENDING AT (DESIG)': ['RPFC', 'APFC'],
            'GROUP ID': [103, 104]
        })
        self.create_dummy_csv(os.path.join(self.download_dir, "tin.csv"), {
            'TRAN CLAIM ID': [101, 102],
            'ACC TASK ID': [10101, 10102],
            'PENDING DAYS': [10, 20],
            'STATUS': ['Pending at DA Accounts', 'Pending at SS/AO/AC Accounts'],
            'GROUP ID': [101, 101]
        })
        self.create_dummy_excel(os.path.join(self.download_dir, "online.xlsx"), {
            'MEMBER ID': ['M1', 'M2'],
            'PENDING DAYS': [5, 10],
            'A/C GROUP': [101, 102],
            'DESIGNATION': ['RPFC', 'APFC'],
            'GROUP ID': [101, 102]
        })
        self.create_dummy_excel(os.path.join(self.download_dir, "primary.xlsx"), {
            'MEMBER ID': ['M3', 'M4'],
            'PENDING DAYS': [7, 12],
            'A/C GROUP': [103, 104],
            'DESIGNATION': ['RPFC', 'APFC'],
            'GROUP ID': [103, 104]
        })
        self.create_dummy_excel(os.path.join(self.download_dir, "others.xlsx"), {
            'MEMBER ID': ['M5', 'M6'],
            'PENDING DAYS': [8, 18],
            'A/C GROUP': [105, 106],
            'DESIGNATION': ['RPFC', 'APFC'],
            'GROUP ID': [105, 106]
        })

        # Create a dummy template.html
        os.makedirs(os.path.join(self.download_dir, "templates"), exist_ok=True)
        with open(os.path.join(self.download_dir, "templates/template.html"), "w") as f:
            f.write("<html><body>%s</body></html>")

        self.reporter = DailyReporter(download_dir=self.download_dir, template_path=os.path.join(self.download_dir, "templates/template.html"))

    def tearDown(self):
        import shutil
        if os.path.exists(self.download_dir):
            shutil.rmtree(self.download_dir)

    def create_dummy_csv(self, filepath, data):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)

    def create_dummy_excel(self, filepath, data):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        df = pd.DataFrame(data)
        df.to_excel(filepath, index=False)

    @patch('pdfkit.from_string')
    def test_generate_daily_report(self, mock_from_string):
        self.reporter.generate_daily_report()

        # Check if dataframes are loaded
        self.assertIsNotNone(self.reporter.df_claim)
        self.assertIsNotNone(self.reporter.df_dsc)
        self.assertIsNotNone(self.reporter.df_esign)
        self.assertIsNotNone(self.reporter.df_online)
        self.assertIsNotNone(self.reporter.df_primary)
        self.assertIsNotNone(self.reporter.df_others)
        self.assertIsNotNone(self.reporter.df_tin)

        # Check if pivot tables are created
        self.assertTrue(hasattr(self.reporter, 'df_claim_pivot1'))
        self.assertTrue(hasattr(self.reporter, 'df_dsc_pivot'))
        # Add assertions for other pivot tables

        # Check if pdfkit.from_string was called (meaning PDF was attempted to be generated)
        mock_from_string.assert_called_once()

if __name__ == '__main__':
    unittest.main()
