import pandas as pd
import logging

logger = logging.getLogger(__name__)


class DataFrameStyler:
    """
    Utility class for styling pandas DataFrames with various highlighting methods.

    Provides static methods for highlighting cells based on values, quantiles,
    changes, and custom conditions.
    """

    @staticmethod
    def highlight_min(s, color='green'):
        """
        Highlight minimum values in a Series.

        Args:
            s (pd.Series): Input series
            color (str): Background color for minimum values

        Returns:
            list: List of CSS style strings
        """
        is_min = s == s.min()
        attr = f'background-color: {color}'
        return [attr if v else '' for v in is_min]

    @staticmethod
    def highlight_max(s, color='yellow'):
        """
        Highlight maximum values in a Series.

        Args:
            s (pd.Series): Input series
            color (str): Background color for maximum values

        Returns:
            list: List of CSS style strings
        """
        is_max = s == s.max()
        attr = f'background-color: {color}'
        return [attr if v else '' for v in is_max]

    @staticmethod
    def highlight_top3(s, color='darkorange'):
        """
        Highlight top 3 values in a Series (excluding zeros).

        Args:
            s (pd.Series): Input series
            color (str): Background color for top 3 values

        Returns:
            list: List of CSS style strings
        """
        top3_values = s.nlargest(3).index
        is_top3 = s.index.isin(top3_values) & (s > 0)
        attr = f'background-color: {color};font-weight: bold;'
        return [attr if v else '' for v in is_top3]

    @staticmethod
    def conditional_color(val, cutoff=100, color='red'):
        """
        Apply text color if value exceeds cutoff.

        Args:
            val (numeric): Cell value
            cutoff (numeric): Threshold value
            color (str): Text color to apply if val > cutoff

        Returns:
            str: CSS style string
        """
        return f"color: {color}" if val > cutoff else "color: black"

    @staticmethod
    def color_quantile(s, color='red', quantile=0.75):
        """
        Highlight values in the top quantile (excluding zeros).

        Args:
            s (pd.Series): Input series
            color (str): Background color for top quantile
            quantile (float): Quantile threshold (default: 0.75 for top 25%)

        Returns:
            list: List of CSS style strings
        """
        threshold = s.quantile(quantile)
        is_in_quantile = (s >= threshold) & (s > 0)
        attr = f'background-color: {color}'
        return [attr if v else '' for v in is_in_quantile]

    @staticmethod
    def color_change_from_previous(x, increase_color='red', decrease_color='green',
                                   increase_threshold=200, decrease_threshold=-200):
        """
        Color cells based on change from previous value (for time series data).

        Highlights values that increased or decreased significantly compared
        to the previous column.

        Args:
            x (pd.Series): Row of values
            increase_color (str): Color for significant increases
            decrease_color (str): Color for significant decreases
            increase_threshold (numeric): Threshold for increase highlighting
            decrease_threshold (numeric): Threshold for decrease highlighting

        Returns:
            list: List of CSS style strings

        Example:
            # For monthly data showing increases/decreases
            df.style.apply(color_change_from_previous, axis=1)
        """
        styles = []

        for i, (val, col) in enumerate(zip(x, x.index)):
            style = 'color: black;'

            if i > 0:  # Skip first column (no previous to compare)
                previous_value = x.iloc[i - 1]
                change = val - previous_value

                if change > increase_threshold:
                    style = f'color: {increase_color};font-weight: bold;'
                elif change < decrease_threshold:
                    style = f'color: {decrease_color};font-weight: bold;'

            styles.append(style)

        return styles

    @staticmethod
    def color_by_threshold_with_highlight(val, threshold=1000, highlight_color='orange'):
        """
        Highlight cells exceeding threshold with background color.

        Args:
            val (numeric): Cell value
            threshold (numeric): Threshold for highlighting
            highlight_color (str): Background color to apply

        Returns:
            str: CSS style string
        """
        if val > threshold:
            return f'background-color: {highlight_color};'
        return ''

    @staticmethod
    def get_styled_default(df, axis=1):
        """
        Apply default styling to pivot tables (highlight top 3 values).

        Args:
            df (pd.DataFrame): Input dataframe (typically a pivot table with margins)
            axis (int): Axis to apply styling (0=columns, 1=rows)

        Returns:
            pd.io.formats.style.Styler: Styled dataframe
        """
        try:
            u = df.index.get_level_values(0)
            cols = df.columns

            # Apply to all except margins row/column
            df_styled = df.style.apply(
                DataFrameStyler.highlight_top3, color='orange',
                subset=pd.IndexSlice[u[:-1], cols[:-1]], axis=axis
            )

            return df_styled

        except Exception as e:
            logger.warning(f"Failed to apply default styling: {str(e)}")
            return df.style

    @staticmethod
    def get_styled_with_quantiles(df, axis=1):
        """
        Apply styling with both top 3 highlighting and top quantile coloring.

        Args:
            df (pd.DataFrame): Input dataframe
            axis (int): Axis to apply styling

        Returns:
            pd.io.formats.style.Styler: Styled dataframe
        """
        try:
            u = df.index.get_level_values(0)
            cols = df.columns

            df_styled = df.style.apply(
                DataFrameStyler.highlight_top3, color='darkred',
                subset=pd.IndexSlice[u[:-1], cols[:-1]], axis=axis
            ).apply(
                DataFrameStyler.color_quantile, color='khaki',
                subset=pd.IndexSlice[u[:-1], cols[:-1]], axis=axis
            )

            return df_styled

        except Exception as e:
            logger.warning(f"Failed to apply quantile styling: {str(e)}")
            return df.style


