from unittest import TestCase

from AvgVolCal import AvgVolCal


class TestAvgVolCal(TestCase):
    def test_update(self):
        avg_vol_cal = AvgVolCal()
        avg_vol_cal.update("2017-04-01 23:03:09.306 UTC", 6.70)
        avg_vol_cal.update("2017-04-02 23:03:09.306 UTC", 6.50)
        avg_vol_cal.update("2017-04-03 23:03:09.306 UTC", 7.45)
        avg_vol_cal.update("2017-04-04 23:03:09.306 UTC", 7.40)
        avg_vol_cal.update("2017-04-05 23:03:09.306 UTC", 7.25)
        avg_vol_cal.update("2017-04-06 23:03:09.306 UTC", 7.15)
        avg_vol_cal.update("2017-04-07 23:03:09.306 UTC", 7.25)
        avg_vol_cal.update("2017-04-08 23:03:09.306 UTC", 7.00)
        avg_vol_cal.update("2017-04-09 23:03:09.306 UTC", 7.00)
        self.assertEqual(avg_vol_cal.avg_vol, 7.142857142857143)
