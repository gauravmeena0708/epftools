import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class MultiSourceReportAggregator:
    """
    Aggregate reports from multiple EPF data sources into a unified dashboard.
    """

    def __init__(self):
        """
        Initialize MultiSourceReportAggregator.
        """
        self.sources = {}
        self.consolidated_report = None

    def register_source(self, source_name, file_path, loader_function):
        """
        Register a new data source.

        Args:
            source_name (str): A unique name for the data source.
            file_path (str): The path to the data file.
            loader_function (callable): A function that takes a file path and returns a pandas DataFrame.
        """
        self.sources[source_name] = {
            'file_path': file_path,
            'loader': loader_function
        }

    def generate_consolidated_report(self, base_source_name):
        """
        Generate a consolidated report from all registered data sources.

        Args:
            base_source_name (str): The name of the source to be used as the base for the report.

        Returns:
            pd.DataFrame: A consolidated DataFrame.
        """
        if base_source_name not in self.sources:
            raise ValueError(f"Base source '{base_source_name}' not registered.")

        logger.info(f"Generating consolidated report with base source: {base_source_name}")

        base_source = self.sources[base_source_name]
        base_df = base_source['loader'](base_source['file_path'])

        if base_df is None:
            raise RuntimeError(f"Failed to load base source: {base_source_name}")

        for source_name, source_info in self.sources.items():
            if source_name == base_source_name:
                continue

            try:
                source_df = source_info['loader'](source_info['file_path'])
                if source_df is not None:
                    base_df = base_df.merge(source_df, how='outer', left_index=True, right_index=True)
            except Exception as e:
                logger.warning(f"Failed to load or merge source '{source_name}': {e}")

        base_df.sort_index(inplace=True)
        self.consolidated_report = base_df.fillna(0).astype(int)

        logger.info(f"Consolidated report generated with {len(self.consolidated_report)} rows.")
        return self.consolidated_report

    def export_to_html(self, output_path):
        """
        Export the consolidated report to an HTML file.

        Args:
            output_path (str): The path for the output HTML file.
        """
        if self.consolidated_report is None:
            raise RuntimeError("Consolidated report not generated. Call generate_consolidated_report() first.")
        self.consolidated_report.to_html(output_path)
        logger.info(f"Report exported to {output_path}")

    def export_to_excel(self, output_path):
        """
        Export the consolidated report to an Excel file.

        Args:
            output_path (str): The path for the output Excel file.
        """
        if self.consolidated_report is None:
            raise RuntimeError("Consolidated report not generated. Call generate_consolidated_report() first.")
        self.consolidated_report.to_excel(output_path)
        logger.info(f"Report exported to {output_path}")


# Example usage
"""
from epftools import MultiSourceReportAggregator

# Configure data sources
config = {
    'claims': 'data/Claim.xls',
    'epfigms': 'data/EPFiGMS.xlsx',
    'esign': 'data/esign.xlsx',
    'dsc': 'data/dsc.xlsx',
    'transfer': 'data/transfer.csv',
    'basic': 'data/249_pending_list_online.xlsx',
    'primary': 'data/249_pending_list_primary.xlsx',
    'others': 'data/249_pending_list_others.xlsx'
}

# Create aggregator
aggregator = MultiSourceReportAggregator(config)

# Generate consolidated dashboard
dashboard_df = aggregator.generate_consolidated_report()

# View summary
print(dashboard_df.head())

# Export to formats
aggregator.export_to_html('dashboard.html')
aggregator.export_to_excel('dashboard.xlsx')

# Style with DataFrameStyler (optional)
from epftools import DataFrameStyler
styled = DataFrameStyler.get_styled_default(dashboard_df)
display(styled)  # In Jupyter
"""
