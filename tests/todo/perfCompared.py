import os, re, time
import pdfkit
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup


directory_path = 'reports/'
rejection_cols = ['Pending at SS/AO/AC Accounts [Rejection]']
approver_cols = ['Pending [ Approver Pending ]', 'Pending at SS/AO/AC Accounts']
da_cols      = ['Pending at DA','Pending at DA Accounts [EDIT]', 'Pending at DA Accounts','Pending at DA Accounts [Rejection]']
cash_cols    = ['Pending at DA SCROLL', 'Pending at Dispatch', 'Pending at CHEQUE Alottment/Printing']
pension_cols = ['Pending at E-Sign', 'Pending at AC Pension [Worksheet Generation]','Pending at DA Pension [Worksheet Generation]','Pending at DA Pension [SC worksheet generation]']


template = Path('templates/template.html').read_text()
path_to_wkhtmltopdf = r'/path/to/wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)
column_name = 'processed_at_DA'

def style_map_func(value):
    color = ''
    if value < 65 and value > 7:
        intensity = 100+int(55 * (value / 50))  # Adjust intensity based on value
        color = f'rgb(255, {intensity}, {intensity})'  # Red with changing intensity
        weight = 'bold'
    else:
        color = f'rgb(255,255,255)'
        weight = 'normal'
    return f'background-color: {color};font-weight:{weight};'
    
def make_html(df,fname,title_string=''):
    classes = 'table table-bordered border-primary'# d-print-table table-sm fs-6'
    html = template % ("<h5>Processed at DA level: "+title_string+" </h5>"+
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
    
def make_pdf(df, fname,column_names,title_string=''):
    options = {
        'page-size': 'A4',
        'orientation': 'Portrait',
        'margin-top': '0.2in',
        'margin-right': '0.2in',
        'margin-bottom': '0.2in',
        'margin-left': '0.2in'
    }
    html = make_html(df,fname,title_string)
    pdfkit.from_string(html,fname, options=options,configuration=config)
    print(fname+" generated.")
    
    

def create_bins(df,col,bin_col):
    df.loc[df[col].isin(rejection_cols), bin_col] = 'Rejection'
    df.loc[df[col].isin(approver_cols), bin_col] = 'Approver'
    df.loc[df[col].isin(da_cols), bin_col] = 'DA'
    df.loc[df[col].isin(cash_cols), bin_col] = 'Cash'
    df.loc[df[col].isin(pension_cols), bin_col] = 'Pension'
    return df     

def create_pending_bins(df,col):
    df.loc[df[col].between(0, 5, 'both'), 'cat'] = '0-5 Days'
    df.loc[df[col].between(6, 10, 'both'), 'cat'] = '6-10 Days'
    df.loc[df[col].between(11, 15, 'both'), 'cat'] = '11-15 Days'
    df.loc[df[col].between(16, 20, 'both'), 'cat'] = '16-20 Days'
    df.loc[df[col].between(20, 2000, 'right'), 'cat'] = 'More than 20 Days'
    return df



# Load the two DataFrames
def compare_claims(path, date1, date2):
    df1 = pd.read_csv(path+date1+"\\claim.csv") #later date
    df2 = pd.read_csv(path+date2+"\\claim.csv") #earlier date
    df1 = df1[df1['STATUS'].isin(da_cols)]
    df2 = df2[df2['STATUS'].isin(da_cols)]

    df3=df2.merge(df1, on='CLAIM ID', how='left')
    df3= df3[df3['STATUS_y'].isna()] 
    df3 = df3[['CLAIM ID','TASK ID_x','PENDING DAYS_x','STATUS_x','GROUP ID_x']]

    df3  = create_bins(df3,'STATUS_x',date2)
    df3  = create_pending_bins(df3,'PENDING DAYS_x')

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
    
    df5 = df5.rename(columns=column_mapping)[['GROUP','TASK',date2]]
    
    return df5


directory_names = [directory_path+name for name in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, name))]
directory_names


dfs = []
for index in range(len(directory_names)-1):
    date1 = directory_names[index][-10:]
    date2 = directory_names[index+1][-10:]
    
    title_string = date1+" - "+date2
    df = compare_claims(directory_path, date2,date1)
    dfs.append(df.set_index(['GROUP','TASK']))
    out_pdf  = directory_path +"\\"+date1+"_performance_da.pdf"
    make_pdf(df, out_pdf,title_string=title_string, column_names=[date1])

result = pd.concat(dfs, axis=1).fillna(0).astype(int).reset_index()
result['TASK'] = result['TASK'].astype(str)
result = result.sort_values('TASK')
column_names=[name for name in result.columns if re.search(r"\d{4}", name)]
styled_df = result.style.applymap(style_map_func, subset=column_names)
make_pdf(styled_df, directory_names[-1][-10:]+"_summary.pdf",title_string='',column_names=column_names )



cols = ['CLAIM ID','TASK ID','GROUP ID','STATUS']
def get_formatted_df(fname, cols=[],at=[]):
    df = pd.read_csv(fname)
    column_mapping1 = {
        'TRAN CLAIM ID': 'CLAIM ID',
        'ACC TASK ID': 'TASK ID',
    }
    if 'ACC TASK ID' in df.columns:
        df['GROUP ID'] = [int(str(x)[:3]) for x in df['ACC TASK ID']]
        column_title = 'tr_ins'
    df = df.rename(columns=column_mapping1)
    if len(cols):
        df=df[cols]
        
    if len(at):
        df = df[df['STATUS'].isin(at)]
    return df

def get_date_compared(directory_path,date1, date2,fname):
    df11 = get_formatted_df(directory_path+date1+"\\"+fname,cols,da_cols)
    df21 = get_formatted_df(directory_path+date2+"\\"+fname,cols,da_cols)

    diff = df11.merge(df21, on='CLAIM ID', how='left')
    diff = diff[diff['STATUS_y'].isna()]
    
    pivot= pd.pivot_table(diff, values='CLAIM ID', index=['GROUP ID_x','TASK ID_x'], 
                             margins=True,
                             aggfunc=lambda x: len(x),fill_value=0)
    pivot = pivot.reset_index()
    column_mapping = {
        'GROUP ID_x': 'GROUP',
        'TASK ID_x': 'TASK',
        'CLAIM ID': fname[:-4]+"_"+date1
    }
    pivot = pivot.rename(columns=column_mapping)
    return pivot

str1 = "2023_06_13"
str2 = "2023_06_14"
diff_t = get_date_compared(directory_path,str1, str2,"tin.csv")
diff_c = get_date_compared(directory_path,str1, str2,"claim.csv")
diff_t = diff_t.set_index(['GROUP', 'TASK'])
diff_c = diff_c.set_index(['GROUP', 'TASK'])
concatenated = pd.concat([diff_c, diff_t], axis=1)
concatenated = concatenated.fillna(0).astype(int)
concatenated = concatenated.reset_index()
concatenated[str1] = concatenated['claim_'+str1] + concatenated['tin_'+str1]
concatenated = concatenated.sort_values([str1])
column_names=[name for name in concatenated.columns if re.search(r"^\d{4}", name)]
styled_df = concatenated.style.applymap(style_map_func, subset=column_names)
make_pdf(styled_df, str1+"_summary.pdf",title_string='',column_names=column_names )