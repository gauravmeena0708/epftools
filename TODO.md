# TODO

This document outlines the tasks for incorporating new functionalities into the `epftools` package.

## New Features

### Anomaly Detection
- [x] Create a new module `src/epftools/anomaly_detector.py`.
- [x] Implement functions for anomaly detection based on the suggestions in `tests/todo/anomaly.py`.
  - [x] Month-wise, gender-wise claims analysis.
  - [x] Month-wise, form-wise claims analysis.
  - [x] Month-wise, establishment-wise claims analysis.
  - [x] Month-wise, section-wise claims analysis.
- [x] Add the new module to `__init__.py`.
- [x] Add unit tests for the anomaly detection module.

### Daily Report Generation
- [x] Create a new module `src/epftools/daily_reporter.py`.
- [x] Implement a class for generating daily reports, based on the logic in `tests/todo/dailyreport.py` and `tests/todo/dailyreport2.py`.
  - [x] Consolidate data from multiple sources (claims, dsc, esign, etc.).
  - [x] Create pivot tables and summaries.
  - [x] Generate an HTML report from the processed data.
  - [x] Add the new module to `__init__.py`.
- [x] Add unit tests for the daily report generation module.

### Word Document Generation
- [x] Create a new module `src/epftools/word_reporter.py`.
- [x] Implement a class for generating Word documents, based on the logic in `tests/todo/dox use.py`.
  - [x] Add functionality to create headings, paragraphs, and tables.
- [x] Add the new module to `__init__.py`.
- [x] Add unit tests for the Word document generation module.

### "estmst" Data Analysis
- [x] Create a new module `src/epftools/estmst_analyzer.py`.
- [x] Add the new module to `__init__.py`.
- [x] Add unit tests for the "estmst" data analysis module.

### GUI
- [x] Create a new module `src/epftools/gui.py`.
- [x] Implement a simple GUI for the package using `tkinter`, based on the logic in `tests/todo/gui.py`.
  - [x] Add a file browser to select input files.
  - [x] Add a display area for showing results and summaries.
- [x] Add the new module to `__init__.py`.
- [x] Add unit tests for the GUI module.

### Conditional PDF Splitting
- [x] Enhance the existing `PDFTools` class in `src/epftools/pdf_tools.py`.
- [x] Add a new method `split_pdf_on_condition` to split a PDF based on a condition in the text of each page, based on the logic in `tests/todo/pdf_split_oncondition.py`.
  - [x] The method should accept a regular expression and a condition function as arguments.
- [x] Add unit tests for the new method.

### Performance Analysis
- [x] Create a new module `src/epftools/performance_analyzer.py`.
- [x] Implement a class for analyzing performance data and generating reports, based on the logic in `tests/todo/perfCompared.py` and `tests/todo/performance.py`.
  - [x] Read performance data from Excel files.
  - [x] Compare performance between different periods.
  - [x] Generate PDF reports with pivot tables and summaries.
- [x] Add the new module to `__init__.py`.
- [x] Add unit tests for the performance analysis module.

### Website Scraping
- [x] Create a new module `src/epftools/website_scraper.py`.
- [x] Implement a class for scraping circulars from the EPFO website, based on the logic in `tests/todo/website.py`.
  - [x] Fetch and parse HTML from the website.
  - [x] Save the scraped data to JSON and Excel files.
- [x] Add the new module to `__init__.py`.
- [x] Add unit tests for the website scraping module.
