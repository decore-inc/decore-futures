from unittest import TestCase

from VolatilityCal import VolatilityCal


class TestVolatilityCal(TestCase):
    def test_to_datetime(self):
        vol_cal = VolatilityCal()
        datetime = vol_cal.to_datetime("2017-04-27 14:03:09.306 UTC")
        self.assertEqual(datetime.year, 2017)
        self.assertEqual(datetime.month, 4)
        self.assertEqual(datetime.day, 27)
        self.assertEqual(datetime.hour, 14)
        self.assertEqual(datetime.minute, 3)
        self.assertEqual(datetime.second, 9)

    def test_update_volatility_not_in_time_range(self):
        vol_cal = VolatilityCal()
        vol_cal.update_volatility("2017-04-27 14:03:09.306 UTC", 0.0446)
        self.assertTrue(not vol_cal.minutely_candles)

    def test_update_volatility(self):
        vol_cal = VolatilityCal()
        vol_cal.update_volatility("2017-04-27 23:03:09.306 UTC", 0.0446)
        self.assertEqual(vol_cal.minutely_candles.__len__(), 1)
        candle = vol_cal.minutely_candles[-1]
        self.assertEqual(candle.datetime_idx, "2017-04-27T23:03")
        self.assertEqual(candle.open, 0.0446)
        self.assertEqual(candle.high, 0.0446)
        self.assertEqual(candle.low, 0.0446)
        self.assertEqual(candle.close, 0.0446)
        self.assertTrue(not vol_cal.daily_twaps)

        vol_cal.update_volatility("2017-04-27 23:03:19.306 UTC", 0.0546)
        self.assertEqual(vol_cal.minutely_candles.__len__(), 1)
        candle = vol_cal.minutely_candles[-1]
        self.assertEqual(candle.datetime_idx, "2017-04-27T23:03")
        self.assertEqual(candle.open, 0.0446)
        self.assertEqual(candle.high, 0.0546)
        self.assertEqual(candle.low, 0.0446)
        self.assertEqual(candle.close, 0.0546)
        self.assertTrue(not vol_cal.daily_twaps)

        vol_cal.update_volatility("2017-04-27 23:03:29.306 UTC", 0.0346)
        self.assertEqual(vol_cal.minutely_candles.__len__(), 1)
        candle = vol_cal.minutely_candles[-1]
        self.assertEqual(candle.datetime_idx, "2017-04-27T23:03")
        self.assertEqual(candle.open, 0.0446)
        self.assertEqual(candle.high, 0.0546)
        self.assertEqual(candle.low, 0.0346)
        self.assertEqual(candle.close, 0.0346)
        self.assertTrue(not vol_cal.daily_twaps)

        vol_cal.update_volatility("2017-04-27 23:04:09.306 UTC", 0.0246)
        self.assertEqual(vol_cal.minutely_candles.__len__(), 2)
        candle = vol_cal.minutely_candles[-1]
        self.assertEqual(candle.datetime_idx, "2017-04-27T23:04")
        self.assertEqual(candle.open, 0.0246)
        self.assertEqual(candle.high, 0.0246)
        self.assertEqual(candle.low, 0.0246)
        self.assertEqual(candle.close, 0.0246)
        self.assertTrue(not vol_cal.daily_twaps)

        vol_cal.update_volatility("2017-04-28 23:03:09.306 UTC", 0.0446)
        self.assertEqual(vol_cal.minutely_candles.__len__(), 1)
        candle = vol_cal.minutely_candles[-1]
        self.assertEqual(candle.datetime_idx, "2017-04-28T23:03")
        self.assertEqual(candle.open, 0.0446)
        self.assertEqual(candle.high, 0.0446)
        self.assertEqual(candle.low, 0.0446)
        self.assertEqual(candle.close, 0.0446)
        self.assertEqual(vol_cal.daily_twaps.__len__(), 1)
        self.assertEqual(vol_cal.daily_twaps[-1].date_idx, "2017-04-27")
        self.assertEqual(vol_cal.daily_twaps[-1].twap, 0.03335)

