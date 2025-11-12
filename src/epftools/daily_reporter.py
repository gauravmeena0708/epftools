import pandas as pd
import numpy as np
import os
import time
import logging
from pathlib import Path
from bs4 import BeautifulSoup
import pdfkit

logger = logging.getLogger(__name__)

class DailyReporter:
    """
    A class for generating daily reports from various EPF data sources.
    """

    STATUS_MAPPING  = {
        'Pending at DA Accounts'                          : 'DA',
        'Pending at DA Accounts [EDIT]'                   : 'DA',
        
        'Pending at Dispatch'                             : 'Other',
        'Pending at DA SCROLL'                            : 'Other',
        'Pending at CHEQUE Alottment/Printing'            : 'Other',
        'Pending [ Referred to Other Office ]'            : 'Other',
        
        'Pending at SS/AO/AC Accounts [Rejection]'        : 'Rejection',
        
        'Pending at SS/AO/AC Accounts'                    : 'App',
        'Pending [ Approver Pending ]'                    : 'App',

        'Pending at DA Pension [Worksheet Generation]'    : 'Other',
        'Pending at DA Pension [PPO Generation]'          : 'Other',
        'Pending at DA Pension [SC worksheet generation]' : 'Other',
        'Pending at E-Sign'                               : 'Other',
        'Pending at AC Pension [Worksheet Generation]'    : 'Other',
        'Pending at AC Pension [PPO Generation]'          : 'Other',
        'Pending at DA Pension [SC verification awaited]' : 'Other',
        'Pending at Invalid Status'                       : 'Other',
        'Pending at AC Pension [SC generation]'           : 'Other',
        'Pending at DA Pension [SC generation]'           : 'Other'
    }
    
    STATUS_MAPPING2  = {
        'Pending at DA Accounts'                          : '1-DA',
        'Pending at DA Accounts [EDIT]'                   : '1-DA',
        
        'Pending at Dispatch'                             : '4-Cash/scroll/cheque',
        'Pending at DA SCROLL'                            : '4-Cash/scroll/cheque',
        'Pending at CHEQUE Alottment/Printing'            : '4-Cash/scroll/cheque',
        
        
        'Pending at SS/AO/AC Accounts [Rejection]'        : '5-Rejection',
        
        'Pending at SS/AO/AC Accounts'                    : '2-Approver',
        'Pending [ Approver Pending ]'                    : '2-Approver',

        'Pending at DA Pension [SC generation]'           : '3-Pension',
        'Pending at DA Pension [Worksheet Generation]'    : '3-Pension',
        'Pending at DA Pension [PPO Generation]'          : '3-Pension',
        'Pending at DA Pension [SC worksheet generation]' : '3-Pension',
        'Pending at AC Pension [SC generation]'           : '3-Pension',
        'Pending at AC Pension [Worksheet Generation]'    : '3-Pension',
        'Pending at AC Pension [PPO Generation]'          : '3-Pension',
        'Pending at DA Pension [SC verification awaited]' : '3-Pension',
        'Pending [ Referred to Other Office ]'            : '3-Pension',
        'Pending at E-Sign'                               : '3-Pension',
        'Pending at Invalid Status'                       : '6-Other/Invalid'
    }

    def __init__(self, download_dir="downloads", template_path="templates/template.html", wkhtmltopdf_path="/path/to/wkhtmltopdf.exe"):
        self.download_dir = download_dir
        self.temp_dir = os.path.join(download_dir, "TEMP")
        os.makedirs(self.temp_dir, exist_ok=True)
        self.template = Path(template_path).read_text()
        self.wkhtmltopdf_path = wkhtmltopdf_path
        self.pdfkit_config = None
        try:
            path = "" if wkhtmltopdf_path == "/path/to/wkhtmltopdf.exe" else wkhtmltopdf_path
            self.pdfkit_config = pdfkit.configuration(wkhtmltopdf=path)
        except (OSError, FileNotFoundError) as exc:
            logger.warning("wkhtmltopdf not available (%s); PDF generation will rely on system defaults.", exc)

        self.file_paths = {
            "claim": os.path.join(self.download_dir, "Claim.csv"),
            "dsc": os.path.join(self.download_dir, "dsc.xlsx"),
            "esign": os.path.join(self.download_dir, "esign.xlsx"),
            "tin": os.path.join(self.download_dir, "tin.csv"),
            "online": os.path.join(self.download_dir, "online.xlsx"),
            "primary": os.path.join(self.download_dir, "primary.xlsx"),
            "others": os.path.join(self.download_dir, "others.xlsx"),
        }

    def _filter_and_rename(self, df, columns, rename_cols):
        df = df[columns]
        df1 = df.rename(columns=rename_cols)
        return df1

    def _create_bins(self, df):
        df.loc[df['GROUP ID'].isin([110, 111, 112, 113]), 'Officer'] = 'OFFICER_A'
        df.loc[df['GROUP ID'].isin([106, 107, 109, 114]), 'Officer'] = 'OFFICER_B'
        df.loc[df['GROUP ID'].isin([104, 105, 108, 188]), 'Officer'] = 'OFFICER_C'
        df.loc[df['GROUP ID'].isin([101, 102, 103]), 'Officer'] = 'OFFICER_D'
        return df

    def _pending_bins(self, df, num=2):
        if num == 2:
            df.loc[df['PENDING DAYS'].between(0, 20, 'both'), 'cat'] = 'Upto 20 Days'
            df.loc[df['PENDING DAYS'].between(20, 2000, 'right'), 'cat'] = 'More than 20 Days'
        elif num == 3:
            df.loc[df['PENDING DAYS'].between(0, 15, 'both'), 'cat'] = '<=15 Days'
            df.loc[df['PENDING DAYS'].between(16, 20, 'both'), 'cat'] = '16-20 Days'
            df.loc[df['PENDING DAYS'].between(20, 3000, 'right'), 'cat'] = '>20 Days'
        elif num == 4:
            df.loc[df['PENDING DAYS'].between(0, 10, 'both'), 'cat'] = '<=10 Days'
            df.loc[df['PENDING DAYS'].between(10, 5000, 'right'), 'cat'] = '>10 Days'
        else:
            df.loc[df['PENDING DAYS'].between(0, 20, 'both'), 'cat'] = '<=20 Days'
            df.loc[df['PENDING DAYS'].between(21, 100, 'both'), 'cat'] = '21-100 Days'
            df.loc[df['PENDING DAYS'].between(100, 5000, 'right'), 'cat'] = '>100 Days'
        return df

    def _status_bin_modify(self, df):
        set1 = ['Pending at DA Accounts','Pending at DA Accounts [EDIT]']
        set2 = ['Pending at Dispatch','Pending at DA SCROLL','Pending at CHEQUE Alottment/Printing','Pending [ Referred to Other Office ]']
        set3 = ['Pending at SS/AO/AC Accounts [Rejection]']
        set4 = ['Pending at SS/AO/AC Accounts','Pending [ Approver Pending ]']
        set5 = ['Pending at DA Pension [Worksheet Generation]','Pending at DA Pension [PPO Generation]',
                     'Pending at DA Pension [SC worksheet generation]','Pending at E-Sign',
                    'Pending at AC Pension [Worksheet Generation]','Pending at AC Pension [PPO Generation]']

        df['STATUS'] = df['STATUS'].replace(to_replace=set1,value="DA(Includes NTE)")
        df['STATUS'] = df['STATUS'].replace(to_replace=set2,value="Dispatch/Cash/Scroll")
        df['STATUS'] = df['STATUS'].replace(to_replace=set3,value="Rejection")
        df['STATUS'] = df['STATUS'].replace(to_replace=set4,value="Approver")
        df['STATUS'] = df['STATUS'].replace(to_replace=set5,value="Pension")
        return df

    def _get_pivot_table(self, df, index_col, column_col, values_col, aggfunc='count'):
        if df.empty:
            return pd.DataFrame()
        pivot = pd.pivot_table(df, values=values_col, index=index_col, columns=column_col,
                               margins=True, aggfunc=aggfunc).fillna(0).astype(int)
        return pivot

    def _load_claim_data(self, file_path):
        df = pd.read_csv(file_path)
        df['TASK ID'] = df['TASK ID'].astype(float).astype("Int32")
        df['TASK ID'] = df['TASK ID'].fillna(10100)
        df['GROUP ID'] = [int(str(x)[:3]) for x in df['TASK ID']]
        df = self._status_bin_modify(df)
        df = self._create_bins(df)
        df = self._pending_bins(df)
        return df

    def _load_dsc_esign_data(self, file_path):
        df = pd.read_excel(file_path, skiprows=1)
        if 'ACC TASK ID' not in df.columns:
            df = pd.read_excel(file_path)
        df.rename(columns = {'EST ID':'EST_ID','ACC TASK ID':'Pending With','PENDING AT (DESIG)':'desig'}, inplace = True)
        if 'PENDING DAYS' not in df.columns:
            df['PENDING DAYS'] = 0
        df['TASK ID'] = [int(str(x)[-5:]) for x in df['Pending With']]
        df['GROUP ID'] = [int(str(x)[:3]) for x in df['TASK ID']]
        df['desig']=df['desig'].replace("RPFC", "RPFC/APFC")
        df['desig']=df['desig'].replace("APFC", "RPFC/APFC")
        df = self._create_bins(df)
        df = self._pending_bins(df)
        return df

    def _load_online_primary_others_data(self, file_path):
        df = pd.read_excel(file_path, skiprows=1)
        if 'MEMBER ID' not in df.columns:
            df = pd.read_excel(file_path)
        columns=['MEMBER ID','PENDING DAYS','A/C GROUP','DESIGNATION']
        rename_cols={'MEMBER ID':'Basic','DESIGNATION':'desig'}
        df=self._filter_and_rename(df,columns, rename_cols)
        df['GROUP ID'] = [int(str(x)[-3:]) for x in df['A/C GROUP']]
        df['TASK ID'] = [str(x)+'00-sum' for x in df['GROUP ID']]
        df = self._create_bins(df)
        df = self._pending_bins(df)
        return df

    def _load_tin_data(self, file_path):
        df = pd.read_csv(file_path)
        df['ACC TASK ID'] = df['ACC TASK ID'].astype(float).astype("Int32")
        df['ACC TASK ID'] = df['ACC TASK ID'].fillna(10100)
        df['GROUP ID'] = [int(str(x)[:3]) for x in df['ACC TASK ID']]
        df = self._status_bin_modify(df)
        df = self._create_bins(df)
        df = self._pending_bins(df,5)
        return df

    def consolidate_data(self):
        self.df_claim = self._load_claim_data(self.file_paths["claim"])
        self.df_dsc = self._load_dsc_esign_data(self.file_paths["dsc"])
        self.df_esign = self._load_dsc_esign_data(self.file_paths["esign"])
        self.df_online = self._load_online_primary_others_data(self.file_paths["online"])
        self.df_primary = self._load_online_primary_others_data(self.file_paths["primary"])
        self.df_others = self._load_online_primary_others_data(self.file_paths["others"])
        self.df_tin = self._load_tin_data(self.file_paths["tin"])

        logger.info("Data consolidated from multiple sources.")

    def _highlight(self, df, val=0):
        # This is a simplified version of the highlight function from dailyreport.py
        # It assumes df_claim4 is available, which might not be the case in a modular setup.
        # A more robust implementation would pass styling parameters or a styling function.
        if val == 0:
            try:
                return df.style.applymap(lambda x: 'font-weight: bold; border: 1px solid;')
            except AttributeError:
                return df
        else:
            try:
                return df.style.applymap(lambda x: 'font-weight: bold; background-color: orange;border: 1px solid;' 
                                         if (isinstance(x, (int, float)) and x > val) else 'border: 1px solid;')
            except AttributeError:
                return df

    def generate_daily_report(self):
        self.consolidate_data()

        # Pivot tables from dailyreport.py
        self.df_claim_pivot1 = self._get_pivot_table(self.df_claim, index_col='cat', column_col=["Officer","GROUP ID"], values_col='CLAIM ID')
        self.df_claim_pivot2 = self._get_pivot_table(self.df_claim, index_col='STATUS', column_col=["Officer","GROUP ID"], values_col='CLAIM ID')
        self.df_claim_pivot3 = self._get_pivot_table(self.df_claim[self.df_claim['PENDING DAYS'] > 20], index_col='STATUS', column_col=["Officer","GROUP ID"], values_col='CLAIM ID')
        self.df_claim_pivot4 = self._get_pivot_table(self.df_claim[self.df_claim['STATUS'] == 'DA(Includes NTE)'], index_col=["GROUP ID",'TASK ID'], column_col=["cat"], values_col='CLAIM ID')

        self.df_dsc_pivot = self._get_pivot_table(self.df_dsc, index_col=['cat','desig'], column_col=["Officer","GROUP ID"], values_col='EST_ID')
        self.df_esign_pivot = self._get_pivot_table(self.df_esign, index_col=['cat','desig'], column_col=["Officer","GROUP ID"], values_col='EST_ID')

        self.df_online_pivot = self._get_pivot_table(self.df_online, index_col=['cat','desig'], column_col=["Officer","GROUP ID"], values_col='Basic')
        self.df_primary_pivot = self._get_pivot_table(self.df_primary, index_col=['cat','desig'], column_col=["Officer","GROUP ID"], values_col='Basic')
        self.df_others_pivot = self._get_pivot_table(self.df_others, index_col=['cat','desig'], column_col=["Officer","GROUP ID"], values_col='Basic')

        self.df_tin_pivot1 = self._get_pivot_table(self.df_tin, index_col='cat', column_col=["Officer","GROUP ID"], values_col='TRAN CLAIM ID')
        self.df_tin_pivot2 = self._get_pivot_table(self.df_tin, index_col='STATUS', column_col=["Officer","GROUP ID"], values_col='TRAN CLAIM ID')
        self.df_tin_pivot3 = self._get_pivot_table(self.df_tin[self.df_tin['PENDING DAYS'] > 20], index_col='STATUS', column_col=["Officer","GROUP ID"], values_col='TRAN CLAIM ID')
        self.df_tin_pivot4 = self._get_pivot_table(self.df_tin[self.df_tin['STATUS'].isin(["Pending at DA","Pending at SS"])], index_col=["GROUP ID",'TASK ID'], column_col=["STATUS", "cat"], values_col='TRAN CLAIM ID')

        logger.info("Pivot tables and summaries created.")

        parts = [
            "<h5>Claim Pendency</h5>" + self._highlight(self.df_claim_pivot1, 5000).to_html(),
            "<h5>Claim Pendency (at each level)</h5>" + self._highlight(self.df_claim_pivot2, 5000).to_html(),
            "<h5>Claim Pendency (at each level >20days)</h5>" + self._highlight(self.df_claim_pivot3, 5).to_html(),
            "<h5>Transfer In Pendency</h5>" + self._highlight(self.df_tin_pivot1, 1000).to_html(),
            "<h5>Transfer In (at each level)</h5>" + self._highlight(self.df_tin_pivot2, 1000).to_html(),
            "<h5>Transfer In (at each level >20days)</h5>" + self._highlight(self.df_tin_pivot3, 1000).to_html(),
            "<div class='pagebreak' style=\"break-after:page\"></div>",
            "<h5>Online Change Pendency</h5>" + self._highlight(self.df_online_pivot, 50).to_html(),
            "<h5>Primary Change Pendency</h5>" + self._highlight(self.df_primary_pivot, 50).to_html(),
            "<h5>Other Change Pendency</h5>" + self._highlight(self.df_others_pivot, 10).to_html(),
            "<h5>DSC Pendency</h5>" + self._highlight(self.df_dsc_pivot, 50).to_html(),
            "<h5>E-Sign Pendency</h5>" + self._highlight(self.df_esign_pivot, 50).to_html(),
            "<div class='pagebreak' style=\"break-after:page\"></div>",
            "<h5>DA wise Pendency(Pending at DA or NTE)</h5>" + self._highlight(self.df_claim_pivot4).to_html(),
            "<br/>",
            "<h5>DA wise NEFT Transfer in Pendency</h5>" + self._highlight(self.df_tin_pivot4, 20).to_html(),
            "<br/>",
        ]
        html_report_content = "".join(parts)

        out_html_path = os.path.join(self.temp_dir, "report_" + time.strftime("%Y_%m_%d") + ".html")
        formatted_html = self._make_html(html_report_content)
        with open(out_html_path, 'w') as _file:
            _file.write(formatted_html)
        logger.info(f"HTML report generated: {out_html_path}")

        # Convert HTML to PDF
        out_pdf_path = os.path.join(self.download_dir, "report_" + time.strftime("%Y_%m_%d") + ".pdf")
        self._make_pdf(formatted_html, out_pdf_path)
        logger.info(f"PDF report generated: {out_pdf_path}")

    def _make_html(self, html_content, classes='table table-sm table-bordered border-primary d-print-table fs-6'):
        # This method now takes html_content directly, assuming it's already formatted with tables
        soup = BeautifulSoup(html_content, 'html.parser')
        for table in soup.find_all('table'):
            table["class"] = classes
        for td in soup.find_all('td'):
            td["style"] = "font-size:10px;padding:2px;text-align:center;" 
        for th in soup.find_all('th'):
            th["style"] = "font-size:10px;padding:2px;text-align:center;"
        return str(soup)

    def _make_pdf(self, html_content, output_path, options=None):
        if options is None:
            options = {
                'page-size': 'A4',
                'margin-top': '0.2in',
                'margin-right': '0.2in',
                'margin-bottom': '0.2in',
                'margin-left': '0.2in'
            }
        kwargs = {'options': options}
        if self.pdfkit_config is not None:
            kwargs['configuration'] = self.pdfkit_config
        pdfkit.from_string(html_content, output_path, **kwargs)
        logger.info(f"Generated PDF: {output_path}")
