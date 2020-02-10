import datetime


class AvgVolCal:
    def __init__(self, rolling_period=7):
        self.last_date_idx = None
        self.rolling_period = rolling_period
        self.vols = []
        self.last_vol = 0
        self.avg_vol = None

    def update(self, timestamp, vol):
        """
        This function needs to be called in timestamp order.
        :param timestamp:
        :param vol:
        """
        _datetime = self.to_datetime(timestamp)
        date_idx = _datetime.strftime("%Y-%m-%d")

        if not self.last_date_idx:
            self.last_date_idx = date_idx

        if date_idx != self.last_date_idx:
            self.vols.append(Vol(self.last_vol, self.last_vol))
            self.last_vol = 0

            if self.vols.__len__() >= self.rolling_period + 1:
                sum = 0
                for i in range(-self.rolling_period, 0, 1):
                    sum += self.vols[i].vol
                self.avg_vol = sum / self.rolling_period

        self.last_vol += vol

    @staticmethod
    def to_datetime(timestamp):
        return datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f %Z')


class Vol:
    def __init__(self, date_idx, vol):
        self.date_idx = date_idx
        self.vol = vol
