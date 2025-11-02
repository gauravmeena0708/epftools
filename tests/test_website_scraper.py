import unittest
import os
import json
import pandas as pd
from unittest.mock import patch, MagicMock
from src.epftools.website_scraper import WebsiteScraper

class TestWebsiteScraper(unittest.TestCase):

    def setUp(self):
        self.scraper = WebsiteScraper(
            initial_url="http://test.com/circulars.php",
            post_url="http://test.com/get_cir_content.php",
            base_url="http://test.com/"
        )
        self.test_dir = "test_scraper_output"
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch('requests.get')
    @patch('requests.post')
    def test_scrape_circulars(self, mock_post, mock_get):
        # Mock initial page response
        mock_get.return_value.raise_for_status = MagicMock()
        mock_get.return_value.text = '''
            <html><body>
                <table>
                    <thead><tr><th>Col1</th><th>Col2</th><th>Col3</th><th>Col4</th></tr></thead>
                    <tr class="small_font"><td>1</td><td>Date 01/01/2023</td><td><a href="hindi.pdf">Hindi</a></td><td><a href="english.pdf">English</a></td></tr>
                </table>
                <select id="dd"><option value="2022"></option><option value="2021"></option></select>
            </body></html>
        '''

        # Mock post response for year 2022
        post_response_2022 = MagicMock()
        post_response_2022.raise_for_status = MagicMock()
        post_response_2022.text = '''
            <html><body>
                <table>
                    <thead><tr><th>Col1</th><th>Col2</th><th>Col3</th><th>Col4</th></tr></thead>
                    <tr class="small_font"><td>2</td><td>Date 02/02/2022</td><td><a href="hindi2.pdf">Hindi2</a></td><td><a href="english2.pdf">English2</a></td></tr>
                </table>
            </body></html>
        '''
        post_response_2021 = MagicMock()
        post_response_2021.raise_for_status = MagicMock()
        post_response_2021.text = '''
            <html><body>
                <table>
                    <thead><tr><th>Col1</th><th>Col2</th><th>Col3</th><th>Col4</th></tr></thead>
                </table>
            </body></html>
        '''
        mock_post.side_effect = [post_response_2022, post_response_2021]

        self.scraper.scrape_circulars()

        self.assertEqual(len(self.scraper.all_circulars), 2)
        self.assertEqual(self.scraper.all_circulars[0][0], '1')
        self.assertEqual(self.scraper.all_circulars[0][4], '') # Year for initial page
        self.assertEqual(self.scraper.all_circulars[0][5], '2023-01-01') # Formatted Date
        self.assertEqual(self.scraper.all_circulars[1][0], '2')
        self.assertEqual(self.scraper.all_circulars[1][4], '2022') # Year for post page
        self.assertEqual(self.scraper.all_circulars[1][5], '2022-02-02') # Formatted Date

        self.assertEqual(self.scraper.headers, ['Col1', 'Col2', 'Col3', 'Col4', 'Year', 'Date'])

    def test_save_data(self):
        self.scraper.all_circulars = [
            ['1', 'Date 01/01/2023', 'http://test.com/hindi.pdf', 'http://test.com/english.pdf', '2023', '2023-01-01']
        ]
        self.scraper.headers = ['Col1', 'Col2', 'Col3', 'Col4', 'Year', 'Date']

        json_output_path = os.path.join(self.test_dir, 'test_circulars.json')
        excel_output_path = os.path.join(self.test_dir, 'test_circulars.xlsx')

        self.scraper.save_data(json_file=json_output_path, excel_file=excel_output_path)

        self.assertTrue(os.path.exists(json_output_path))
        self.assertTrue(os.path.exists(excel_output_path))

        with open(json_output_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            self.assertEqual(len(json_data), 1)
            self.assertEqual(json_data[0]['Col1'], '1')

        excel_data = pd.read_excel(excel_output_path)
        self.assertEqual(len(excel_data), 1)
        self.assertEqual(str(excel_data.iloc[0]['Col1']), '1')

if __name__ == '__main__':
    unittest.main()
