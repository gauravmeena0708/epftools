import unittest
import tkinter as tk
from tkinter import filedialog
from unittest.mock import patch, MagicMock
import os
import pandas as pd
from src.epftools.gui import EPFToolsGUI
from tkinter import TclError

class TestEPFToolsGUI(unittest.TestCase):

    def setUp(self):
        try:
            self.root = tk.Tk()
        except TclError as exc:
            self.skipTest(f"Tk display unavailable: {exc}")
        self.root.withdraw()  # Hide the main window
        self.app = EPFToolsGUI(self.root)
        self.test_dir = "test_gui_data"
        os.makedirs(self.test_dir, exist_ok=True)

        self.dummy_excel_path = os.path.join(self.test_dir, "dummy.xlsx")
        pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]}).to_excel(self.dummy_excel_path, index=False)

        self.dummy_csv_path = os.path.join(self.test_dir, "dummy.csv")
        pd.DataFrame({'colA': [5, 6], 'colB': [7, 8]}).to_csv(self.dummy_csv_path, index=False)

    def tearDown(self):
        self.root.destroy()
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch('tkinter.filedialog.askopenfilename')
    def test_browse_file_excel(self, mock_askopenfilename):
        mock_askopenfilename.return_value = self.dummy_excel_path
        self.app._browse_file()
        self.assertEqual(self.app.file_path, self.dummy_excel_path)
        self.assertIn("count", self.app.summary_text.get(1.0, tk.END))

    @patch('tkinter.filedialog.askopenfilename')
    def test_browse_file_csv(self, mock_askopenfilename):
        mock_askopenfilename.return_value = self.dummy_csv_path
        self.app._browse_file()
        self.assertEqual(self.app.file_path, self.dummy_csv_path)
        self.assertIn("count", self.app.summary_text.get(1.0, tk.END))

    @patch('tkinter.filedialog.askopenfilename')
    def test_browse_file_no_selection(self, mock_askopenfilename):
        mock_askopenfilename.return_value = ""
        self.app._browse_file()
        self.assertIsNone(self.app.file_path)
        self.assertEqual(self.app.file_label.cget("text"), "No file selected")

    def test_display_summary_unsupported_file(self):
        self.app.file_path = os.path.join(self.test_dir, "unsupported.txt")
        with open(self.app.file_path, "w") as f:
            f.write("some text")
        self.app._display_summary()
        self.assertIn("Unsupported file type", self.app.summary_text.get(1.0, tk.END))

if __name__ == '__main__':
    unittest.main()
