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

    def test_update_not_in_time_range(self):
        vol_cal = VolatilityCal()
        vol_cal.update("2017-04-27 14:03:09.306 UTC", 0.0446)
        self.assertTrue(not vol_cal.minutely_candles)

    def test_update(self):
        vol_cal = VolatilityCal()
        vol_cal.update("2017-04-27 23:03:09.306 UTC", 0.0446)
        self.assertEqual(vol_cal.minutely_candles.__len__(), 1)
        candle = vol_cal.minutely_candles[-1]
        self.assertEqual(candle.datetime_idx, "2017-04-27T23:03")
        self.assertEqual(candle.open, 0.0446)
        self.assertEqual(candle.high, 0.0446)
        self.assertEqual(candle.low, 0.0446)
        self.assertEqual(candle.close, 0.0446)
        self.assertTrue(not vol_cal.daily_twaps)

        vol_cal.update("2017-04-27 23:03:19.306 UTC", 0.0546)
        self.assertEqual(vol_cal.minutely_candles.__len__(), 1)
        candle = vol_cal.minutely_candles[-1]
        self.assertEqual(candle.datetime_idx, "2017-04-27T23:03")
        self.assertEqual(candle.open, 0.0446)
        self.assertEqual(candle.high, 0.0546)
        self.assertEqual(candle.low, 0.0446)
        self.assertEqual(candle.close, 0.0546)
        self.assertTrue(not vol_cal.daily_twaps)

        vol_cal.update("2017-04-27 23:03:29.306 UTC", 0.0346)
        self.assertEqual(vol_cal.minutely_candles.__len__(), 1)
        candle = vol_cal.minutely_candles[-1]
        self.assertEqual(candle.datetime_idx, "2017-04-27T23:03")
        self.assertEqual(candle.open, 0.0446)
        self.assertEqual(candle.high, 0.0546)
        self.assertEqual(candle.low, 0.0346)
        self.assertEqual(candle.close, 0.0346)
        self.assertTrue(not vol_cal.daily_twaps)

        vol_cal.update("2017-04-27 23:04:09.306 UTC", 0.0246)
        self.assertEqual(vol_cal.minutely_candles.__len__(), 2)
        candle = vol_cal.minutely_candles[-1]
        self.assertEqual(candle.datetime_idx, "2017-04-27T23:04")
        self.assertEqual(candle.open, 0.0246)
        self.assertEqual(candle.high, 0.0246)
        self.assertEqual(candle.low, 0.0246)
        self.assertEqual(candle.close, 0.0246)
        self.assertTrue(not vol_cal.daily_twaps)

        vol_cal.update("2017-04-28 23:03:09.306 UTC", 0.0446)
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
        self.assertTrue(not vol_cal.volatility)

    def test_update_volatility(self):
        vol_cal = VolatilityCal()
        vol_cal.update("2017-04-01 23:03:09.306 UTC", 6.70)
        vol_cal.update("2017-04-02 23:03:09.306 UTC", 6.50)
        vol_cal.update("2017-04-03 23:03:09.306 UTC", 7.45)
        vol_cal.update("2017-04-04 23:03:09.306 UTC", 7.40)
        vol_cal.update("2017-04-05 23:03:09.306 UTC", 7.25)
        vol_cal.update("2017-04-06 23:03:09.306 UTC", 7.15)
        vol_cal.update("2017-04-07 23:03:09.306 UTC", 7.25)
        vol_cal.update("2017-04-08 23:03:09.306 UTC", 7.00)
        vol_cal.update("2017-04-09 23:03:09.306 UTC", 7.00)
        self.assertEqual(vol_cal.volatility, 1.139230204054311)


