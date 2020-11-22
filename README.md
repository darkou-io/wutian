# wutian
量化交易平台

#运行本项目
* 下载 backtrader，本项目使用作者修改过的 backtrader

`cd $BACKTRADER_PARENT_PATH && git clone https://github.com/darkou-io/backtrader.git`
* 本见将 $BACKTRADER_PATH添加到 PYTHONPATH

`export PYTHONPATH=$PYTHONPATH:$BACKTRADER_PATH`

* 启动脚本查看效果

`python3 cmd/start_up.py $TUSHARE_TOKEN 000725.SZ`

* 效果图查看
![效果图](https://github.com/darkou-io/wutian/static/images/000725.png)
