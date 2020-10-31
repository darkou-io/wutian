#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
# @Time: 2020/10/19 下午11:14
# @Author: 黑莲
# @Version: v0.1.0
# @File: main.py
# @Desc:

import backtrader as bt
import backtrader.indicators as btind
import backtrader.feeds as btfeeds
from backtrader.plot import Plot
import pandas as pd
import tushare
import sys
import datetime


tushare_token = sys.argv[1]
tushare.set_token(tushare_token)
client = tushare.pro_api()
all_company = {}


class TestStrategy(bt.Strategy):
    params = (
        ('exit_bars', 5),
        ('ma_period', 15),
        ('print_log', False),
    )

    def log(self, txt, dt=None, do_print=False):
        ''' Logging function for this strategy'''
        if self.params.print_log or do_print:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        # self.sma = bt.indicators.MovingAverageSimple(
        #     self.datas[0], period=self.params.ma_period)
        self.dataclose = self.datas[0].close
        self.order = None
        self.order = None
        self.buyprice = None
        self.buycomm = None
        bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        self.sma = bt.indicators.StochasticSlow(self.datas[0])
        # bt.indicators.WeightedMovingAverage(
        #     self.datas[0], period=25, subplot=True)
        bt.indicators.MACDHisto(self.datas[0])
        # rsi = bt.indicators.RSI(self.datas[0])
        # bt.indicators.SmoothedMovingAverage(rsi, period=10)
        # bt.indicators.ATR(self.datas[0], plot=True)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] > self.sma[0]:
                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

        else:

            if self.dataclose[0] < self.sma[0]:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()

    def stop(self):
        self.log('(MA Period %2d) Ending Value %.2f' %
                 (self.params.ma_period, self.broker.getvalue()), do_print=True)


def align_data_for_backtrader(df):
    df.index = pd.to_datetime(df['trade_date'])
    df['open'] = df['open']
    df['high'] = df['high']
    df['low'] = df['low']
    df['close'] = df['close']
    df['volume'] = df['vol']
    df['openinterest'] = 0
    return df[['open', 'high', 'low', 'close',
               'volume', 'openinterest', 'amount']]


def get_today():
    today = datetime.date.today()
    return today.strftime("%Y%m%d")


def get_data_source(ts_code):
    df = client.query(
        'daily',
        ts_code=ts_code,
        start_date='20200119',
        end_date=get_today())
    print(df.columns)
    df = align_data_for_backtrader(df)
    df = df.sort_index(ascending=True)
    print(df.index)
    return df


def analyse_target(ts_code):
    company = all_company[ts_code]
    data = bt.feeds.PandasDirectData(dataname=get_data_source(ts_code))
    cerebro = bt.Cerebro()
    cerebro.addstrategy(
        TestStrategy,
        ma_period=20)
    bt.feeds.PandasDirectData()
    cerebro.adddata(data)
    cerebro.broker.setcash(100000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    cerebro.broker.setcommission(commission=0.0016)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run(maxcpus=1)
    plot = Plot(title='{}({})'.format(company['name'], ts_code))
    cerebro.plot(plotter=plot, iplot=False)


def list_all_company():
    resp = client.query('stock_basic', list_status='L')
    for _, row in resp.iterrows():
        all_company[row['ts_code']] = row.to_dict()


def _real_main():
    list_all_company()
    share_codes = sys.argv[2].split(',')
    for sc in share_codes:
        analyse_target(sc)


if __name__ == '__main__':
    _real_main()
