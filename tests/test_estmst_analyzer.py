import unittest
import pandas as pd
import os
from src.epftools.estmst_analyzer import EstmstAnalyzer

class TestEstmstAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = EstmstAnalyzer()
        self.test_dir = "test_estmst_data"
        os.makedirs(self.test_dir, exist_ok=True)

        # Create dummy CSV files for testing
        self.create_dummy_estmst_csv(os.path.join(self.test_dir, "2016.csv"), {
            "EST ID": ["EST1", "EST2"],
            "Jan-2016_AMOUNT": [100, 200],
            "Jan-2016_ECR": [10, 20],
            "Jan-2016_MEMBER": [1, 2],
            "Feb-2016_AMOUNT": [110, 210],
            "Feb-2016_ECR": [11, 21],
            "Feb-2016_MEMBER": [3, 4],
        })
        self.create_dummy_estmst_csv(os.path.join(self.test_dir, "2017.csv"), {
            "EST ID": ["EST1", "EST2"],
            "Jan-2017_AMOUNT": [120, 220],
            "Jan-2017_ECR": [12, 22],
            "Jan-2017_MEMBER": [5, 6],
        })

    def tearDown(self):
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def create_dummy_estmst_csv(self, filepath, data):
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)

    def test_parse_estmst_file(self):
        filepath = os.path.join(self.test_dir, "2016.csv")
        df = self.analyzer.parse_estmst_file(filepath)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)
        self.assertIn('date', df.columns)
        self.assertIn('type', df.columns)

    def test_analyze_multiple_estmst_files(self):
        filenames = {
            "2016": os.path.join(self.test_dir, "2016.csv"),
            "2017": os.path.join(self.test_dir, "2017.csv")
        }
        df_analyzed = self.analyzer.analyze_multiple_estmst_files(filenames)
        self.assertIsInstance(df_analyzed, pd.DataFrame)
        self.assertFalse(df_analyzed.empty)
        self.assertIn('date', df_analyzed.columns)
        self.assertIn('EST ID', df_analyzed.columns)
        self.assertIn('MEMBER', df_analyzed.columns)
        self.assertEqual(len(df_analyzed), 6) # 2 EST IDs * 3 months across files

    def test_change_col(self):
        self.assertEqual(self.analyzer._change_col("Jan-2023"), "2023-01")
        self.assertEqual(self.analyzer._change_col("Dec-2022"), "2022-12")

if __name__ == '__main__':
    unittest.main()
