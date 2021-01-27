import os
import json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from dianjing import dianjing
from ghelp.gsheets import get_sheets, get_last_row, append_sheet

GOOGLE_SHEET = os.environ['360_GOOGLE_SHEET']

def run_region_report(client, yesterday):
    regions = client.get_region_dict()
    region_df = pd.DataFrame(regions)[['areaname','areacode']]
    region_df = region_df.rename(columns={'areacode':'regionId'})
    region_report = client.get_region_report(start=yesterday, end=yesterday)
    dfs = [pd.DataFrame(page) for page in region_report]
    region_report_df = pd.concat(dfs)

    merged_df = region_report_df.merge(region_df, on='regionId', how='left')
    merged_df = merged_df.rename(columns={'date':'Date'})
    merged_df.Date = pd.to_datetime(merged_df.Date, format='%Y-%m-%d')
    merged_df = merged_df[
        ['Date','campaignName','areaname','views','clicks','totalCost']
        ]
    sheets = get_sheets(GOOGLE_SHEET)
    last_region_date = get_last_row(
        sheets.get('region'), GOOGLE_SHEET, index_col='Date'
        ).Date.values[0]
    new_region_values = merged_df.loc[merged_df.Date > last_region_date]

    if not new_region_values.empty:
        append_sheet(sheets.get('region'), GOOGLE_SHEET, new_region_values)

def run_fengwu_report(client, startend):
    report = client.get_fengwu_report(start=startend, end=startend)
    dfs = [pd.DataFrame(page) for page in report]
    fengwu_df = pd.concat(dfs)
    fengwu_df.date = pd.to_datetime(fengwu_df.date, format='%Y-%m-%d')

    sheets = get_sheets(GOOGLE_SHEET)

    last_fengwu_date = get_last_row(
        sheets.get('fengwu'), GOOGLE_SHEET
        ).date.values[0]

    new_fengwu_values = fengwu_df.loc[fengwu_df.date > last_fengwu_date]
    new_fengwu_values = new_fengwu_values.replace(np.nan, '', regex=True)

    if not new_fengwu_values.empty:
        append_sheet(sheets.get('fengwu'), GOOGLE_SHEET, new_fengwu_values)

def run_device_report(client, yesterday):
    sheets = get_sheets(GOOGLE_SHEET)
    last_device_date = get_last_row(
        sheets.get('platform'), GOOGLE_SHEET, 'Date'
        ).Date.values[0]
    after_device_date = last_device_date + np.timedelta64(1,'D')
    start = np.datetime_as_string(last_device_date, unit='D')

    mobile_report = client.get_campaign_report(
        start=start, end=yesterday, device='mobile'
        )
    dfs = [pd.DataFrame(page) for page in mobile_report]
    mobile_df = pd.concat(dfs)
    mobile_df['Platform'] = 'Mobile'

    desktop_report = client.get_campaign_report(
        start=start, end=yesterday, device='computer'
        )
    dfs = [pd.DataFrame(page) for page in desktop_report]
    desktop_df = pd.concat(dfs)
    desktop_df['Platform'] = 'Desktop'

    platform_df = pd.concat(
        [mobile_df, desktop_df]).sort_values(by=['date','Platform']
        )
    platform_df = platform_df[
        ['date','campaignName','views','clicks','totalCost','Platform']
        ]
    platform_df.date = pd.to_datetime(platform_df.date, format='%Y-%m-%d')

    new_platform_values = platform_df.loc[platform_df.date > last_device_date]
    new_platform_values = new_platform_values.replace(np.nan, '', regex=True)

    if not new_platform_values.empty:
        append_sheet(sheets.get('platform'), GOOGLE_SHEET, new_platform_values)


def lambda_handler(event, context):
    yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')

    client = dianjing.Q360Base(
        account=os.environ['360_ACCOUNT'].encode('utf-8'),
        password=os.environ['360_PASSWORD'].encode('utf-8')
    )

    client._get_access_token()

    run_fengwu_report(client, yesterday)

    run_device_report(client, yesterday)

    run_region_report(client, yesterday)

    return {
        'statusCode': 200,
        'body': json.dumps('It worked!')
    }
