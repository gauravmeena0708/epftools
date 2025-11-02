# EPF Tools

[![version number](https://img.shields.io/github/v/release/gauravmeena0708/epftools.svg)](https://github.com/gauravmeena0708/epftools/releases)
[![Actions Status](https://github.com/gauravmeena0708/epftools/workflows/Test/badge.svg)](https://github.com/gauravmeena0708/epftools/actions)
[![License](https://img.shields.io/github/license/gauravmeena0708/epftools)](https://github.com/gauravmeena0708/epftools/blob/main/LICENSE)

This is an alpha repo for EPF analysis tool.

## Install

```bash
pip install -e git+https://github.com/gauravmeena0708/epftools#egg=epftools
```

## Features

### Anomaly Detector

The `AnomalyDetector` class provides methods for detecting anomalies in EPF claims data.

**Example:**

```python
import pandas as pd
from epftools import AnomalyDetector

# Load your claim data
df = pd.read_csv('claims.csv')

# Initialize the detector
detector = AnomalyDetector()

# Get month-wise, form-wise claims analysis
pivot = detector.monthwise_formwise_claims(df)
print(pivot)
```

### Daily Reporter

The `DailyReporter` class generates daily reports from various EPF data sources.

**Example:**

```python
from epftools import DailyReporter

# Initialize the reporter
reporter = DailyReporter(download_dir='path/to/your/data', template_path='path/to/your/template.html', wkhtmltopdf_path='/path/to/wkhtmltopdf')

# Generate the report
reporter.generate_daily_report()
```

### Word Reporter

The `WordReporter` class provides an interface for generating Word documents.

**Example:**

```python
from epftools import WordReporter

# Initialize the reporter
reporter = WordReporter()

# Add content to the document
reporter.add_heading("My Report", level=1)
reporter.add_paragraph("This is a paragraph in my report.")

# Save the document
reporter.save("my_report.docx")
```

### Estmst Analyzer

The `EstmstAnalyzer` class is used to parse and analyze "estmst" data.

**Example:**

```python
from epftools import EstmstAnalyzer

# Initialize the analyzer
analyzer = EstmstAnalyzer()

# Analyze multiple estmst files
filenames = {
    '2021': 'path/to/2021.csv',
    '2022': 'path/to/2022.csv'
}
df_analyzed = analyzer.analyze_multiple_estmst_files(filenames)
print(df_analyzed.head())
```

### GUI

The `EPFToolsGUI` class provides a simple graphical user interface for the package.

**Example:**

```python
from epftools.gui import run_gui

# Run the GUI
run_gui()
```

### PDF Tools

The `PDFTools` class provides static methods for working with PDF files.

#### Splitting PDFs

The `split_pdf` function allows you to split a PDF file into multiple smaller files based on page ranges.

**Example:**

```python
from epftools import PDFTools

input_path = "my_document.pdf"
output_path_template = "split_doc_{0}_{1}.pdf"
page_ranges = [(1, 3), (4, 6), (7, 10)]

PDFTools.split_pdf(input_path, output_path_template, page_ranges)
```

#### Merging PDFs

The `merge_pdfs` function allows you to merge multiple PDF files into a single file.

**Example:**

```python
from epftools import PDFTools

input_files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
output_file = "merged_document.pdf"

PDFTools.merge_pdfs(input_files, output_file)
```

#### Conditional PDF Splitting

The `split_pdf_on_condition` method splits a PDF file based on a condition found in the text of each page.

**Example:**

```python
from epftools import PDFTools

# To split pages where a year less than 2019 is found in a specific sentence pattern:
pattern = r'Stoppage of pension from .* (\\d{4}) -Regarding\\.'
condition_func = lambda matches: len(matches) > 0 and int(matches[0]) < 2019
PDFTools.split_pdf_on_condition("input.pdf", "old_pension_docs.pdf", pattern, condition_func)
```

### Performance Analyzer

The `PerformanceAnalyzer` class is used to analyze performance data and generate reports.

**Example:**

```python
from epftools import PerformanceAnalyzer

# Initialize the analyzer
analyzer = PerformanceAnalyzer(directory_path='path/to/reports', template_path='path/to/template.html', wkhtmltopdf_path='/path/to/wkhtmltopdf')

# Generate the performance report
analyzer.generate_performance_report()
```

### Website Scraper

The `WebsiteScraper` class scrapes circulars from the EPFO website.

**Example:**

```python
from epftools import WebsiteScraper

# Initialize the scraper
scraper = WebsiteScraper()

# Scrape the circulars
scraper.scrape_circulars()

# Save the data
scraper.save_data(json_file='circulars.json', excel_file='circulars.xlsx')
```

### PDF Report Generation

The `PDFReport` class provides a unified interface for generating PDF reports from various sources.

**Engines:**

*   `reportlab`: A good choice for creating simple, table-based reports.
*   `wkhtmltopdf`: Ideal for generating reports with complex styling and charts, as it leverages the power of HTML and CSS.

**Example (reportlab engine):**

```python
import pandas as pd
from epftools import PDFReport

# Create some sample DataFrames
df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
df2 = pd.DataFrame({'C': [5, 6], 'D': [7, 8]})

# Create the PDF report
report = PDFReport(engine='reportlab')
report.from_dataframes([df1, df2], 'my_report.pdf')
```

**Example (wkhtmltopdf engine):**

```python
import pandas as pd
from epftools import PDFReport

# Your dataframes
df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
html_content = df1.to_html()

# Path to wkhtmltopdf
wkhtmltopdf_path = '/path/to/wkhtmltopdf'

# Create the PDF report
report = PDFReport(engine='wkhtmltopdf', wkhtmltopdf_path=wkhtmltopdf_path)
report.from_html(html_content, 'styled_report.pdf')
```

### Visualization

The `visualization` module provides tools for creating geospatial visualizations.

#### Choropleth Maps

The `create_choropleth_map` function creates an interactive choropleth map from your data and saves it as an HTML file.

**Example:**

```python
import pandas as pd
from epftools.visualization import create_choropleth_map

# Create a sample DataFrame
data = {
    'pincode': ['560001', '560002', '560003'],
    'office': ['Office A', 'Office B', 'Office A'],
    'establishments': [100, 150, 120],
    'members': [2000, 2500, 2200]
}
df = pd.DataFrame(data)

# Path to your GeoJSON file
geojson_file = "path/to/your/map.json"

# Create the map
create_choropleth_map(
    df=df,
    location_col='pincode',
    color_col='office',
    geojson_path=geojson_file,
    output_path='my_map.html'
)
```

### Claim Processor

The `ClaimProcessor` class is designed to process EPF claim data. It helps in categorizing claims based on their status, type, and pendency period.

**Arguments:**

*   `pendency_cutoff_1` (int): The first cut-off for pendency days.
*   `pendency_cutoff_2` (int): The second cut-off for pendency days.

**Example:**

```python
import pandas as pd
from epftools import ClaimProcessor

# Load your claim data
df = pd.read_csv('claims.csv')

# Initialize the processor
processor = ClaimProcessor(pendency_cutoff_1=15, pendency_cutoff_2=20)

# Add bins and categories to the DataFrame
df = processor.add_bins_and_categories(df)

# Generate a pivot table
pivot = processor.get_flat_pivot(df, index_col="GROUP", column_col="CATEGORY")
print(pivot)
```

### Excel Merger

The `ExcelMerger` class allows you to merge multiple Excel files from a folder into a single file.

**Arguments:**

*   `folder_path` (str): The path to the folder containing the Excel files.
*   `ext` (str, optional): The file extension to look for. Defaults to ".xlsx".
*   `sheetnum` (int, optional): The sheet number to read from each file. Defaults to 0.

**Example:**

```python
from epftools import ExcelMerger

# Path to the folder with your Excel files
folder_path = 'my_excel_files/'

# Merge the files
merger = ExcelMerger(folder_path)
merger.merge_and_save('merged_file.xlsx')
```

### DataFrame Styler

The `DataFrameStyler` class provides a collection of static methods to style pandas DataFrames for better visualization, especially in reports.

**Example:**

```python
import pandas as pd
from epftools import DataFrameStyler

# Create a sample DataFrame
data = {'A': [10, 20, 5], 'B': [30, 40, 25]}
df = pd.DataFrame(data)

# Apply styling
styled_df = df.style.apply(DataFrameStyler.highlight_max, color='lightblue')

# In a Jupyter environment, you can display it directly
# display(styled_df)

# Or get the default styled table for reports
default_styled = DataFrameStyler.get_styled_default(df)
```

### Multi-Source Report Aggregator

The `MultiSourceReportAggregator` class is a powerful tool for consolidating data from various EPF-related reports into a single dashboard.

**Example:**

```python
from epftools import MultiSourceReportAggregator

# Define a loader function for your custom data source
def my_custom_loader(file_path):
    # Your data loading and processing logic here
    df = pd.read_csv(file_path)
    # ...
    return df

# Create the aggregator
aggregator = MultiSourceReportAggregator()

# Register your data sources
aggregator.register_source('claims', 'path/to/claims.csv', my_custom_loader)
aggregator.register_source('grievances', 'path/to/grievances.csv', my_custom_loader)

# Generate the consolidated report
dashboar_df = aggregator.generate_consolidated_report(base_source_name='claims')

# Export the report
aggregator.export_to_html('dashboard.html')
aggregator.export_to_excel('dashboard.xlsx')
```

### PDF OCR

The `PDFOCR` class provides functionality to perform Optical Character Recognition (OCR) on scanned PDF files, making them searchable.

**Note:** This feature requires `tesseract` and `poppler` to be installed on your system.

**Example:**

```python
from epftools import PDFOCR

# Paths to your tools and files
poppler_path = r'/path/to/poppler/bin'
input_folder = 'scanned_pdfs/'
output_folder = 'searchable_pdfs/'

# Convert the PDFs
PDFOCR.convert_images_to_pdf(input_folder, output_folder, poppler_path)
```

### Pendency Processor

The `PendencyProcessor` class is used to parse and analyze EPF pendency reports.

**Example:**

```python
from epftools import PendencyProcessor

# Initialize the processor
processor = PendencyProcessor()

# Process a list of pendency files
files_to_process = [
    ('Pendency_DA.pdf', 'DA'),
    ('Pendency_SS.pdf', 'SS/Approver')
]
merged_df = processor.process_files(files_to_process)

# Create a summary pivot table
summary = processor.create_pivot_summary(merged_df, 'days_cat', 'group')
print(summary)
```

### Periodicity Analysis

The `periodicity` module provides functions for analyzing the periodicity of claim settlements and rejections.

**Example:**

```python
from epftools import periodicity

# Path to your periodicity data
file_path = 'periodicity_data.csv'

# Read and process the data
df = periodicity.read_periodicity_data(file_path, '2023-24')

# Get a rejection summary grouped by a column
rejection_summary = periodicity.get_rejection_summary(df, "GROUP_ID")
print(rejection_summary)
```

### Rejection Categorizer

The `RejectionCategorizer` uses machine learning to categorize claim rejection reasons. This requires the `scikit-learn` library (`pip install epftools[ml]`).

**Example:**

```python
import pandas as pd
from epftools import RejectionCategorizer

# Initialize the categorizer
categorizer = RejectionCategorizer()

# Load training data and train the model
training_data = pd.read_csv('labeled_reasons.csv')
categorizer.train(training_data, reason_column='reason', category_column='category')

# Predict categories for new rejection reasons
new_reasons = ["PAN not seeded", "Incorrect bank details"]
predictions = categorizer.predict(new_reasons)
print(predictions)

# Save the trained model for later use
categorizer.save_model('rejection_model.pkl')
```

### Validation Utilities

The `ValidationUtils` class provides a set of static methods for validating various EPF-related data formats.

**Example:**

```python
from epftools import ValidationUtils

# Validate a member ID
is_valid, message = ValidationUtils.validate_member_id("PYKRP00123450001234567")
print(f"Is member ID valid? {is_valid}, Message: {message}")

# Validate a claim ID
is_valid, message = ValidationUtils.validate_claim_id("PYKRP123456789012")
print(f"Is claim ID valid? {is_valid}, Message: {message}")

# Batch validate a list of items
claim_ids = ["PYKRP123456789012", "INVALID_ID", "PYKRP123456789013"]
results = ValidationUtils.validate_batch(claim_ids, ValidationUtils.validate_claim_id)
print(f"Validation results: {results}")
```
