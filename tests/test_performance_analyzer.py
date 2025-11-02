import unittest
import os
from unittest.mock import patch, MagicMock

import numpy as np
import pandas as pd

from src.epftools.performance_analyzer import PerformanceAnalyzer

class TestPerformanceAnalyzer(unittest.TestCase):

    def setUp(self):
        self.test_dir = "test_performance_data"
        self.reports_dir = os.path.join(self.test_dir, "reports")
        os.makedirs(self.reports_dir, exist_ok=True)

        # Create dummy data for testing compare_claims and get_date_compared
        self.date1_dir = os.path.join(self.reports_dir, "2023_06_13")
        self.date2_dir = os.path.join(self.reports_dir, "2023_06_14")
        os.makedirs(self.date1_dir, exist_ok=True)
        os.makedirs(self.date2_dir, exist_ok=True)

        pd.DataFrame({
            'CLAIM ID': [1, 2, 3, 4],
            'TASK ID': [101, 102, 103, 104],
            'PENDING DAYS': [5, 10, 15, 20],
            'STATUS': ['Pending at DA Accounts', 'Pending at DA Accounts [EDIT]', 'Pending at SS/AO/AC Accounts [Rejection]', 'Pending [ Approver Pending ]'],
            'GROUP ID': [1, 2, 3, 4]
        }).to_csv(os.path.join(self.date1_dir, "claim.csv"), index=False)

        pd.DataFrame({
            'CLAIM ID': [1, 2, 5, 6],
            'TASK ID': [101, 102, 105, 106],
            'PENDING DAYS': [6, 11, 16, 21],
            'STATUS': ['Pending at DA Accounts', 'Pending at DA Accounts [EDIT]', 'Pending at SS/AO/AC Accounts', 'Pending [ Approver Pending ]'],
            'GROUP ID': [1, 2, 5, 6]
        }).to_csv(os.path.join(self.date2_dir, "claim.csv"), index=False)

        pd.DataFrame({
            'TRAN CLAIM ID': [10, 11, 12],
            'ACC TASK ID': [201, 202, 203],
            'PENDING DAYS': [7, 12, 17],
            'STATUS': ['Pending at DA Accounts', 'Pending at SS/AO/AC Accounts', 'Pending at DA Pension [Worksheet Generation]'],
            'GROUP ID': [10, 11, 12]
        }).to_csv(os.path.join(self.date1_dir, "tin.csv"), index=False)

        pd.DataFrame({
            'TRAN CLAIM ID': [10, 13, 14],
            'ACC TASK ID': [201, 204, 205],
            'PENDING DAYS': [8, 13, 18],
            'STATUS': ['Pending at DA Accounts', 'Pending at SS/AO/AC Accounts', 'Pending at DA Pension [Worksheet Generation]'],
            'GROUP ID': [10, 13, 14]
        }).to_csv(os.path.join(self.date2_dir, "tin.csv"), index=False)

        # Create dummy Excel files for summarize_performance_excel
        self.performance_da_excel = os.path.join(self.reports_dir, "Performance ReportDA.xlsx")
        self.performance_ao_excel = os.path.join(self.reports_dir, "Performance AO.xlsx")
        self.mapping_excel = os.path.join(self.reports_dir, "mapping.xlsx")

        # Create dummy Excel files with some data to avoid errors
        pd.DataFrame(np.random.rand(20, 40)).to_excel(self.performance_da_excel, index=False, header=False, engine='xlsxwriter')
        pd.DataFrame(np.random.rand(20, 40)).to_excel(self.performance_ao_excel, index=False, header=False, engine='xlsxwriter')
        pd.DataFrame({'userid': [1, 2], 'group': ['A', 'B']}).to_excel(self.mapping_excel, index=False, engine='xlsxwriter')

        # Create a dummy template.html
        self.template_dir = os.path.join(self.test_dir, "templates")
        os.makedirs(self.template_dir, exist_ok=True)
        with open(os.path.join(self.template_dir, "template.html"), "w") as f:
            f.write("<html><body>%s</body></html>")

        self.analyzer = PerformanceAnalyzer(directory_path=self.reports_dir, template_path=os.path.join(self.template_dir, "template.html"))

    def tearDown(self):
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch('pdfkit.from_string')
    def test_generate_performance_report(self, mock_from_string):
        self.analyzer.generate_performance_report()
        # Check if pdfkit.from_string was called multiple times for different reports
        self.assertGreater(mock_from_string.call_count, 0)

    def test_compare_claims(self):
        df_compared = self.analyzer.compare_claims("2023_06_14", "2023_06_13")
        self.assertIsInstance(df_compared, pd.DataFrame)
        self.assertFalse(df_compared.empty)
        self.assertIn('GROUP', df_compared.columns)
        self.assertIn('TASK', df_compared.columns)
        self.assertIn('2023_06_13', df_compared.columns)

    def test_get_date_compared(self):
        df_compared = self.analyzer.get_date_compared("2023_06_13", "2023_06_14", "claim.csv")
        self.assertIsInstance(df_compared, pd.DataFrame)
        self.assertFalse(df_compared.empty)
        self.assertIn('GROUP', df_compared.columns)
        self.assertIn('TASK', df_compared.columns)
        self.assertIn('claim_2023_06_13', df_compared.columns)

    def test_summarize_performance_excel(self):
        df_summary = self.analyzer.summarize_performance_excel(self.performance_da_excel, flag=1, mapping_file=self.mapping_excel)
        self.assertIsInstance(df_summary, pd.DataFrame)
        self.assertFalse(df_summary.empty)
        self.assertIn('userid', df_summary.columns)
        self.assertIn('total', df_summary.columns)

if __name__ == '__main__':
    unittest.main()
