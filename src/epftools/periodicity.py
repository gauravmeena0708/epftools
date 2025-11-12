import pandas as pd
import numpy as np
from datetime import datetime

FORM_NAME_MAPPING = {
    'Form-31': '31',
    'Form-31 [ COVID-2 ]': '31 - cov2',
    'Form-31 [ COVID ]': '31 - cov',
    'Form-31 [ 68J / Illness ]': '31 - ill',
    'Form-13 (Transfer Out) [ WITHOUT-MONEY  ]': '13 - wom',
    'Form-13 (Transfer Out) [ OTHERS ]': '13 - ot',
    'Form-13 (Transfer Out) [ WITH-MONEY ]': '13 - wm',
    'Form-13 (Transfer In / Same Office)': '13 - tin',
    'Form-10D': '10D',
    'Form-19': '19',
    'Form-10C [ Withdrawal Benefit ] ': '10C - WB',
    'Form-10C [ Scheme Certificate ]': '10C - SC',
    'Form-10D [ Death Case ]': 'Death-10D',
    'Form-5IF': 'Death-5IF',
    'Form-20': 'Death-20',
    'Form-14 (Funding of LIP)': '14'
}

PARA_DETAILS_MAPPING = {
    'Marriage ': 'Advance - Marriage',
    'DECLARED AS AFFECTED BY OUTBREAK OF EPIDEMIC OR PANDEMIC  BY APPROPRIATE GOVERNMENT (COVID-19)': 'Advance - Covid',
    'Illness': 'Advance - Illness',
    'Transfer (Unexempted to Unexempted in other region or to Exempted Establishments)': 'Transfer',
    'Transfer (Unexempted to Unexempted in other region or to Exempted Establishments)': 'Transfer',
    'Transfer (Unexempted to Unexempted in same region (office)': 'Transfer',
    'Transfer (Unexempted to Unexempted in same region (office)': 'Transfer',
    'Transfer (Unexempted to Unexempted in same region (office)\r\n':'Transfer',
    'Transfer (Unexempted to Unexempted in same region (office) ':'Transfer',
    'Monthly Pension - Member': 'Pension - 10D',
    'Resign': 'Final - 19',
    'Settelment to Survivor on death of member':'Death-20',
    'Non Receipt of Wages (>2 months)':'Advance - NRW2M',
    'ADVANCE FOR CONTINUOUS UNEMPLOYMENT FOR ABOVE ONE MONTH': 'Advance - Unemployment 1M',
    'Withdrawal Benefit / Scheme Certificate': 'Pension - 10C',
    'Additions / Alterations of House': 'Advance - Alteration',
    'Construction of House': 'Advance - Construction',
    'Purchase of House / Flat / Construction including acquisition if site from agency': 'Advance - Agency',
    'Natural Calamities': 'Advance - NC',
    'Purchase of Site for Construction of Dwelling House': 'Advance - Construction',
    'Non-Receipt of Wages (>2 months)': 'Advance - NRW_2M',
    ' Higher Education': 'Advance - Higher Education',
    'Purchase of Dwelling House/ Flat from a Promoter ': 'Advance - Promoter',
    'Purchase of Handicap equipment': 'Advance - Handicap',
    'Retirement from service after attaining the age of 55 years': 'Final - 19',
    'Termination of service in the case of mass or individual retrenchment': 'Advance - Mass Retrenchment',
    '90% Withdrawal before retirement': 'Advance - Before Retirement 90',
    'Monthly Pension - Survivors': 'Death-Pension',
    'EDLI Assurance Benefit': 'Death-EDLI',
    'Settlement to Survivor on the death of a member': 'Death-PF',
    'Power Cut': 'Advance - PowerCut',
    'nan': 'Not Available',
    'Payment of Accumulations in the case of Beneficiary charged with the offense of Murder of the deceased member ': 'Advance - ChargedWithMurder',
    'Payment of LIP Premium': 'Advance - LIP',
    np.nan: 'Death-20'
}

def read_periodicity_data(filepath, year):
    """Reads and processes periodicity data from a CSV file."""
    df = pd.read_csv(filepath, encoding='latin1')
    df['RECEIPT_DATE'] = pd.to_datetime(df['RECEIPT_DATE'])
    df.dropna(subset=['SETTLED_REJECT_DATE'], how='all', inplace=True)
    df['SETTLED_REJECT_DATE'] = pd.to_datetime(df['SETTLED_REJECT_DATE'])

    df['FORM_NAME'] = df['FORM_NAME'].replace(FORM_NAME_MAPPING)
    df['PARA_DETAILS'] = df['PARA_DETAILS'].replace(PARA_DETAILS_MAPPING)

    df['EST'] = [str(x)[:15] for x in df['MEMBER_ID']]
    df['month'] = df['SETTLED_REJECT_DATE'].dt.month
    df['week'] = df['SETTLED_REJECT_DATE'].dt.isocalendar().week
    df['weekday'] = df['SETTLED_REJECT_DATE'].dt.day_name()
    df['mday'] = df['SETTLED_REJECT_DATE'].dt.day
    df['yday'] = df['SETTLED_REJECT_DATE'].dt.dayofyear
    df.dropna(subset=['TASK_ID'], inplace=True)
    df['TASK_ID'] = df['TASK_ID'].astype("int").astype("category")
    df['GROUP_ID'] = df['GROUP_ID'].astype("int").astype("category")
    df['FORM_NAME'] = df['FORM_NAME'].astype("category")
    df['PARA_DETAILS'] = df['PARA_DETAILS'].astype("category")
    df['dt'] = pd.to_datetime(df['SETTLED_REJECT_DATE']).dt.date
    df['month'] = pd.to_datetime(df['SETTLED_REJECT_DATE']).dt.month.astype(str).str.zfill(2)
    df['monthn'] = pd.to_datetime(df['SETTLED_REJECT_DATE'], format='%d/%m/%y, %I:%M %p').dt.month_name()
    df['date'] = pd.to_datetime(df['SETTLED_REJECT_DATE']).dt.day
    df['day'] = pd.to_datetime(df['SETTLED_REJECT_DATE']).dt.day_name()
    df['year'] = pd.to_datetime(df['SETTLED_REJECT_DATE']).dt.year
    df['ym'] = df['year'].astype(str) + df['month'].astype(str)
    df['md'] = df['monthn'].astype(str) + '-' + df['date'].astype(str)
    df['fy'] = year
    df['quarter'] = df['SETTLED_REJECT_DATE'].apply(get_financial_year_quarter)

    df.loc[df['DAYS_TAKEN_FOR_REJECTION'].isnull(), 'outcome'] = 'settled'
    df.loc[df['DAYS_TAKEN_FOR_SETTLEMENT'].isnull(), 'outcome'] = 'rejected'

    df['TOTAL_AMOUNT'] = df['TOTAL_AMOUNT'].apply(process_row)
    df.loc[df['TOTAL_AMOUNT'].between(0, 50000, 'both'), 'cat'] = '<50k'
    df.loc[df['TOTAL_AMOUNT'].between(50001, 500000, 'both'), 'cat'] = '50k-5lakh'
    df.loc[df['TOTAL_AMOUNT'].between(500001, 2500000, 'both'), 'cat'] = '5lakh-25lakh'
    df.loc[df['TOTAL_AMOUNT'].ge(2500000), 'cat'] = '>=25lakh'
    return df

def get_rejection_summary(df, group_by_col):
    """Generates a summary of rejection ratios grouped by a specific column."""
    df['rejected'] = df.groupby(['month', group_by_col])['outcome'].transform(lambda x: (x == 'rejected').sum())
    df['settled'] = df.groupby(['month', group_by_col])['outcome'].transform(lambda x: (x == 'settled').sum())
    df['total'] = df.groupby(['month', group_by_col])['outcome'].transform('count')
    df['Rejected_Ratio'] = round(df['rejected'] * 100 / df['total'], 2)
    pivot_table = df.pivot_table(index=group_by_col, columns='month', values='Rejected_Ratio', fill_value=0)
    pivot_table = pivot_table.round(2)

    for index, row in pivot_table.iterrows():
        total_count = df[df[group_by_col] == index]['total'].count()
        settled_count = df[(df[group_by_col] == index) & (df['outcome'] == 'settled')]['settled'].count()
        rejected_count = df[(df[group_by_col] == index) & (df['outcome'] == 'rejected')]['rejected'].count()

        pivot_table.at[index, 'rejected'] = int(rejected_count)
        pivot_table.at[index, 'settled'] = int(settled_count)
        pivot_table.at[index, 'total'] = int(total_count)
        pivot_table.at[index, 'overall_ratio'] = round(int(rejected_count) * 100 / int(total_count), 2) if total_count > 0 else 0

    return pivot_table.reset_index()

def get_financial_year_quarter(date):
    if date.month >= 4:
        return (date.month - 4) // 3 + 1
    else:
        return (date.month + 8) // 3

def process_row(value):
    if value == 'nan' or value == '' or value == ' ':
        return np.nan
    else:
        return float(str(value).replace(',', ''))
