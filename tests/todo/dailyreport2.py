import pandas as pd
options = {
    'page-size': 'A4',
    'margin-top': '0.2in',
    'margin-right': '0.2in',
    'margin-bottom': '0.2in',
    'margin-left': '0.2in',
    'orientation':'Landscape',
    'dpi':300
}

  
def filter_and_rename(df,columns, rename_cols):
    df=df[columns]
    df1 = df.rename(columns = rename_cols)
    return df1

cols1 = ['CLAIM ID', 'MEMBER ID', 'RECEIPT DATE','CLAIM TYPE','AUTO/MANUAL', 'TASK ID', 'PENDING DAYS',
       'STATUS', 'DEATH CASE','GROUP ID']
cols2 = ['NEW MEMBER ID','ACC TASK ID',
       'OLD MEMBER ID', 'TRAN CLAIM ID', 'STATUS', 'TOTAL AMOUNT',
       'TRANSFER TYPE',  'SLIP TYPE', 'PENDING DAYS']

columns=['UAN','MEMBER ID','PENDING DAYS','A/C GROUP','DESIGNATION']
rename_cols={'MEMBER ID':'Mem ID','DESIGNATION':'Designation','A/C GROUP':'GROUP ID'}
    
    
def make_pdf(df,fname):
    config = pdfkit.configuration(wkhtmltopdf='/path/to/wkhtmltopdf.exe')
    if 'CLAIM TYPE' in df.columns:
        df['CLAIM TYPE'] = df['CLAIM TYPE'].map(lambda x: x[:7])
    html = template % ("<h5>"+fname[:-4]+"</h5>"+df.to_html(classes=classes))
    soup = BeautifulSoup(html, 'html.parser')
    for td in soup.find_all('td'):
        td["style"] = "font-size:10px;padding:2px;text-align:center;"
    for th in soup.find_all('th'):
        th["style"] = "font-size:10px;padding:2px;text-align:center;" 
    pdfkit.from_string(str(soup),fname, options=options,configuration=config)
    print(fname+" generated.")

df1 = pd.read_csv(file1)
df1 = filter_and_rename(df1,cols1,{})
df1 = df1.sort_values(by=['PENDING DAYS', 'TASK ID', 'STATUS'], ascending=False)
df2 = pd.read_csv(file5)
df2 = filter_and_rename(df2,cols2,{'ACC TASK ID':'TASK ID'})
df2 = df2.sort_values(by=['PENDING DAYS', 'TASK ID'], ascending=False)
df3 = pd.read_excel(file6,skiprows=1)
df3  = filter_and_rename(df3,columns, rename_cols)
df4 = pd.read_excel(file7,skiprows=1)
df4=filter_and_rename(df4,columns, rename_cols)

cf1= df1[df1['STATUS'].isin(set2)].reset_index(drop=True)                   #settled but pending at scroll or cheque allotment
cf2= df1[df1['DEATH CASE']=='DEATH CASE'].sort_values(by=['TASK ID']).reset_index(drop=True)           #death Case
cf3= df1[df1['STATUS'].isin(set5)].reset_index(drop=True)                  #pending at pension
cf4= df1[df1['STATUS'].isin(set3)].reset_index(drop=True)                  #Pending at rejection
cf5= df1[df1['STATUS'].isin(set4)].reset_index(drop=True)                  #Pending at approver
cf6= df1[df1['PENDING DAYS'] >=20].sort_values(by=['TASK ID','PENDING DAYS']).reset_index(drop=True)  #>20 days pendency
cfx= df1[df1['STATUS'].isin(set1)].reset_index(drop=True)                  #DA and NTE
cfx1= df1[(df1['STATUS'].isin(set6)) & (df1['PENDING DAYS'] >=18)].reset_index(drop=True)    

cf7= cfx[cfx['PENDING DAYS'].isin([17,18,19])].sort_values(by=['TASK ID','PENDING DAYS']).reset_index(drop=True)
cf8= cfx[cfx['PENDING DAYS'].isin([13,14,15,16])].sort_values(by=['TASK ID','PENDING DAYS']).reset_index(drop=True)

cf9 = df2[df2['PENDING DAYS']>=20].sort_values(by=['TASK ID','PENDING DAYS']).reset_index(drop=True)
cf10 = df3[df3['PENDING DAYS']>=20].sort_values(by=['GROUP ID','PENDING DAYS']).reset_index(drop=True)
cf11 = df4[df4['PENDING DAYS']>=20].sort_values(by=['GROUP ID','PENDING DAYS']).reset_index(drop=True)
cf12 = pd.pivot_table(cfx, values='CLAIM ID', index=["GROUP ID"], columns=["PENDING DAYS"], margins=True, aggfunc=lambda x: len(x),fill_value=0)
cf13 = pd.pivot_table(cfx1, values='CLAIM ID', index=["GROUP ID"], columns=["STATUS"], margins=True, aggfunc=lambda x: len(x),fill_value=0)

with pd.ExcelWriter(out_xlsx, engine="xlsxwriter") as writer:
    # Write the dataframes to the worksheets
    cf1.to_excel(writer, sheet_name='Pending at Cash-Scroll')
    make_pdf(cf1, "Claims pending at Cash-Scroll.pdf")
    cf2.to_excel(writer, sheet_name='Pending Death Cases')
    make_pdf(cf2, "Claims pending Death cases.pdf")
    cf3.to_excel(writer, sheet_name='Pending at Pension')
    make_pdf(cf3, "Claims pending at Pension.pdf")
    cf4.to_excel(writer, sheet_name='Pending at Rejection')
    make_pdf(cf4, "Claims pending at Rejection.pdf")
    cf5.to_excel(writer, sheet_name='Pending at Approver')
    make_pdf(cf5, "Claims pending at approver.pdf")
    cf6.to_excel(writer, sheet_name='Pending >=20 days')
    make_pdf(cf6, "Claims pending 20 days.pdf")
    cf7.to_excel(writer, sheet_name='Pending for 17-19')
    make_pdf(cf7, "Claims pending for 17-19 days.pdf")
    cf8.to_excel(writer, sheet_name='Pending for 13-16')
    make_pdf(cf8, "Claims pending for 13-16 days.pdf")
    cf9.to_excel(writer, sheet_name='Transfer in Pending for >20')
    make_pdf(cf9, "Transfer in pending for 20 days.pdf")
    cf10.to_excel(writer, sheet_name='Online Pending for 20 days')
    make_pdf(cf10, "Online Pending for 20 days.pdf")
    cf11.to_excel(writer, sheet_name='Primary Pending for 20 days')
    make_pdf(cf11, "Primary Pending for 20 days.pdf")
    cf12.to_excel(writer, sheet_name='daywise at DA')
    make_pdf(cf12, "DAY wise pendency at DA.pdf")
    cf13.to_excel(writer, sheet_name='pending for 18 and above')
    make_pdf(cf12, "pending for 18 and above.pdf")

print("All files completed")