import pandas as pd
from pathlib import Path
import pdfkit

template=Path('template.html').read_text()
file1 = "Performance ReportDA.XLS"
file2 = "Performance AO.XLS"
file3 = "mapping.xlsx"
df_map = pd.read_excel(file3)

significant = lambda x: '<span class="significant">%f</span>' % x if x<0.05 else str(x)
classes = 'table table-hover table-bordered border-primary d-print-table'

def highlight(val=0):
    if val==0:
        return lambda x: ['font-weight: bold; background-color: orange;border: 1px solid;'
               if value > df_claim4.nlargest(10,columns=['<=15 Days'])['<=15 Days'].iloc[9] else 'border: 1px solid;' for value in x]
    else:
        return lambda x: ['font-weight: bold; background-color: orange;border: 1px solid;'
               if (isinstance(value, int) and int(value) > int(val)) else 'border: 1px solid;' for value in x]
    
def summarize(input_file,flag=0):
    df = pd.read_excel(input_file,header=None, skiprows=13)#, encoding= 'unicode_escape')
    df2 = df[df[9].notna()]
    df3 = df2[df2[9].str.isnumeric()]
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
    df5 = df5.astype({'userid':'int',
                      "F19":'int',
                      "F20":'int',
                      "F31":'int',
                      "13-in":'int',
                      "13-out":'int',
                      "14":'int',
                      '10D':'int',
                      "5If":'int',
                      "10c":'int',
                      "others":'int',
                      "total":'int',
                      "annexurek":'int'
}, errors = 'ignore')
    if flag:
        df6 = pd.merge(left=df5, right=df_map, how='left',on='userid')
        df6 = df6.sort_values(['group','total'], ascending=[True,False])
    else:
        df6 = df5.sort_values(['total'], ascending=[False])
    return df6    
    #df6.to_excel(input_file+"_summary.xlsx",index=False) #.style.apply(highlight(5000))
    
    
df1 = summarize(file1,flag=1)
df2 = summarize(file2,flag=0)
path_to_wkhtmltopdf = r'/path/to/wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)
html = template % (""+
        "<h2>DA performance</h2>"+df1.to_html(classes=classes) + "<br/>" +
        "<h2>Approver Performance</h2>" +df2.to_html(classes=classes) + "<br/>" +
    "")
#pdfkit.from_string(html, input_file+"_summary.pdf")
pdfkit.from_string(str(html),"Performance_summary.pdf", configuration=config)