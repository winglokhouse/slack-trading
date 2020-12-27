import yfinance as yf
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_finance import candlestick_ohlc
import talib as TA

from os import listdir
import boto3

def download_data_from_s3(s3_bucket, local_path):
    session = boto3.Session(region_name='ap-east-1')
    s3 = session.client('s3', endpoint_url='https://s3.ap-east-1.amazonaws.com')
    response = s3.list_objects(Bucket=s3_bucket)
    file_list = [k['Key'] for k in response['Contents']]
    for key in file_list:
        local_file = local_path + '/' + key
        response = s3.download_file(Bucket=s3_bucket, Key=key, Filename=local_file)

def upload_data_to_s3(s3_bucket, local_path):
    session = boto3.Session(region_name='ap-east-1')
    s3 = session.client('s3', endpoint_url='https://s3.ap-east-1.amazonaws.com')
    file_list = listdir(local_path)
    for key in file_list:
        local_file = local_path + '/' + key
        response = s3.upload_file(Bucket=s3_bucket, Key=key, Filename=local_file)


def plot_two_stocks(stock1, stock2, prevday_returns, today_returns, start, end):
    if '.prev' in stock1:
        stock1 = stock1.split('.prev')[0]
        print(stock1)
    #
    df1 = yf.download(stock1, start=start, end=end)
    df1['Date'] = df1.index
    df1['Date'] = df1['Date'].apply(mdates.date2num)
    df2 = yf.download(stock2, start=start, end=end)
    df2['Date'] = df2.index
    df2['Date'] = df2['Date'].apply(mdates.date2num)
    #
    ohlc_seq = ['Date', 'Open', 'High', 'Low', 'Close']
    fig = plt.figure(figsize = (15,20))
    # fig.suptitle('{}.HK {}'.format(label, start_date.year), fontsize=18)
    current_row = 0
    ax_height = 3
    ax0 = plt.subplot2grid((15,4), (current_row,0), rowspan=ax_height, colspan=4)
    ax0.grid(True)
    candlestick_ohlc(ax0, df1[ohlc_seq].values, width=.4, colorup='#53c156', colordown='#ff1717')
    ax0.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax0.legend(['Prev {}'.format(stock1)])
    #
    current_row = current_row + ax_height
    ax_height = 3
    ax1 = plt.subplot2grid((15,4), (current_row,0), rowspan=ax_height, colspan=4, sharex=ax0)
    ax1.grid(True)
    candlestick_ohlc(ax1, df2[ohlc_seq].values, width=.4, colorup='#53c156', colordown='#ff1717')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax1.legend(['Today {}'.format(stock2)])
    #
    prev_stock = '{}.prev'.format(stock1)
    now_stock = stock2
    compare_df = pd.concat([prevday_returns[prev_stock], today_returns[now_stock]], axis=1)
    print('Total prev stock rise {}'.format(compare_df[compare_df[prev_stock]<0].shape[0]))
    print('Total prev stock rise and today rise {}'.format(compare_df[(compare_df[prev_stock]<0) & (compare_df[now_stock]<0)].shape[0]))
    #
    current_row = current_row + ax_height
    ax_height = 3
    ax2 = plt.subplot2grid((15,4), (current_row,0), rowspan=ax_height, colspan=4, sharex=ax0)
    ax2.grid(True)
    ax2.plot(prevday_returns.index,prevday_returns[prev_stock],color="black",label="Prevday Return",linewidth=1)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax2.legend(['Prev {}'.format(stock1)])
    #
    current_row = current_row + ax_height
    ax_height = 3
    ax3 = plt.subplot2grid((15,4), (current_row,0), rowspan=ax_height, colspan=4, sharex=ax0)
    ax3.grid(True)
    ax3.plot(today_returns.index,today_returns[now_stock],color="blue",label="Today Return",linewidth=1)
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax3.legend(['Today {}'.format(stock2)])