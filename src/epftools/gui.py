import os
import tkinter as tk
from tkinter import filedialog, scrolledtext
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class EPFToolsGUI:
    """
    A simple GUI for EPF tools using Tkinter.
    """

    def __init__(self, master):
        self.master = master
        master.title("EPF Tools GUI")

        self.file_path = None

        # File selection frame
        self.file_frame = tk.LabelFrame(master, text="Select File")
        self.file_frame.pack(pady=10, padx=10, fill="x")

        self.file_label = tk.Label(self.file_frame, text="No file selected")
        self.file_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.browse_button = tk.Button(self.file_frame, text="Browse", command=self._browse_file)
        self.browse_button.pack(side=tk.RIGHT, padx=5, pady=5)

        # Summary display frame
        self.summary_frame = tk.LabelFrame(master, text="File Summary")
        self.summary_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.summary_text = scrolledtext.ScrolledText(self.summary_frame, wrap=tk.WORD, width=80, height=20)
        self.summary_text.pack(padx=5, pady=5, fill="both", expand=True)
        self.summary_text.insert(tk.END, "Select an Excel file to see its summary.")
        self.summary_text.config(state=tk.DISABLED) # Make it read-only

    def _browse_file(self):
        filetypes = [("Excel files", "*.xlsx"), ("CSV files", "*.csv"), ("All files", "*.*")]
        self.file_path = filedialog.askopenfilename(filetypes=filetypes)
        if self.file_path:
            self.file_label.config(text=os.path.basename(self.file_path))
            logger.info(f"Selected file: {self.file_path}")
            self._display_summary()
        else:
            self.file_label.config(text="No file selected")
            self.summary_text.config(state=tk.NORMAL)
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(tk.END, "No file selected.")
            self.summary_text.config(state=tk.DISABLED)

    def _display_summary(self):
        if not self.file_path:
            return

        try:
            if self.file_path.endswith(".xlsx"):
                df = pd.read_excel(self.file_path)
            elif self.file_path.endswith(".csv"):
                df = pd.read_csv(self.file_path)
            else:
                self.summary_text.config(state=tk.NORMAL)
                self.summary_text.delete(1.0, tk.END)
                self.summary_text.insert(tk.END, "Unsupported file type.")
                self.summary_text.config(state=tk.DISABLED)
                return

            summary_str = df.describe().to_string()
            self.summary_text.config(state=tk.NORMAL)
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(tk.END, summary_str)
            self.summary_text.config(state=tk.DISABLED)
            logger.info(f"Displayed summary for {self.file_path}")
        except Exception as e:
            self.summary_text.config(state=tk.NORMAL)
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(tk.END, f"Error reading file: {e}")
            self.summary_text.config(state=tk.DISABLED)
            logger.error(f"Error displaying summary for {self.file_path}: {e}")

def run_gui():
    root = tk.Tk()
    app = EPFToolsGUI(root)
    root.mainloop()

if __name__ == '__main__':
    run_gui()
