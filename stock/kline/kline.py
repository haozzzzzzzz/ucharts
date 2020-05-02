# -*- coding: utf-8 -*-
__author__ = "Hao Luo"

from pyecharts.charts import Kline, Bar, Line, Grid
import pyecharts.options as opts
from pyecharts.commons.utils import JsCode
import talib
import pandas


class Config:
    COLOR_POSITIVE = "#B34038"
    COLOR_NEGATIVE = "#354654"

    ZOOM_RANGE_START_PERCENT = 90
    ZOOM_RANGE_END_PERCENT = 100

    CLOSE_PRICE_MALINE_CONFIGS = [
        {
            "day_count": 1,
            "color": "gold"
        },
        {
            "day_count": 5,
            "color": "blue"
        },
        {
            "day_count": 10,
            "color": "black"
        },
        {
            "day_count": 20,
            "color": "red"
        },
        {
            "day_count": 30,
            "color": "rosybrown"
        }
    ]

    VOLUME_MALINE_CONFIGS = [
        {
            "day_count": 5,
            "color": "blue"
        },
        {
            "day_count": 10,
            "color": "black"
        }
    ]

    KDJ = {
        "k_color": "red",
        "d_color": "blue",
        "j_color": "gold"
    }


class IndexGenerator:
    index = 0

    def __init__(self):
        self.index = 0

    def generate(self):
        idx = self.index
        self.index += 1
        return 0


class Candlestick:
    """
    基础K线图
    """
    title = ""
    x_date = [] # [str_date]
    y_data = [] # [[open_price, close_price, low_price, high_price]]
    y_close_prices = [] # [close_price]
    xaxis_index = None
    yaxis_index = None

    def __init__(self, title, x_date, y_data, xaxis_index=0, yaxis_index=0):
        self.title = title
        self.x_date = x_date
        self.y_data = y_data
        self.xaxis_index = xaxis_index
        self.yaxis_index = yaxis_index

        for y_item in y_data:
            self.y_close_prices.append(y_item[1])

    def get_chart(self):
        k_chart = Kline()
        k_chart.add_xaxis(xaxis_data=self.x_date)
        k_chart.add_yaxis(
            series_name="candle",
            y_axis=self.y_data,
            xaxis_index=self.xaxis_index,
            yaxis_index=self.yaxis_index,
            itemstyle_opts=opts.ItemStyleOpts(
                color=Config.COLOR_POSITIVE,
                color0=Config.COLOR_NEGATIVE,
            ),
        )
        k_chart.set_series_opts()
        k_chart.set_global_opts(
            title_opts=opts.TitleOpts(title=self.title),
            xaxis_opts=opts.AxisOpts(
                is_scale=True,
                axispointer_opts=opts.AxisPointerOpts(
                    is_show=True,
                )
            ),
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                splitarea_opts=opts.SplitAreaOpts(
                    is_show=True,
                    areastyle_opts=opts.AreaStyleOpts(opacity=1)
                )
            ),
            datazoom_opts=[
                opts.DataZoomOpts(
                    range_start=Config.ZOOM_RANGE_START_PERCENT,
                    range_end=Config.ZOOM_RANGE_END_PERCENT
                ),
                opts.DataZoomOpts(
                    type_="inside",
                    range_start=Config.ZOOM_RANGE_START_PERCENT,
                    range_end=Config.ZOOM_RANGE_END_PERCENT
                )
            ],
        )

        ma_line = MaLine(self.title, x_date=self.x_date, y_close_prices=self.y_close_prices, xaxis_index=self.xaxis_index, yaxis_index=self.yaxis_index)
        ma_line_chart = ma_line.get_chart()
        k_chart.overlap(ma_line_chart)
        return k_chart

    def render(self):
        return self.get_chart().render()

    def render_notebook(self):
        return self.get_chart().render_notebook()


bar_color_function = '''
        function (params) {
            var change_state = params.data[2];
            if (change_state >= 0) {
                return \'''' + Config.COLOR_POSITIVE + '''\';
            } else if (change_state < 0) {
                return \'''' + Config.COLOR_NEGATIVE + '''\';
            }
            return 'yellow';
        }
'''


class VolumeBar:
    """
    成交量
    """
    title = ""
    x_date = []  # [str_date]
    y_data = []  # [[index, volume, change_state]]
    y_volumes = []
    xaxis_index = 0
    yaxis_index = 0

    def __init__(self, title, x_date, y_data, xaxis_index=0, yaxis_index=0):
        self.title = title
        self.x_date = x_date
        self.y_data = y_data
        self.xaxis_index = xaxis_index
        self.yaxis_index = yaxis_index

        for y_item in y_data:
            self.y_volumes.append(y_item[1])

    def get_chart(self):
        # bar
        volume_bar = Bar()
        volume_bar.add_xaxis(xaxis_data=self.x_date)
        volume_bar.add_yaxis(
            series_name="volume",
            yaxis_data=self.y_data,
            xaxis_index=self.xaxis_index,
            yaxis_index=self.yaxis_index,
            label_opts=opts.LabelOpts(
                is_show=False
            ),
            itemstyle_opts=opts.ItemStyleOpts(color=JsCode(bar_color_function))
        )
        volume_bar.set_global_opts(
            title_opts=opts.TitleOpts(title=self.title),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                is_scale=True,
                axispointer_opts=opts.AxisPointerOpts(
                    is_show=True,
                )
            ),
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                splitarea_opts=opts.SplitAreaOpts(
                    is_show=True,
                    areastyle_opts=opts.AreaStyleOpts(opacity=1)
                )
            ),
            datazoom_opts=[
                opts.DataZoomOpts(
                    range_start=Config.ZOOM_RANGE_START_PERCENT,
                    range_end=Config.ZOOM_RANGE_END_PERCENT
                ),
                opts.DataZoomOpts(
                    type_="inside",
                    range_start=Config.ZOOM_RANGE_START_PERCENT,
                    range_end=Config.ZOOM_RANGE_END_PERCENT
                )
            ],
        )

        # ma line
        ma_line = Line()
        ma_line.add_xaxis(xaxis_data=self.x_date)

        for ma_config in Config.VOLUME_MALINE_CONFIGS:
            day_count = ma_config["day_count"]
            ma_line.add_yaxis(
                series_name="VMA%d" % day_count,
                y_axis=talib.MA(pandas.Series(self.y_volumes), timeperiod=day_count, matype=0),
                xaxis_index=self.xaxis_index,
                yaxis_index=self.yaxis_index,
                linestyle_opts=opts.LineStyleOpts(
                    width=1,
                    color=ma_config["color"],
                ),
                is_symbol_show=False,
            )

        ma_line.set_series_opts(
            label_opts=opts.LabelOpts(
                is_show=False
            ),
        )

        volume_bar.overlap(ma_line)

        return volume_bar

    def render(self):
        return self.get_chart().render()

    def render_notebook(self):
        return self.get_chart().render_notebook()


class MaLine:
    """
        移动平均线
    """
    title = ""
    x_date = []  # [str_date]
    y_close_prices = []  # [close_price]
    day_configs = []
    xaxis_index = None
    yaxis_index = None

    def __init__(self, title, x_date, y_close_prices, xaxis_index=0, yaxis_index=0, day_configs=[]):
        self.title = title
        self.x_date = x_date
        self.y_close_prices = y_close_prices
        self.xaxis_index = xaxis_index
        self.yaxis_index = yaxis_index

        self.day_configs = [config for config in Config.CLOSE_PRICE_MALINE_CONFIGS] + day_configs

    def get_chart(self):
        line = Line()
        line.add_xaxis(xaxis_data=self.x_date)

        for day_config in self.day_configs:
            day_count = day_config["day_count"]
            line.add_yaxis(
                series_name="MA%d" % day_count,
                y_axis=talib.MA(pandas.Series(self.y_close_prices), timeperiod=day_count, matype=0),
                xaxis_index=self.xaxis_index,
                yaxis_index=self.yaxis_index,
                linestyle_opts=opts.LineStyleOpts(
                    width=1,
                    color=day_config["color"],
                ),
                is_symbol_show=False
            )

        line.set_series_opts(
            label_opts=opts.LabelOpts(
                is_show=False
            ),
        )
        line.set_global_opts(
            title_opts=opts.TitleOpts(title=self.title),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                is_scale=True,

                axispointer_opts=opts.AxisPointerOpts(
                    is_show=True,
                )
            ),
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
            ),
            datazoom_opts=[
                opts.DataZoomOpts(
                    range_start=Config.ZOOM_RANGE_START_PERCENT,
                    range_end=Config.ZOOM_RANGE_END_PERCENT
                ),
                opts.DataZoomOpts(
                    type_="inside",
                    range_start=Config.ZOOM_RANGE_START_PERCENT,
                    range_end=Config.ZOOM_RANGE_END_PERCENT
                )
            ],
        )
        return line

    def render_notebook(self):
        return self.get_chart().render_notebook()


class MacdChart:
    '''
    MACD
    '''
    title = ""
    x_date = [] # [date]
    diff_data = [] # [number]
    signal_data = [] # [number]
    histogram_data = [] # [[idx, number, display_color]]
    hist_diplay_ratio = 1  # 乘上系数用于展示。同花顺、雪球是2
    xaxis_index = 0

    color_diff = "gold"
    color_signal = "blue"

    def __init__(self, title, x_date, close_prices, xaxis_index=0, yaxis_index=0):
        self.title = title + " MACD"
        self.x_date = x_date
        self.xaxis_index = xaxis_index
        self.yaxis_index = yaxis_index

        # macd
        macd_dif, macd_signal, macd_hist = talib.MACD(pandas.Series(close_prices))

        self.diff_data = macd_dif
        self.signal_data = macd_signal
        for i, hist in enumerate(macd_hist):
            display_color = 1
            if hist < 0:
                display_color = -1

            self.histogram_data.append([i, hist, display_color])

    def get_chart(self):
        line = Line()
        line.add_xaxis(xaxis_data=self.x_date)
        line.add_yaxis(
            series_name="DIF",
            y_axis=self.diff_data,
            xaxis_index=self.xaxis_index,
            yaxis_index=self.yaxis_index,
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(
                color=self.color_diff,
            )
        )
        line.add_yaxis(
            series_name="DEA",
            y_axis=self.signal_data,
            xaxis_index=self.xaxis_index,
            yaxis_index=self.yaxis_index,
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(
                color=self.color_signal,
            )
        )
        line.set_series_opts(
            label_opts=opts.LabelOpts(
                is_show=False
            ),
            is_symbol_show=False
        )

        bar = Bar()
        bar.add_xaxis(xaxis_data=self.x_date)
        bar.add_yaxis(
            series_name="HIST",
            yaxis_data=self.histogram_data,
            xaxis_index=self.xaxis_index,
            yaxis_index=self.yaxis_index,
            itemstyle_opts=opts.ItemStyleOpts(
                color=JsCode(bar_color_function),
            )
        )
        bar.set_series_opts(
            label_opts=opts.LabelOpts(
                is_show=False
            ),
        )

        bar.set_global_opts(
            title_opts=opts.TitleOpts(title=self.title),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                is_scale=True,
                axispointer_opts=opts.AxisPointerOpts(
                    is_show=True,
                )
            ),
            yaxis_opts=opts.AxisOpts(
                is_scale=True
            ),
            datazoom_opts=[
                opts.DataZoomOpts(
                    range_start=Config.ZOOM_RANGE_START_PERCENT,
                    range_end=Config.ZOOM_RANGE_END_PERCENT
                ),
                opts.DataZoomOpts(
                    type_="inside",
                    range_start=Config.ZOOM_RANGE_START_PERCENT,
                    range_end=Config.ZOOM_RANGE_END_PERCENT
                )
            ],
        )

        bar.overlap(line)

        return bar

    def render_notebook(self):
        return self.get_chart().render_notebook()


class KdjLine:
    title = ""

    x_date = []
    slow_k = []
    slow_d = []
    slow_j = []

    xaxis_index = None
    yaxis_index = None

    def __init__(self, title, x_date, high_prices, low_prices, close_prices, j_type="3D-2K", xaxis_index=0, yaxis_index=0):
        self.title = title
        self.x_date = x_date
        self.xaxis_index = xaxis_index
        self.yaxis_index = yaxis_index

        self.slow_k, self.slow_d = talib.STOCH(high=high_prices, low=low_prices, close=close_prices)
        if j_type == "3D-2K":
            self.slow_j = self.slow_d * 3 - self.slow_k * 2

        elif j_type == "3K-2D":
            self.slow_j = self.slow_k * 3 - self.slow_d * 2

        elif j_type == "K-D":
            self.slow_j = self.slow_k - self.slow_d

        else:
            self.slow_j = self.slow_k - self.slow_d

        self.x_date = [item for item in self.x_date]
        self.slow_k = [item for item in self.slow_k]
        self.slow_d = [item for item in self.slow_d]
        self.slow_j = [item for item in self.slow_j]

    def get_chart(self):
        line = Line()
        line.add_xaxis(xaxis_data=self.x_date)
        line.add_yaxis(
            series_name="K",
            y_axis=self.slow_k,
            xaxis_index=self.xaxis_index,
            yaxis_index=self.yaxis_index,
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(
                width=1,
                color=Config.KDJ["k_color"],
            ),
        )

        line.add_yaxis(
            series_name="D",
            y_axis=self.slow_d,
            xaxis_index=self.xaxis_index,
            yaxis_index=self.yaxis_index,
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(
                width=1,
                color=Config.KDJ["d_color"],
            ),
        )

        line.add_yaxis(
            series_name="J",
            y_axis=self.slow_j,
            xaxis_index=self.xaxis_index,
            yaxis_index=self.yaxis_index,
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(
                width=1,
                color=Config.KDJ["j_color"],
            ),
        )

        line.set_series_opts(
            label_opts=opts.LabelOpts(
                is_show=False
            ),
        )
        line.set_global_opts(
            title_opts=opts.TitleOpts(title=self.title),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                is_scale=True,
                axispointer_opts=opts.AxisPointerOpts(
                    is_show=True,
                )
            ),
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
            ),
            datazoom_opts=[
                opts.DataZoomOpts(
                    range_start=Config.ZOOM_RANGE_START_PERCENT,
                    range_end=Config.ZOOM_RANGE_END_PERCENT
                ),
                opts.DataZoomOpts(
                    type_="inside",
                    range_start=Config.ZOOM_RANGE_START_PERCENT,
                    range_end=Config.ZOOM_RANGE_END_PERCENT
                )
            ],
        )

        return line

    def render_notebook(self):
        return self.get_chart().render_notebook()


class ProKline:
    """
    专业K线图
    """
    title = ""
    df = None

    def __init__(self, title, df):
        """
        :param title:
        :param df: pandas.DataFrame
        columes str_date、open_price、close_price、low_price、high_price、preclose_price、volume
        """
        self.title = title
        self.df = df

    def parse_data(self):
        str_dates = []
        candlestick_y_data = []
        volume_bar_y_data = []
        for idx, item in self.df.iterrows():
            str_dates.append(item["str_date"])
            candlestick_y_data.append([
                item["open_price"],
                item["close_price"],
                item["low_price"],
                item["high_price"]
            ])

            change_state = 1
            if item["close_price"] < item["preclose_price"]:
                change_state = -1

            volume_bar_y_data.append([idx, item["volume"], change_state])

        return {
            "str_dates": str_dates,
            "high_prices": self.df["high_price"],
            "low_prices": self.df["low_price"],
            "close_prices": self.df["close_price"],
            "candlestick_y_data": candlestick_y_data,
            "volume_bar_y_data": volume_bar_y_data,
        }

    def get_chart(self):
        grid_chart = Grid(init_opts=opts.InitOpts(
            height="800px",
            animation_opts=opts.AnimationOpts(animation=False),
        ))

        data = self.parse_data()

        candlestick_chart_index = 0
        volume_bar_chart_index = 1
        macd_chart_index = 2
        kdj_chart_index = 3
        xaxis_index = [candlestick_chart_index, volume_bar_chart_index, macd_chart_index, kdj_chart_index]

        candlestick_chart = Candlestick(title="CANDLESTICK", x_date=data["str_dates"], y_data=data["candlestick_y_data"], xaxis_index=candlestick_chart_index).get_chart()
        volume_bar_chart = VolumeBar(title="VOLUME", x_date=data["str_dates"], y_data=data["volume_bar_y_data"], xaxis_index=volume_bar_chart_index).get_chart()
        macd_chart = MacdChart(title="MACD", x_date=data["str_dates"], close_prices=data["close_prices"], xaxis_index=macd_chart_index).get_chart()
        kdj_chart = KdjLine(title="KDJ", x_date=data["str_dates"], high_prices=data["high_prices"], low_prices=data["low_prices"], close_prices=data["close_prices"], j_type="K-D", xaxis_index=kdj_chart_index, yaxis_index=kdj_chart_index).get_chart()

        candlestick_chart.set_global_opts(
            axispointer_opts=opts.AxisPointerOpts(
                is_show=True,
                link=[{"xAxisIndex": "all"}],
            ),
            datazoom_opts=[
                opts.DataZoomOpts(
                    xaxis_index=xaxis_index,
                    range_start=Config.ZOOM_RANGE_START_PERCENT,
                    range_end=Config.ZOOM_RANGE_END_PERCENT
                ),
                opts.DataZoomOpts(
                    type_="inside",
                    xaxis_index=xaxis_index,
                    range_start=Config.ZOOM_RANGE_START_PERCENT,
                    range_end=Config.ZOOM_RANGE_END_PERCENT
                )
            ],
            legend_opts=opts.LegendOpts(
                type_="scroll",
                pos_left="right"
            )
        )

        volume_bar_chart.set_global_opts(
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(is_show=False),
            ),
            yaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(is_show=False),
            ),
            legend_opts=opts.LegendOpts(
                type_="scroll",
                pos_left="right",
                pos_top="41%"
            )
        )

        macd_chart.set_global_opts(
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(is_show=False),
            ),
            yaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(is_show=False),
            ),
            legend_opts=opts.LegendOpts(
                type_="scroll",
                pos_left="right",
                pos_top="57%"
            )
        )

        kdj_chart.set_global_opts(
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(is_show=False),
            ),
            yaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(is_show=False),
            ),
            legend_opts=opts.LegendOpts(
                type_="scroll",
                pos_left="right",
                pos_top="78%"
            )
        )

        grid_chart.add(candlestick_chart, grid_opts=opts.GridOpts(
            pos_left="5%", pos_right="1%", height="30%"
        ))

        grid_chart.add(volume_bar_chart, grid_opts=opts.GridOpts(
            pos_left="5%", pos_right="1%", pos_top="41%", height="15%"
        ))

        grid_chart.add(macd_chart, grid_opts=opts.GridOpts(
            pos_left="5%", pos_right="1%", pos_top="57%", height="20%"
        ))

        grid_chart.add(kdj_chart, grid_opts=opts.GridOpts(
            pos_left="5%", pos_right="1%", pos_top="78%", height="15%"
        ))

        return grid_chart

    def render_notebook(self):
        return self.get_chart().render_notebook()

