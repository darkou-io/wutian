#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
# @Time: 2020/10/19 下午11:14
# @Author: 黑莲
# @Version: v0.1.0
# @File: main.py
# @Desc:

import backtrader as bt
import pandas as pd
import tushare
import sys
import datetime


tushare_token = sys.argv[1]
tushare.set_token(tushare_token)
client = tushare.pro_api()
cerebro = bt.Cerebro()


class PrintClose(bt.Strategy):
    params = (
        ('ma_period', 10),
    )

    def __init__(self):
        # 指定价格序列
        self.dataclose = self.datas[0].close
        # 初始化交易指令、买卖价格和手续费
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # 添加移动均线指标，内置了talib模块
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.ma_period)

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
        print(self.datas[0])
        # 打印日期和收盘价格

    def next(self):
        if self.order:  # 检查是否有指令等待执行,
            return

        # 检查是否持仓
        if not self.position:  # 没有持仓
            # 执行买入条件判断：收盘价格上涨突破20日均线
            if self.dataclose[0] > self.sma[0]:
                # 执行买入
                self.order = self.buy(size=500)
        else:
            # 执行卖出条件判断：收盘价格跌破20日均线
            if self.dataclose[0] < self.sma[0]:
                # 执行卖出
                self.order = self.sell(size=500)


def align_data_for_backtrader(df):
    df.index = pd.to_datetime(df['trade_date'])
    df['open'] = df['open']
    df['high'] = df['high']
    df['low'] = df['low']
    df['close'] = df['close']
    df['volume'] = df['vol']
    df['openinterest'] = 0
    return df[['open', 'high', 'low', 'close', 'volume', 'openinterest', 'amount']]


def get_data_source():
    share_code = '600028.SH'
    df = client.query('daily', ts_code=share_code, start_date='20200101', end_date='20201019')
    print(df.columns)
    return align_data_for_backtrader(df)


def _real_main():
    data = bt.feeds.PandasDirectData(dataname=get_data_source())
    cerebro.addstrategy(PrintClose)
    bt.feeds.PandasDirectData()
    cerebro.adddata(data)
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.00025)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    results = cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    print('最终资金: %.2f' % cerebro.broker.getvalue())
    cerebro.plot()


if __name__ == '__main__':
    _real_main()
