import pandas as pd
import logging

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """
    A class for performing anomaly detection on EPF claims data.
    """

    def __init__(self):
        pass

    def _create_pivot_table(self, df, index_col, column_col, value_col='CLAIM_ID'):
        """
        Helper function to create a pivot table.
        """
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame.")
        
        if value_col not in df.columns:
            logger.warning(f"Value column '{value_col}' not found. Using default count aggregation.")
            return pd.pivot_table(df, index=index_col, columns=column_col,
                                  margins=True, aggfunc='size').fillna(0).astype(int)

        return pd.pivot_table(df, values=value_col, index=index_col, columns=column_col,
                              margins=True, aggfunc='count').fillna(0).astype(int)

    def monthwise_genderwise_claims(self, df):
        """
        Analyzes claims month-wise and gender-wise.
        Requires 'month' and 'gender' columns in the DataFrame.
        """
        logger.info("Performing month-wise, gender-wise claims analysis.")
        # Placeholder for gender-wise analysis, assuming 'gender' column exists
        if 'month' not in df.columns or 'gender' not in df.columns:
            logger.warning("DataFrame must contain 'month' and 'gender' columns for month-wise, gender-wise analysis.")
            return pd.DataFrame()
        return self._create_pivot_table(df, index_col='month', column_col='gender')

    def monthwise_formwise_claims(self, df):
        """
        Analyzes claims month-wise and form-wise.
        Requires 'month' and 'FORM_NAME' columns in the DataFrame.
        """
        logger.info("Performing month-wise, form-wise claims analysis.")
        if 'month' not in df.columns or 'FORM_NAME' not in df.columns:
            logger.warning("DataFrame must contain 'month' and 'FORM_NAME' columns for month-wise, form-wise analysis.")
            return pd.DataFrame()
        return self._create_pivot_table(df, index_col='month', column_col='FORM_NAME')

    def monthwise_estwise_claims(self, df):
        """
        Analyzes claims month-wise and establishment-wise.
        Requires 'month' and 'EST_ID' (or similar) columns in the DataFrame.
        """
        logger.info("Performing month-wise, establishment-wise claims analysis.")
        if 'month' not in df.columns or 'EST_ID' not in df.columns:
            logger.warning("DataFrame must contain 'month' and 'EST_ID' columns for month-wise, establishment-wise analysis.")
            return pd.DataFrame()
        return self._create_pivot_table(df, index_col='month', column_col='EST_ID')

    def monthwise_sectionwise_claims(self, df):
        """
        Analyzes claims month-wise and section-wise.
        Requires 'month' and 'SECTION' (or similar) columns in the DataFrame.
        """
        logger.info("Performing month-wise, section-wise claims analysis.")
        if 'month' not in df.columns or 'SECTION' not in df.columns:
            logger.warning("DataFrame must contain 'month' and 'SECTION' columns for month-wise, section-wise analysis.")
            return pd.DataFrame()
        return self._create_pivot_table(df, index_col='month', column_col='SECTION')

    def monthwise_groupwise_claims(self, df):
        """
        Analyzes claims month-wise and group-wise.
        Requires 'month' and 'GROUP_ID' columns in the DataFrame.
        """
        logger.info("Performing month-wise, group-wise claims analysis.")
        if 'month' not in df.columns or 'GROUP_ID' not in df.columns:
            logger.warning("DataFrame must contain 'month' and 'GROUP_ID' columns for month-wise, group-wise analysis.")
            return pd.DataFrame()
        return self._create_pivot_table(df, index_col='month', column_col='GROUP_ID')