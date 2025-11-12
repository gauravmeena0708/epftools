import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class EstmstAnalyzer:
    """
    A class for parsing and analyzing 'estmst' data.
    """

    dict_month = {
        'Jan':'01',
        'Feb':'02',
        'Mar':'03',
        'Apr':'04',
        'May':'05',
        'Jun':'06',
        'Jul':'07',
        'Aug':'08',
        'Sep':'09',
        'Oct':'10',
        'Nov':'11',
        'Dec':'12'
    }

    def __init__(self):
        pass

    def _change_col(self, x):
        year=x[-4:]
        month = self.dict_month[x[:3]]
        return str(year)+'-'+str(month)

    def parse_estmst_file(self, filename):
        """
        Parses a single 'estmst' CSV file into a tidy structure with
        columns: date (YYYY-MM), type (EST ID), metric, value.
        """
        try:
            df = pd.read_csv(filename, low_memory=False)
            if "EST ID" not in df.columns:
                logger.error(f"'EST ID' column missing in estmst file: {filename}")
                return pd.DataFrame()

            melted = df.melt(id_vars="EST ID", var_name="raw_field", value_name="value")
            melted.dropna(subset=["value"], inplace=True)

            month_metric = melted["raw_field"].str.rsplit("_", n=1, expand=True)
            if month_metric.shape[1] != 2:
                logger.error(f"Unexpected column format in estmst file: {filename}")
                return pd.DataFrame()

            melted["metric"] = month_metric[1].str.upper()

            def _safe_change_col(token):
                try:
                    return self._change_col(token)
                except (KeyError, TypeError):
                    logger.warning(f"Unsupported month token '{token}' in file {filename}")
                    return None

            melted["date"] = month_metric[0].apply(_safe_change_col)
            melted.dropna(subset=["date"], inplace=True)

            tidy = melted.rename(columns={"EST ID": "type"})
            tidy["value"] = pd.to_numeric(tidy["value"], errors="coerce")
            tidy.dropna(subset=["value"], inplace=True)

            tidy = tidy[["date", "type", "metric", "value"]]
            return tidy.reset_index(drop=True)

        except FileNotFoundError:
            logger.error(f"Estmst file not found: {filename}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error parsing estmst file {filename}: {e}")
            return pd.DataFrame()

    def analyze_multiple_estmst_files(self, filenames):
        """
        Analyzes multiple 'estmst' files, concatenates them, and performs transformations.
        `filenames` should be a dictionary where keys are identifiers (e.g., year) and values are file paths.
        """
        parsed_frames = []
        for key, filename in filenames.items():
            df = self.parse_estmst_file(filename)
            if not df.empty:
                parsed_frames.append(df.assign(source=key))

        if not parsed_frames:
            logger.warning("No valid estmst dataframes to concatenate.")
            return pd.DataFrame()

        df_common = pd.concat(parsed_frames, ignore_index=True)

        pivot = (
            df_common.pivot_table(
                index=["date", "type"],
                columns="metric",
                values="value",
                aggfunc="first"
            )
            .reset_index()
        )

        pivot = pivot.rename(columns={"type": "EST ID"})

        numeric_cols = [col for col in ["AMOUNT", "ECR", "MEMBER"] if col in pivot.columns]
        for col in numeric_cols:
            pivot[col] = pivot[col].round().astype("Int64")

        pivot["date"] = pd.to_datetime(pivot["date"], format="%Y-%m", errors="coerce")
        pivot = pivot.dropna(subset=["date"])
        pivot = pivot.sort_values(by=["EST ID", "date"]).reset_index(drop=True)

        logger.info(f"Analyzed {len(parsed_frames)} estmst files.")
        return pivot
