import unittest
import pandas as pd
from src.epftools.anomaly_detector import AnomalyDetector

class TestAnomalyDetector(unittest.TestCase):

    def setUp(self):
        self.detector = AnomalyDetector()
        self.df = pd.DataFrame({
            'CLAIM_ID': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'month': [1, 1, 2, 2, 3, 3, 1, 2, 3, 1],
            'gender': ['M', 'F', 'M', 'F', 'M', 'F', 'M', 'F', 'M', 'F'],
            'FORM_NAME': ['F1', 'F2', 'F1', 'F2', 'F1', 'F2', 'F1', 'F2', 'F1', 'F2'],
            'EST_ID': ['E1', 'E2', 'E1', 'E2', 'E1', 'E2', 'E1', 'E2', 'E1', 'E2'],
            'SECTION': ['S1', 'S2', 'S1', 'S2', 'S1', 'S2', 'S1', 'S2', 'S1', 'S2'],
            'GROUP_ID': [101, 102, 101, 102, 101, 102, 101, 102, 101, 102],
        })

    def test_monthwise_genderwise_claims(self):
        result = self.detector.monthwise_genderwise_claims(self.df)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('M', result.columns)
        self.assertIn('F', result.columns)
        self.assertIn('All', result.columns)
        self.assertIn('All', result.index)

    def test_monthwise_formwise_claims(self):
        result = self.detector.monthwise_formwise_claims(self.df)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('F1', result.columns)
        self.assertIn('F2', result.columns)
        self.assertIn('All', result.columns)
        self.assertIn('All', result.index)

    def test_monthwise_estwise_claims(self):
        result = self.detector.monthwise_estwise_claims(self.df)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('E1', result.columns)
        self.assertIn('E2', result.columns)
        self.assertIn('All', result.columns)
        self.assertIn('All', result.index)

    def test_monthwise_sectionwise_claims(self):
        result = self.detector.monthwise_sectionwise_claims(self.df)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('S1', result.columns)
        self.assertIn('S2', result.columns)
        self.assertIn('All', result.columns)
        self.assertIn('All', result.index)

    def test_monthwise_groupwise_claims(self):
        result = self.detector.monthwise_groupwise_claims(self.df)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn(101, result.columns)
        self.assertIn(102, result.columns)
        self.assertIn('All', result.columns)
        self.assertIn('All', result.index)

    def test_missing_columns_monthwise_genderwise(self):
        df_missing = self.df.drop(columns=['gender'])
        result = self.detector.monthwise_genderwise_claims(df_missing)
        self.assertTrue(result.empty)

    def test_missing_columns_monthwise_formwise(self):
        df_missing = self.df.drop(columns=['FORM_NAME'])
        result = self.detector.monthwise_formwise_claims(df_missing)
        self.assertTrue(result.empty)

    def test_missing_columns_monthwise_estwise(self):
        df_missing = self.df.drop(columns=['EST_ID'])
        result = self.detector.monthwise_estwise_claims(df_missing)
        self.assertTrue(result.empty)

    def test_missing_columns_monthwise_sectionwise(self):
        df_missing = self.df.drop(columns=['SECTION'])
        result = self.detector.monthwise_sectionwise_claims(df_missing)
        self.assertTrue(result.empty)

    def test_missing_columns_monthwise_groupwise(self):
        df_missing = self.df.drop(columns=['GROUP_ID'])
        result = self.detector.monthwise_groupwise_claims(df_missing)
        self.assertTrue(result.empty)

if __name__ == '__main__':
    unittest.main()
