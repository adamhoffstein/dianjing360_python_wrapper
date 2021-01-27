import pandas as pd
import numpy as np
import pygsheets
import csv
from datetime import timedelta

def auth_sheet(url):
    client =  pygsheets.authorize(
        service_account_env_var = 'GDRIVE_API_CREDENTIALS'
        )
    return client.open_by_url(url)

def get_sheets(url):
    sh = auth_sheet(url)
    sheet_dict = {}
    for s in sh:
        sheet_dict.update({s.title:s.index})
    return sheet_dict

def get_last_row(sheet, url, index_col='date'):
    sh = auth_sheet(url)
    wks = sh[sheet]
    last_row = wks.get_as_df(has_header=True).tail(1)
    last_row[index_col] = pd.to_datetime(last_row[index_col], format='%Y-%m-%d')
    return last_row

def append_sheet(sheet, url, data):
    sh = auth_sheet(url)
    wks = sh[sheet]
    last_row = wks.get_as_df(has_header=True).tail(1).index[0]+3
    wks.set_dataframe(data, f'A{last_row}', copy_head=False, copy_index=False)

def replace_sheet(sheet, url, data):
    sh = auth_sheet(url)
    wks = sh[0]
    wks.set_dataframe(data, 'A1', copy_head=True, copy_index=False)

def format_360(path):
    df = pd.read_csv(path, encoding='GBK')

    if ('mobile' in path or 'pc' in path):
        df.columns = [
            'Account','Date','Campaign','Impressions',
            'Clicks','CTR','Cost','CPC','Product Line'
            ]
        df = df[[
            'Date','Campaign','Impressions','Clicks','Cost'
        ]]

    else:
        df.columns = [
            'Account','Date','Campaign','City','Location method',
            'Impressions','Clicks','CTR','Cost','CPC','Product Line'
        ]
        df = df[[
            'Date','Campaign','City','Location method',
            'Impressions','Clicks','Cost'
            ]]

    last_row = df.index[df['Date'] == '总点击次数'].tolist()[0]-1
    df = df.truncate(after=last_row)
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    return df

def format_ga(data):
    with open(data) as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        readerlist = [r for r in reader][6:]
        column_names = readerlist[0]
        data = readerlist[1:]
        print(data)

    df = pd.DataFrame(data, columns=column_names)
    index_row = df.index[df['Search Query'] == 'Day Index'].tolist()[0]-3
    df = df.truncate(after=index_row)
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
    return df

def format_ads_report(path):
    df = pd.read_excel(path, sheet_name='Report data')
    df.columns = [c.lower().replace(' ','_') for c in df.columns]
    df['device'] = np.where(
        df.line_item.str.contains('Desktop'), 'Desktop', 'Smartphone'
        )
    df['dimension'] = 'Parallax'
    df['campaign'] = 'Aller Main'
    df['impressions'] = df.ad_server_impressions
    df['clicks'] = df.ad_server_clicks
    formated_df = df[
        ['date','dimension','campaign','device','impressions','clicks']
        ][:-1]
    formated_df['date'] = formated_df['date']
    return formated_df
