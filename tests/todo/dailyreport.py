import pandas as pd
from pathlib import Path
import numpy as np
from numpy.random import randn
import matplotlib.pyplot as plt
from pathlib import Path
import pdfkit
import time
import os
from bs4 import BeautifulSoup


DIR = "downloads"


DOWNLOAD_DIR = "downloads/2023_04_05" #DIR +time.strftime("%Y_%m_%d") #Change your directory here


TEMP     =DOWNLOAD_DIR+"/TEMP"


os.makedirs(TEMP, exist_ok=True)





file1    =DOWNLOAD_DIR+"/"+"Claim.csv"


file3    =DOWNLOAD_DIR+"/"+"dsc.xlsx"


file4    =DOWNLOAD_DIR+"/"+"esign.xlsx"


file5    =DOWNLOAD_DIR+"/"+"tin.csv"


file6    =DOWNLOAD_DIR+"/"+"online.xlsx"


file7    =DOWNLOAD_DIR+"/"+"primary.xlsx"


file8    =DOWNLOAD_DIR+"/"+"others.xlsx"





options = {


    'page-size': 'A4',


    'margin-top': '0.2in',


    'margin-right': '0.2in',


    'margin-bottom': '0.2in',


    'margin-left': '0.2in'


}


classes = 'table table-sm table-bordered border-primary d-print-table fs-6'





out_html =TEMP+"/"+"out.html"


out_pdf  =DOWNLOAD_DIR+"/"+"report_"+time.strftime("%Y_%m_%d")+".pdf" 


out_xlsx =DOWNLOAD_DIR+"/"+"merged_"+time.strftime("%Y_%m_%d")+".xlsx"


template=Path(DIR+'/template.html').read_text()








set1 = ['Pending at DA Accounts','Pending at DA Accounts [EDIT]']


set2 = ['Pending at Dispatch','Pending at DA SCROLL','Pending at CHEQUE Alottment/Printing','Pending [ Referred to Other Office ]']


set3 = ['Pending at SS/AO/AC Accounts [Rejection]']


set4 = ['Pending at SS/AO/AC Accounts','Pending [ Approver Pending ]']


set5 = ['Pending at DA Pension [Worksheet Generation]','Pending at DA Pension [PPO Generation]',


             'Pending at DA Pension [SC worksheet generation]','Pending at E-Sign',


            'Pending at AC Pension [Worksheet Generation]','Pending at AC Pension [PPO Generation]']


set6 = ['Pending at DA Accounts','Pending at DA Accounts [EDIT]','Pending at SS/AO/AC Accounts']





def process(x):


    y=str(x)[-3:]


    try:


        return int(y)


    except:


        return 100


    


def filter_and_rename(df,columns, rename_cols):


    df=df[columns]


    df1 = df.rename(columns = rename_cols)


    return df1











def create_bins(df):


    df.loc[df['GROUP ID'].isin([110,111,112, 113]), 'Officer'] = 'GM'


    df.loc[df['GROUP ID'].isin([106,107,109, 114]), 'Officer'] = 'NK'


    df.loc[df['GROUP ID'].isin([104,105,108, 188]), 'Officer'] = 'VK'


    df.loc[df['GROUP ID'].isin([101,102,103]), 'Officer'] = 'SR'


    return df





def pending_bins(df,num=2):


    if num==2:


        df.loc[df['PENDING DAYS'].between(0, 20, 'both'), 'cat'] = 'Upto 20 Days'


        df.loc[df['PENDING DAYS'].between(20, 2000, 'right'), 'cat'] = 'More than 20 Days'


    elif num==3:


        df.loc[df['PENDING DAYS'].between(0, 15, 'both'), 'cat'] = '<=15 Days'


        df.loc[df['PENDING DAYS'].between(16, 20, 'both'), 'cat'] = '16-20 Days'


        df.loc[df['PENDING DAYS'].between(20, 3000, 'right'), 'cat'] = '>20 Days'


    elif num ==4:


        df.loc[df['PENDING DAYS'].between(0, 10, 'both'), 'cat'] = '<=10 Days'


        df.loc[df['PENDING DAYS'].between(10, 5000, 'right'), 'cat'] = '>10 Days'


    else:


        df.loc[df['PENDING DAYS'].between(0, 20, 'both'), 'cat'] = '<=20 Days'


        df.loc[df['PENDING DAYS'].between(21, 100, 'both'), 'cat'] = '21-100 Days'


        df.loc[df['PENDING DAYS'].between(100, 5000, 'right'), 'cat'] = '>100 Days'


    return df





def status_bin_modify(df):


    df['STATUS'] = df['STATUS'].replace(to_replace=set1,value="DA(Includes NTE)")


    df['STATUS'] = df['STATUS'].replace(to_replace=set2,value="Dispatch/Cash/Scroll")


    df['STATUS'] = df['STATUS'].replace(to_replace=set3,value="Rejection")


    df['STATUS'] = df['STATUS'].replace(to_replace=set4,value="Approver")


    df['STATUS'] = df['STATUS'].replace(to_replace=set5,value="Pension")


    return df


    


def get_pivot1(file,name="Unnammed"):


    df = pd.read_excel(file,skiprows=1)





    df.rename(columns = {'EST ID':name,'ACC TASK ID':'Pending With','PENDING AT (DESIG)':'desig'}, inplace = True)


    df['TASK ID'] = [int(str(x)[-5:]) for x in df['Pending With']]


    df['GROUP ID'] = [int(str(x)[:3]) for x in df['TASK ID']]


    df['desig']=df['desig'].replace("RPFC", "RPFC/APFC")


    df['desig']=df['desig'].replace("APFC", "RPFC/APFC")


    





    


    df = create_bins(df)


    df = pending_bins(df)


    


    df_pivot= pd.pivot_table(df, values=name, index=['cat','desig'], columns=["Officer","GROUP ID"],


                    margins=True,


                    aggfunc=lambda x: len(x),dropna=True)


    df_pivot=df_pivot.fillna(0)


    df_pivot = df_pivot.astype(int)


    return df_pivot





def get_pivot2(file,name="Unnammed"):


    df = pd.read_excel(file,skiprows=1)


    columns=['MEMBER ID','PENDING DAYS','A/C GROUP','DESIGNATION']


    rename_cols={'MEMBER ID':'Basic','DESIGNATION':'desig'}


    df=filter_and_rename(df,columns, rename_cols)


    df['GROUP ID'] = [process(x) for x in df['A/C GROUP']]


    df['TASK ID'] = [str(x)+'00-sum' for x in df['GROUP ID']]





    df = create_bins(df)


    df = pending_bins(df)


    


    df_pivot= pd.pivot_table(df, values='Basic', index=['cat','desig'],columns=["Officer","GROUP ID"],


                             margins=True,


                             aggfunc=lambda x: len(x))


    df_pivot=df_pivot.fillna(0)


    df_pivot = df_pivot.astype(int)


    return df_pivot





def get_pivot3(file,name="Unnamed",col1="ACC TASK ID",col2="TRAN CLAIM ID"):


    df = pd.read_csv(file)


    df[col1]=df[col1].astype(float).astype("Int32")


    df[col1]=df[col1].fillna(10100)


    columns=[col2,col1,'PENDING DAYS','STATUS']


    


    rename_cols={col2:'TINs',col1:'TASK ID'}


    df=filter_and_rename(df,columns, rename_cols)


    df['GROUP ID'] = [int(str(x)[:3]) for x in df['TASK ID']]


    


    df = create_bins(df)


    df = pending_bins(df,2)


    





    df_pivot= pd.pivot_table(df, values='TINs', index=['cat'], columns=["Officer","GROUP ID"], 


                             margins=True,


                             aggfunc=lambda x: len(x))


    


    df_pivot=df_pivot.fillna(0)


    df_pivot = df_pivot.astype(int)


    return df_pivot





def get_pivot7(file,name="Unnamed",col1="ACC TASK ID",col2="TRAN CLAIM ID"):


    df = pd.read_csv(file)


    df[col1]=df[col1].astype(float).astype("Int32")


    df[col1]=df[col1].fillna(10100)


    columns=[col2,col1,'PENDING DAYS','STATUS']


    


    rename_cols={col2:'TINs',col1:'TASK ID'}


    df=filter_and_rename(df,columns, rename_cols)


    df['GROUP ID'] = [int(str(x)[:3]) for x in df['TASK ID']]


    


    df = create_bins(df)


    df = pending_bins(df,5)


    





    df_pivot= pd.pivot_table(df, values='TINs', index=['cat'], columns=["Officer","GROUP ID"], 


                             margins=True,


                             aggfunc=lambda x: len(x))


    


    df_pivot=df_pivot.fillna(0)


    df_pivot = df_pivot.astype(int)


    return df_pivot





def get_pivot4(file,num=0, name="Unnamed", col1="ACC TASK ID",col2="TRAN CLAIM ID"):


    df = pd.read_csv(file)


    df[col1]=df[col1].astype(float).astype("Int32")


    df[col1]=df[col1].fillna(10100)


    columns=[col2,col1,'PENDING DAYS','STATUS']


    


    


    


    rename_cols={col2:'Claims',col1:'TASK ID'}


    df=filter_and_rename(df,columns, rename_cols)


    df['GROUP ID'] = [int(str(x)[:3]) for x in df['TASK ID']]


    


    df = status_bin_modify(df)


    df = create_bins(df)


    df=df[df['PENDING DAYS'] > num]


    df = pending_bins(df)


    





    df_pivot= pd.pivot_table(df, values='Claims', index=['STATUS'], columns=["Officer","GROUP ID"], 


                             margins=True,


                             aggfunc=lambda x: len(x))


    


    df_pivot=df_pivot.fillna(0)


    df_pivot = df_pivot.astype(int)


    return df_pivot





def get_pivot5(file,num=0, name="Unnamed", col1="ACC TASK ID",col2="TRAN CLAIM ID"):


    df = pd.read_csv(file)


    df[col1]=df[col1].astype(float).astype("Int32")


    df[col1]=df[col1].fillna(10100)


    columns=[col2,col1,'PENDING DAYS','STATUS']


    


    


    


    rename_cols={col2:'Claims',col1:'TASK ID'}


    df=filter_and_rename(df,columns, rename_cols)


    df['GROUP ID'] = [int(str(x)[:3]) for x in df['TASK ID']]


    


    df = status_bin_modify(df)


    df = create_bins(df)


    df=df[df['PENDING DAYS'] > num]


    df=df[df['STATUS'] == 'DA(Includes NTE)']


    df = pending_bins(df,4)


    





    df_pivot= pd.pivot_table(df, values='Claims', index=["GROUP ID",'TASK ID'], columns=["cat"], 


                             margins=True,


                             aggfunc=lambda x: len(x))


    


    df_pivot=df_pivot.fillna(0)


    df_pivot = df_pivot.astype(int)


    return df_pivot





def get_pivot6(file,num=0, name="Unnamed", col1="ACC TASK ID",col2="TRAN CLAIM ID"):


    df = pd.read_csv(file)


    df[col1]=df[col1].astype(float).astype("Int32")


    df[col1]=df[col1].fillna(10100)


    columns=[col2,col1,'PENDING DAYS','STATUS']


    df.to_excel("temp0.xlsx")


    


    


    rename_cols={col2:'Claims',col1:'TASK ID'}


    df=filter_and_rename(df,columns, rename_cols)


    df['GROUP ID'] = [int(str(x)[:3]) for x in df['TASK ID']]


    


    df = status_bin_modify(df)


    df = create_bins(df)


    df=df[df['PENDING DAYS'] > num]


    df = df.loc[df['STATUS'].isin(["Pending at DA","Pending at SS"])]


    df = pending_bins(df,5)


    df_pivot= pd.pivot_table(df, values='Claims', index=["GROUP ID",'TASK ID'], columns=["STATUS", "cat"], 


                             margins=True,


                             aggfunc=lambda x: len(x))


    


    df_pivot=df_pivot.fillna(0)


    df_pivot = df_pivot.astype(int)


    return df_pivot








df_claim   = get_pivot3(file1,"Claims","TASK ID","CLAIM ID")


df_claim2  = get_pivot4(file1,num=0,name="Claims",col1="TASK ID",col2="CLAIM ID")


df_claim3  = get_pivot4(file1,num=20,name="Claims",col1="TASK ID",col2="CLAIM ID")


df_claim4  = get_pivot5(file1,num=0,name="Claims",col1="TASK ID",col2="CLAIM ID")


print(df_claim4.head())


df_dsc     = get_pivot1(file3,"dscs")


df_esign   = get_pivot1(file4,"esigns")





df_online  = get_pivot2(file6,"Online")


df_primary = get_pivot2(file7,"Primary")


df_other   = get_pivot2(file8,"Other")








df_tin      = get_pivot7(file5,"Transfer In")


df_tin2     = get_pivot4(file5,num=0,name="Claims",col1="ACC TASK ID",col2="TRAN CLAIM ID")


df_tin3     = get_pivot4(file5,num=20,name="Claims",col1="ACC TASK ID",col2="TRAN CLAIM ID")


df_tin20    = get_pivot6(file5,num=20,name="Claims",col1="ACC TASK ID",col2="TRAN CLAIM ID")














def highlight(val=0):


    if val==0:


        return lambda x: ['font-weight: bold; border: 1px solid;'


               if value > df_claim4.nlargest(10,columns=['<=10 Days'])['<=10 Days'].iloc[9] else 'border: 1px solid;' for value in x]


    else:


        return lambda x: ['font-weight: bold; background-color: orange;border: 1px solid;'


               if value > val else 'border: 1px solid;' for value in x]


    








html = template % (""+


    "<h5>Claim Pendency</h5>"+df_claim.style.apply(highlight(5000)).to_html(classes=classes) + "" +


    "<h5>Claim Pendency (at each level)</h5>"+df_claim2.style.apply(highlight(5000)).to_html(classes=classes) + "" +


    "<h5>Claim Pendency (at each level >20days)</h5>"+df_claim3.style.apply(highlight(5)).to_html(classes=classes) + "" +


    "<h5>Transfer In Pendency</h5>"+df_tin.style.apply(highlight(1000)).to_html(classes=classes) + "" +


    "<h5>Transfer In (at each level)</h5>"+df_tin2.style.apply(highlight(1000)).to_html(classes=classes) + "" +


    "<h5>Transfer In (at each level >20days)</h5>"+df_tin3.style.apply(highlight(1000)).to_html(classes=classes) + "<div class='pagebreak' style=\"break-after:page\"></div>" +


    "<h5>Online Change Pendency</h5>"+df_online.style.apply(highlight(50)).to_html(classes=classes) + "" + 


    "<h5>Primary Change Pendency</h5>"+df_primary.style.apply(highlight(50)).to_html(classes=classes) + "" +


    "<h5>Other Change Pendency</h5>"+df_other.style.apply(highlight(10)).to_html(classes=classes) + "" + 


    "<h5>DSC Pendency</h5>"+df_dsc.style.apply(highlight(50)).to_html(classes=classes)    + "" + 


    "<h5>E-Sign Pendency</h5>"+df_esign.style.apply(highlight(50)).to_html(classes=classes)  + "<div class='pagebreak' style=\"break-after:page\"></div>" +


    "<h5>DA wise Pendency(Pending at DA or NTE)</h5>"+df_claim4.style.apply(highlight()).to_html(classes=classes) + "<br/>" +


    "<h5>DA wise NEFT Transfer in Pendency</h5>"+df_tin20.style.apply(highlight(20)).to_html(classes=classes) + "<br/>" +


"")





with open(out_html, 'w') as _file:


    soup = BeautifulSoup(html, 'html.parser')


    for table in soup.find_all('table'):


        table["class"] = classes


    for td in soup.find_all('td'):


        td["style"] = "font-size:10px;padding:2px;text-align:center;" 


    for th in soup.find_all('th'):


        th["style"] = "font-size:10px;padding:2px;text-align:center;"


    _file.write(str(soup))   








path_to_wkhtmltopdf = r'/path/to/wkhtmltopdf.exe'


config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)


pdfkit.from_file(out_html, output_path=out_pdf, configuration=config)
