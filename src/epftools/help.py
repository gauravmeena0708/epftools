import textwrap

HELP_TEXT = {
    'PDFReport': '''
    The `PDFReport` class provides a unified interface for generating PDF reports from various sources.

    Engines:
    - 'reportlab': A good choice for creating simple, table-based reports.
    - 'wkhtmltopdf': Ideal for generating reports with complex styling and charts.

    Example (reportlab engine):
    ```python
    import pandas as pd
    from epftools import PDFReport

    df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    df2 = pd.DataFrame({'C': [5, 6], 'D': [7, 8]})

    report = PDFReport(engine='reportlab')
    report.from_dataframes([df1, df2], 'my_report.pdf')
    ```

    Example (wkhtmltopdf engine):
    ```python
    import pandas as pd
    from epftools import PDFReport

    df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    html_content = df1.to_html()

    wkhtmltopdf_path = '/path/to/wkhtmltopdf'

    report = PDFReport(engine='wkhtmltopdf', wkhtmltopdf_path=wkhtmltopdf_path)
    report.from_html(html_content, 'styled_report.pdf')
    ```
    ''',
    'ClaimProcessor': '''
    The `ClaimProcessor` class is designed to process EPF claim data. It helps in categorizing claims based on their status, type, and pendency period.

    Arguments:
    - `pendency_cutoff_1` (int): The first cut-off for pendency days.
    - `pendency_cutoff_2` (int): The second cut-off for pendency days.

    Example:
    ```python
    import pandas as pd
    from epftools import ClaimProcessor

    df = pd.read_csv('claims.csv')

    processor = ClaimProcessor(pendency_cutoff_1=15, pendency_cutoff_2=20)

    df = processor.add_bins_and_categories(df)

    pivot = processor.get_flat_pivot(df, index_col="GROUP", column_col="CATEGORY")
    print(pivot)
    ```
    ''',
    'ExcelMerger': '''
    The `ExcelMerger` class allows you to merge multiple Excel files from a folder into a single file.

    Arguments:
    - `folder_path` (str): The path to the folder containing the Excel files.
    - `ext` (str, optional): The file extension to look for. Defaults to ".xlsx".
    - `sheetnum` (int, optional): The sheet number to read from each file. Defaults to 0.

    Example:
    ```python
    from epftools import ExcelMerger

    folder_path = 'my_excel_files/'

    merger = ExcelMerger(folder_path)
    merger.merge_and_save('merged_file.xlsx')
    ```
    ''',
    'DataFrameStyler': '''
    The `DataFrameStyler` class provides a collection of static methods to style pandas DataFrames for better visualization, especially in reports.

    Example:
    ```python
    import pandas as pd
    from epftools import DataFrameStyler

    data = {'A': [10, 20, 5], 'B': [30, 40, 25]}
    df = pd.DataFrame(data)

    styled_df = df.style.apply(DataFrameStyler.highlight_max, color='lightblue')

    # display(styled_df)
    ```
    ''',
    'MultiSourceReportAggregator': '''
    The `MultiSourceReportAggregator` class is a powerful tool for consolidating data from various EPF-related reports into a single dashboard.

    Example:
    ```python
    from epftools import MultiSourceReportAggregator

    def my_custom_loader(file_path):
        df = pd.read_csv(file_path)
        return df

    aggregator = MultiSourceReportAggregator()

    aggregator.register_source('claims', 'path/to/claims.csv', my_custom_loader)
    aggregator.register_source('grievances', 'path/to/grievances.csv', my_custom_loader)

    dashboard_df = aggregator.generate_consolidated_report(base_source_name='claims')

    aggregator.export_to_html('dashboard.html')
    ```
    ''',
    'PDFOCR': '''
    The `PDFOCR` class provides functionality to perform Optical Character Recognition (OCR) on scanned PDF files, making them searchable.

    Note: This feature requires `tesseract` and `poppler` to be installed on your system.

    Example:
    ```python
    from epftools import PDFOCR

    poppler_path = r'/path/to/poppler/bin'
    input_folder = 'scanned_pdfs/'
    output_folder = 'searchable_pdfs/'

    PDFOCR.convert_images_to_pdf(input_folder, output_folder, poppler_path)
    ```
    ''',
    'PendencyProcessor': '''
    The `PendencyProcessor` class is used to parse and analyze EPF pendency reports.

    Example:
    ```python
    from epftools import PendencyProcessor

    processor = PendencyProcessor()

    files_to_process = [
        ('Pendency_DA.pdf', 'DA'),
        ('Pendency_SS.pdf', 'SS/Approver')
    ]
    merged_df = processor.process_files(files_to_process)

    summary = processor.create_pivot_summary(merged_df, 'days_cat', 'group')
    print(summary)
    ```
    ''',
    'periodicity': '''
    The `periodicity` module provides functions for analyzing the periodicity of claim settlements and rejections.

    Example:
    ```python
    from epftools import periodicity

    file_path = 'periodicity_data.csv'

    df = periodicity.read_periodicity_data(file_path, '2023-24')

    rejection_summary = periodicity.get_rejection_summary(df, "GROUP_ID")
    print(rejection_summary)
    ```
    ''',
    'RejectionCategorizer': '''
    The `RejectionCategorizer` uses machine learning to categorize claim rejection reasons. This requires the `scikit-learn` library (`pip install epftools[ml]`).

    Example:
    ```python
    import pandas as pd
    from epftools import RejectionCategorizer

    categorizer = RejectionCategorizer()

    training_data = pd.read_csv('labeled_reasons.csv')
    categorizer.train(training_data, reason_column='reason', category_column='category')

    new_reasons = ["PAN not seeded", "Incorrect bank details"]
    predictions = categorizer.predict(new_reasons)
    print(predictions)

    categorizer.save_model('rejection_model.pkl')
    ```
    ''',
    'ValidationUtils': '''
    The `ValidationUtils` class provides a set of static methods for validating various EPF-related data formats.

    Example:
    ```python
    from epftools import ValidationUtils

    is_valid, message = ValidationUtils.validate_member_id("PYKRP00123450001234567")
    print(f"Is member ID valid? {is_valid}, Message: {message}")

    is_valid, message = ValidationUtils.validate_claim_id("PYKRP123456789012")
    print(f"Is claim ID valid? {is_valid}, Message: {message}")
    ```
    '''
}

def show_help(topic=None):
    """
    Prints help information for the specified topic.

    Args:
        topic (str, optional): The topic to get help for. If None, lists all available topics.
    """
    if topic is None:
        print("Available topics:")
        for t in sorted(HELP_TEXT.keys()):
            print(f"- {t}")
        return

    if topic not in HELP_TEXT:
        print(f"Unknown topic: '{topic}'. Please choose from the available topics.")
        return

    print(textwrap.dedent(HELP_TEXT[topic]))
