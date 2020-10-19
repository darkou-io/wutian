#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
# @Time: 2020/10/19 下午11:14
# @Author: 黑莲
# @Version: v0.1.0
# @File: main.py
# @Desc:

import tushare
import sys

tushare_token = sys.argv[1]
tushare.set_token(tushare_token)
client = tushare.pro_api()


def _real_main():
    df = client.query('daily', ts_code='600028.SH', start_date='20200701', end_date='20201019')
    print(df[:1])


if __name__ == '__main__':
    _real_main()
