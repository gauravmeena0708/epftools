# EPF Tools

[![version number](https://img.shields.io/github/v/release/gauravmeena0708/epf_tools2.svg)](https://github.com/gauravmeena0708/epf_tools2/releases)
[![Actions Status](https://github.com/gauravmeena0708/epf_tools2/workflows/Test/badge.svg)](https://github.com/gauravmeena0708/epf_tools2/actions)
[![License](https://img.shields.io/github/license/gauravmeena0708/epf_tools2)](https://github.com/gauravmeena0708/epf_tools2/blob/main/LICENSE)

This is an alpha repo for EPF analysis tool.

## Install

```bash
pip install -e git+https://github.com/gauravmeena0708/epftools#egg=epftools
```

## Features

### PDF Tools

The `PDFTools` class provides static methods for working with PDF files.

#### Splitting PDFs

The `split_pdf` function allows you to split a PDF file into multiple smaller files based on page ranges.

**Arguments:**

*   `input_path` (str): Path to the input PDF file.
*   `output_path_template` (str): A template for the output file names (e.g., "output_{0}_{1}.pdf").
*   `page_ranges` (list): A list of tuples, where each tuple defines a page range `(start_page, end_page)`.

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

**Arguments:**

*   `input_paths` (list): A list of paths to the input PDF files.
*   `output_path` (str): The path for the output merged PDF file.

**Example:**

```python
from epftools import PDFTools

input_files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
output_file = "merged_document.pdf"

PDFTools.merge_pdfs(input_files, output_file)
```

### Visualization

The `visualization` module provides tools for creating geospatial visualizations.

#### Choropleth Maps

The `create_choropleth_map` function creates an interactive choropleth map from your data and saves it as an HTML file.

**Arguments:**

*   `df` (pd.DataFrame): A pandas DataFrame containing the data to plot.
*   `location_col` (str): The name of the column in the DataFrame that contains the location data (e.g., pincodes).
*   `color_col` (str): The name of the column to use for the color scale.
*   `geojson_path` (str): The path to the GeoJSON file with the map data.
*   `output_path` (str): The path to save the generated HTML file.

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

### Other Examples

... (existing examples can be moved here)
