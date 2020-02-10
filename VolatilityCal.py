import datetime
import statistics

import numpy as np


class VolatilityCal:
    def __init__(self, rolling_period=7):
        self.name = ""
        self.daily_twaps = []
        self.minutely_candles = []
        self.last_date_idx = None
        self.last_volatility = None
        self.rolling_period = rolling_period

    def update(self, timestamp, price):
        """
        This function needs to be called in timestamp order.
        :param timestamp:
        :param price:
        :return:
        """
        _datetime = self.to_datetime(timestamp)
        date_idx = _datetime.strftime("%Y-%m-%d")
        datetime_idx = _datetime.strftime("%Y-%m-%dT%H:%M")

        if not self.last_date_idx:
            self.last_date_idx = date_idx

        if date_idx != self.last_date_idx:
            sum = 0
            for candle in self.minutely_candles:
                sum += (candle.open + candle.high + candle.low + candle.close) / 4
            daily_twap = sum / self.minutely_candles.__len__()
            self.daily_twaps.append(Twap(self.last_date_idx, daily_twap))
            self.minutely_candles = []
            self.last_date_idx = date_idx

            if self.daily_twaps.__len__() >= self.rolling_period + 1:
                log_returns = []
                for i in range(-self.rolling_period, 0, 1):
                    log_return = np.log(self.daily_twaps[i].twap / self.daily_twaps[i - 1].twap)
                    log_returns.append(log_return)
                self.last_volatility = statistics.stdev(log_returns) * np.math.sqrt(365)

        if _datetime.hour >= 23:
            if not self.minutely_candles:
                self.minutely_candles.append(Candle(datetime_idx))
            last_candle = self.minutely_candles[-1]
            if last_candle.datetime_idx > datetime_idx:
                raise ValueError(f'datetime_idx: ${last_candle.datetime_idx} > ${datetime_idx}')
            elif last_candle.datetime_idx == datetime_idx:
                last_candle.update_price(price)
            else:
                self.minutely_candles.append(Candle(datetime_idx))
                self.minutely_candles[-1].update_price(price)

    @staticmethod
    def to_datetime(timestamp):
        return datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f %Z')


class Twap:
    def __init__(self, date_idx, twap=None):
        self.date_idx = date_idx
        self.twap = twap


class Candle:
    def __init__(self, datetime_idx, open=None, high=None, low=None, close=None):
        self.datetime_idx = datetime_idx
        self.open = open
        self.high = high
        self.low = low
        self.close = close

    def update_price(self, price):
        if self.open is None:
            self.open = price

        if self.high is None:
            self.high = price
        elif price > self.high:
            self.high = price

        if self.low is None:
            self.low = price
        elif price < self.low:
            self.low = price

        self.close = price
