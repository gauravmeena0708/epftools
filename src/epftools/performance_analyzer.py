import pandas as pd
import numpy as np
import os
import re
import time
import logging
from pathlib import Path
from bs4 import BeautifulSoup
import pdfkit

logger = logging.getLogger(__name__)

class PerformanceAnalyzer:
    """
    A class for analyzing performance data and generating reports.
    """

    def __init__(self, directory_path="reports/", template_path="templates/template.html", wkhtmltopdf_path="/path/to/wkhtmltopdf.exe"):
        self.directory_path = directory_path
        self.template = Path(template_path).read_text()
        self.wkhtmltopdf_path = wkhtmltopdf_path
        self.pdfkit_config = None
        try:
            path = "" if wkhtmltopdf_path == "/path/to/wkhtmltopdf.exe" else wkhtmltopdf_path
            self.pdfkit_config = pdfkit.configuration(wkhtmltopdf=path)
        except (OSError, FileNotFoundError) as exc:
            logger.warning("wkhtmltopdf not available (%s); PDF generation will rely on system defaults.", exc)

        self.rejection_cols = ['Pending at SS/AO/AC Accounts [Rejection]']
        self.approver_cols = ['Pending [ Approver Pending ]', 'Pending at SS/AO/AC Accounts']
        self.da_cols      = ['Pending at DA','Pending at DA Accounts [EDIT]', 'Pending at DA Accounts','Pending at DA Accounts [Rejection]']
        self.cash_cols    = ['Pending at DA SCROLL', 'Pending at Dispatch', 'Pending at CHEQUE Alottment/Printing']
        self.pension_cols = ['Pending at E-Sign', 'Pending at AC Pension [Worksheet Generation]','Pending at DA Pension [Worksheet Generation]','Pending at DA Pension [SC worksheet generation]']

    def _resolve_report_path(self, filename):
        """Return the first existing path for a legacy .XLS or modern .xlsx report."""
        base = Path(self.directory_path)
        candidates = [filename]
        stem, dot, ext = filename.rpartition('.')
        if dot:
            candidates.append(f"{stem}.xlsx")
            candidates.append(f"{stem}.xls")
        for candidate in candidates:
            candidate_path = base / candidate
            if candidate_path.exists():
                return str(candidate_path)
        return str(base / filename)

    def _create_bins(self, df, col, bin_col):
        if col not in df.columns or df.empty:
            df[bin_col] = df.get(bin_col, pd.Series(dtype=object))
            return df
        df.loc[df[col].isin(self.rejection_cols), bin_col] = 'Rejection'
        df.loc[df[col].isin(self.approver_cols), bin_col] = 'Approver'
        df.loc[df[col].isin(self.da_cols), bin_col] = 'DA'
        df.loc[df[col].isin(self.cash_cols), bin_col] = 'Cash'
        df.loc[df[col].isin(self.pension_cols), bin_col] = 'Pension'
        return df     

    def _create_pending_bins(self, df, col):
        if col not in df.columns or df.empty:
            df['cat'] = df.get('cat', pd.Series(dtype=object))
            return df
        df.loc[df[col].between(0, 5, 'both'), 'cat'] = '0-5 Days'
        df.loc[df[col].between(6, 10, 'both'), 'cat'] = '6-10 Days'
        df.loc[df[col].between(11, 15, 'both'), 'cat'] = '11-15 Days'
        df.loc[df[col].between(16, 20, 'both'), 'cat'] = '16-20 Days'
        df.loc[df[col].between(20, 2000, 'right'), 'cat'] = 'More than 20 Days'
        return df

    def _style_map_func(self, value):
        color = ''
        if isinstance(value, (int, float)) and value < 65 and value > 7:
            intensity = 100+int(55 * (value / 50))  # Adjust intensity based on value
            color = f'rgb(255, {intensity}, {intensity})'  # Red with changing intensity
            weight = 'bold'
        else:
            color = f'rgb(255,255,255)'
            weight = 'normal'
        return f'background-color: {color};font-weight:{weight};'

    def _make_html(self, df, title_string='', classes='table table-bordered border-primary'):
        html = self.template % ("<h5>"+title_string+"</h5>"+
                           df.to_html(classes=classes,index=False))
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table')
        
        if table:
            num_columns = len(df.columns)
            table_width = min(100, num_columns * 20)  # Adjust the factor (20) as needed
            table['style'] = f"width: {table_width}%"
            
        for td in soup.find_all('td'):
            td["style"] = "font-size:9px;padding:2px;text-align:center;"
            
        for th in soup.find_all('th'):
            th["style"] = "font-size:9px;padding:2px;text-align:center;background:#ddd;"
            
        return str(soup)

    def _make_pdf(self, df, fname, title_string='', column_names=None):
        options = {
            'page-size': 'A4',
            'orientation': 'Portrait',
            'margin-top': '0.2in',
            'margin-right': '0.2in',
            'margin-bottom': '0.2in',
            'margin-left': '0.2in'
        }
        html_content = self._make_html(df, title_string)
        kwargs = {'options': options}
        if self.pdfkit_config is not None:
            kwargs['configuration'] = self.pdfkit_config
        pdfkit.from_string(html_content, fname, **kwargs)
        logger.info(f"Generated PDF: {fname}")

    def compare_claims(self, date1, date2, claim_file="claim.csv"):
        df1 = pd.read_csv(os.path.join(self.directory_path, date1, claim_file))
        df2 = pd.read_csv(os.path.join(self.directory_path, date2, claim_file))

        allowed_statuses = set(self.da_cols + self.approver_cols + self.rejection_cols)
        df1 = df1[df1['STATUS'].isin(allowed_statuses)]
        df2 = df2[df2['STATUS'].isin(allowed_statuses)]

        df3=df2.merge(df1, on='CLAIM ID', how='left')
        df3= df3[df3['STATUS_y'].isna()] 
        df3 = df3[['CLAIM ID','TASK ID_x','PENDING DAYS_x','STATUS_x','GROUP ID_x']]

        df3  = self._create_bins(df3,'STATUS_x',date2)
        df3  = self._create_pending_bins(df3,'PENDING DAYS_x')

        df4= pd.pivot_table(df3, values='CLAIM ID', index=['GROUP ID_x','TASK ID_x'], columns=[date2], 
                                 margins=True,
                                 aggfunc=lambda x: len(x),fill_value=0)
        df4 = df4.astype(int)
        df5 = df4.rename_axis(None, axis=1).reset_index()

        column_mapping = {
            'GROUP ID_x': 'GROUP',
            'TASK ID_x': 'TASK',
            'DA': date2,
            'All':'All'
        }
        
        df5 = df5.rename(columns=column_mapping)
        if date2 not in df5.columns:
            df5[date2] = 0
        df5 = df5[['GROUP','TASK',date2]]
        
        return df5

    def get_formatted_df(self, fname, cols=[], at=[]):
        df = pd.read_csv(fname)
        column_mapping1 = {
            'TRAN CLAIM ID': 'CLAIM ID',
            'ACC TASK ID': 'TASK ID',
        }
        if 'ACC TASK ID' in df.columns:
            df['GROUP ID'] = [int(str(x)[:3]) for x in df['ACC TASK ID']]
            column_title = 'tr_ins' # This variable is not used, consider removing or using it
        df = df.rename(columns=column_mapping1)
        if len(cols):
            df=df[cols]
            
        if len(at):
            df = df[df['STATUS'].isin(at)]
        return df

    def get_date_compared(self, date1, date2, file_name):
        allowed_statuses = set(self.da_cols + self.approver_cols + self.rejection_cols)
        df11 = self.get_formatted_df(os.path.join(self.directory_path, date1, file_name), cols=['CLAIM ID','TASK ID','GROUP ID','STATUS'], at=allowed_statuses)
        df21 = self.get_formatted_df(os.path.join(self.directory_path, date2, file_name), cols=['CLAIM ID','TASK ID','GROUP ID','STATUS'], at=allowed_statuses)

        diff = df11.merge(df21, on='CLAIM ID', how='left')
        diff = diff[diff['STATUS_y'].isna()]
        if diff.empty:
            return pd.DataFrame(columns=['GROUP','TASK', f"{file_name[:-4]}_{date1}"])

        pivot= pd.pivot_table(diff, values='CLAIM ID', index=['GROUP ID_x','TASK ID_x'], 
                                 margins=True,
                                 aggfunc=lambda x: len(x),fill_value=0)
        pivot = pivot.reset_index()
        column_mapping = {
            'GROUP ID_x': 'GROUP',
            'TASK ID_x': 'TASK',
            'CLAIM ID': file_name[:-4]+"_"+date1
        }
        pivot = pivot.rename(columns=column_mapping)
        return pivot

    def summarize_performance_excel(self, input_file, flag=0, mapping_file="mapping.xlsx"):
        df = pd.read_excel(input_file,header=None, skiprows=13)#, encoding= 'unicode_escape')
        df2 = df[df[9].notna()]
        if pd.api.types.is_numeric_dtype(df2[9]):
            mask_numeric = ~pd.isna(df2[9])
        else:
            mask_numeric = df2[9].astype(str).str.isnumeric()
        df3 = df2[mask_numeric]
        df4 = df3[[1,3,7,9,10,12,14,17,18,20,23,26,28,31,35]]
        i=0
        arr=[]
        for row_tup in df4.iterrows():
            row=row_tup[1]
            if pd.isnull(row[1]):
                if row[7]=="TOTAL-:":
                    prev = [prev[0],prev[1],row[9],row[10],row[12],row[14],row[17],row[18],row[20],row[23],row[26],row[28],row[31],row[35]]
            else:
                if i>0:
                    arr.append(prev)
                prev=[row[1],row[3],row[9],row[10],row[12],row[14],row[17],row[18],row[20],row[23],row[26],row[28],row[31],row[35]]
            i=i+1;
        df5 = pd.DataFrame(arr,columns = ['userid','Name','F19','F20','F31','13-in','13-out','14','10D','10c','5If','others','total','annexurek'])
        df5 = df5[df5.userid != "UNP SVR"]
        df5 = df5.astype({
                          'userid': 'int',
                          "F19": 'int',
                          "F20": 'int',
                          "F31": 'int',
                          "13-in": 'int',
                          "13-out": 'int',
                          "14": 'int',
                          '10D': 'int',
                          "5If": 'int',
                          "10c": 'int',
                          "others": 'int',
                          "total": 'int',
                          "annexurek": 'int'
        }, errors='ignore')
        if flag:
            df_map = pd.read_excel(mapping_file)
            df6 = pd.merge(left=df5, right=df_map, how='left',on='userid')
            df6 = df6.sort_values(['group','total'], ascending=[True,False])
        else:
            df6 = df5.sort_values(['total'], ascending=[False])
        return df6    

    def generate_performance_report(self):
        directory_names = [os.path.join(self.directory_path, name) for name in os.listdir(self.directory_path) if os.path.isdir(os.path.join(self.directory_path, name))]
        directory_names.sort() # Ensure chronological order

        dfs = []
        for index in range(len(directory_names)-1):
            date1 = os.path.basename(directory_names[index])
            date2 = os.path.basename(directory_names[index+1])
            
            title_string = date1+" - "+date2
            df = self.compare_claims(date2, date1) # Note: original script had date2, date1 order
            dfs.append(df.set_index(['GROUP','TASK']))
            out_pdf  = os.path.join(self.directory_path, date1+"_performance_da.pdf")
            self._make_pdf(df, out_pdf,title_string=title_string)

        if dfs:
            result = pd.concat(dfs, axis=1).fillna(0).astype(int).reset_index()
            result['TASK'] = result['TASK'].astype(str)
            result = result.sort_values('TASK')
            column_names=[name for name in result.columns if re.search(r"^\\d{4}", name)]
            try:
                styled_df = result.style.applymap(self._style_map_func, subset=column_names)
                export_frame = styled_df
            except AttributeError:
                export_frame = result
            self._make_pdf(export_frame, os.path.join(self.directory_path, os.path.basename(directory_names[-1])+"_summary.pdf"), title_string='Performance Summary', column_names=column_names)

        # Additional reports from performance.py
        file1 = self._resolve_report_path("Performance ReportDA.XLS")
        file2 = self._resolve_report_path("Performance AO.XLS")
        file3 = self._resolve_report_path("mapping.xlsx")

        if os.path.exists(file1):
            df1 = self.summarize_performance_excel(file1, flag=1, mapping_file=file3)
            self._make_pdf(df1, os.path.join(self.directory_path, "DA_performance_summary.pdf"), title_string="DA Performance")
        else:
            logger.warning(f"Performance ReportDA.XLS not found at {file1}")

        if os.path.exists(file2):
            df2 = self.summarize_performance_excel(file2, flag=0)
            self._make_pdf(df2, os.path.join(self.directory_path, "AO_performance_summary.pdf"), title_string="Approver Performance")
        else:
            logger.warning(f"Performance AO.XLS not found at {file2}")

        # Compare claims and tin for specific dates
        str1 = "2023_06_13"
        str2 = "2023_06_14"
        
        try:
            diff_t = self.get_date_compared(str1, str2, "tin.csv")
            diff_c = self.get_date_compared(str1, str2, "claim.csv")

            diff_t = diff_t.set_index(['GROUP', 'TASK'])
            diff_c = diff_c.set_index(['GROUP', 'TASK'])
            concatenated = pd.concat([diff_c, diff_t], axis=1)
            concatenated = concatenated.fillna(0).astype(int)
            concatenated = concatenated.reset_index()
            concatenated[str1] = concatenated['claim_'+str1] + concatenated['tin_'+str1]
            concatenated = concatenated.sort_values([str1])
            column_names=[name for name in concatenated.columns if re.search(r"^\\d{4}", name)]
            try:
                styled_df = concatenated.style.applymap(self._style_map_func, subset=column_names)
                export_concat = styled_df
            except AttributeError:
                export_concat = concatenated
            self._make_pdf(export_concat, os.path.join(self.directory_path, str1+"_summary.pdf"), title_string='Daily Comparison Summary', column_names=column_names)
        except Exception as e:
            logger.error(f"Error generating daily comparison report: {e}")
