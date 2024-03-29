import numpy as np
import scipy.stats

from TokenPool import TokenPool
from Trade import Trade


class AMM:
    safe_p_token_rate = 0.001

    def __init__(self, init_base_token_in_pool, twap_price, delta, g, fee_rate):
        self.base_token_in_pool = init_base_token_in_pool
        self.twap_price = twap_price
        self.delta = delta
        self.g = g
        self.init_p_token_in_pool = self.base_token_in_pool / twap_price
        self.p_token_in_pool = self.init_p_token_in_pool
        self.supply_invariant = self.base_token_in_pool * self.p_token_in_pool
        self.q = self.p_token_in_pool
        self.fee_rate = fee_rate
        self.trades = []
        self.auto_total_buy = 0
        self.auto_total_sell = 0
        self.auto_total_pnl = 0
        self.auto_total_fee = 0
        self.mm_total_buy = 0
        self.mm_total_sell = 0
        self.mm_total_pnl = 0
        self.mm_total_fee = 0
        self.total_buy = 0
        self.total_sell = 0
        self.total_pnl = 0
        self.total_fee = 0
        self.max_mm_rolled_pnl = 0
        self.max_auto_rolled_pnl = 0
        self.min_total_rolled_pnl = 0
        self.max_confidence_mm_rolled_pnl = 0
        self.max_confidence_auto_rolled_pnl = 0
        self.min_confidence_total_rolled_pnl = 0
        self.auto_pool = TokenPool()
        self.mm_pool = TokenPool()

    def __str__(self):
        key_values = []
        for key in self.__dict__.keys():
            if key != 'trades':
                key_values.append(f'"{key}": "{self.__dict__[key]}"')
        return '{' + ', '.join(key_values) + '}'

    def make_trade(self, base_token_from_buyer, target_price, timestamp, is_mm=False):
        trade = self._bonding_curve(base_token_from_buyer, target_price, timestamp, is_mm)
        trade = self._ans_model(trade)
        trade = self._pnl(trade)
        self.trades.append(trade)
        return trade

    def market_maker(self, target_price, timestamp):
        """
        Market maker should buy or sell mm_p_token_to_buyer to let market price near to the target_price.
        p_token_price = base_token_in_pool / (mm_p_token_to_buyer + p_token_in_pool)
        mm_p_token_to_buyer* = base_token_in_pool / p_token_price - p_token_in_pool
        but the mm_p_token_to_buyer* we have here is actually based on the average price
        we divide the token amount in half for now
        """
        mm_p_token_to_buyer = (self.base_token_in_pool / target_price - self.p_token_in_pool) / 2
        mm_base_token_from_buyer = self.supply_invariant / (
                self.p_token_in_pool + mm_p_token_to_buyer) - self.base_token_in_pool
        mm_base_token_from_buyer_with_fee = mm_base_token_from_buyer * (1 + self.fee_rate)
        if mm_base_token_from_buyer_with_fee != 0:
            self.make_trade(mm_base_token_from_buyer_with_fee, target_price, timestamp, True)

    def calculate_max_rolled_pnl(self):
        confidence = 0.95
        mm_trades_rolled_pnl = [trade.mm_rolled_pnl for trade in self.trades]
        auto_trades_rolled_pnl = [trade.auto_rolled_pnl for trade in self.trades]
        trades_rolled_pnl = [trade.rolled_pnl for trade in self.trades]
        self.max_mm_rolled_pnl = max(mm_trades_rolled_pnl)
        self.max_auto_rolled_pnl = max(auto_trades_rolled_pnl)
        self.min_total_rolled_pnl = min(trades_rolled_pnl)

        _mean, _min, _max = self._mean_confidence_interval(mm_trades_rolled_pnl, confidence)
        self.max_confidence_mm_rolled_pnl = _max

        _mean, _min, _max = self._mean_confidence_interval(auto_trades_rolled_pnl, confidence)
        self.max_confidence_auto_rolled_pnl = _max

        _mean, _min, _max = self._mean_confidence_interval(trades_rolled_pnl, confidence)
        self.min_confidence_total_rolled_pnl = _min

    @staticmethod
    def _mean_confidence_interval(data, confidence):
        a = 1.0 * np.array(data)
        n = len(a)
        m, se = np.mean(a), scipy.stats.sem(a)
        h = se * scipy.stats.t.ppf((1 + confidence) / 2., n - 1)
        return m, m - h, m + h

    def _bonding_curve(self, base_token_from_buyer, target_price, timestamp, is_mm=False):
        fee = abs(self.fee_rate * base_token_from_buyer)
        if is_mm:
            self.mm_total_fee += fee
        else:
            self.auto_total_fee += fee
        self.total_fee += fee
        base_token_from_buyer_without_fee = min([base_token_from_buyer - fee, base_token_from_buyer + fee], key=abs)
        """
        p_token_to_buyer = supply_invariant / (base_token_in_pool + base_token_from_buyer) - p_token_in_pool
        """
        p_token_to_buyer = self.supply_invariant / (
                self.base_token_in_pool + base_token_from_buyer_without_fee) - self.p_token_in_pool
        p_token_price = abs(base_token_from_buyer_without_fee / p_token_to_buyer)
        base_token_price = 1 / p_token_price
        self.base_token_in_pool += base_token_from_buyer_without_fee
        self.p_token_in_pool += p_token_to_buyer
        if self.p_token_in_pool < 0:
            raise ValueError(f'p_token_in_pool({self.p_token_in_pool}) is less than 0, timestamp: {timestamp}')
        if abs(self.p_token_in_pool) / self.init_p_token_in_pool < self.safe_p_token_rate:
            raise ValueError(
                f'p_token_in_pool({self.p_token_in_pool}) is less than safe_p_token_rate({self.safe_p_token_rate}) '
                f'of init_p_token_in_pool(){self.init_p_token_in_pool}), timestamp: {timestamp}')

        return Trade(
            p_token_to_buyer,
            self.p_token_in_pool,
            p_token_price,
            base_token_from_buyer,
            base_token_from_buyer_without_fee,
            fee,
            self.base_token_in_pool,
            base_token_price,
            None,
            None,
            None,
            None,
            None,
            timestamp,
            0,
            0,
            0,
            is_mm,
            target_price,
            None
        )

    def _ans_model(self, trade):
        _q = (self.q * trade.p_token_price - self.base_token_in_pool) / (
                self.q * trade.p_token_price + self.base_token_in_pool)
        trade.long_p_token_price = trade.p_token_price * (1.0 - _q * self.g + self.delta)
        trade.short_p_token_price = trade.p_token_price * (1.0 - _q * self.g - self.delta)
        self.q -= trade.p_token_to_buyer
        trade.q = self.q
        return trade

    def _amm_fee_model(self, trade):
        return trade

    def _pnl(self, trade):
        is_buy = trade.p_token_to_buyer < 0
        if is_buy:
            p_token_price = trade.long_p_token_price
            trade.pnl = trade.p_token_to_buyer * trade.long_p_token_price
        else:
            p_token_price = trade.short_p_token_price
            trade.pnl = trade.p_token_to_buyer * trade.short_p_token_price

        trade.buy = -trade.pnl if is_buy else 0
        trade.sell = trade.pnl if not is_buy else 0

        if trade.is_mm:
            self.mm_total_buy += trade.buy
            self.mm_total_sell += trade.sell
            self.mm_pool.trade(trade.p_token_to_buyer, p_token_price)
        else:
            self.auto_total_buy += trade.buy
            self.auto_total_sell += trade.sell
            self.auto_pool.trade(trade.p_token_to_buyer, p_token_price)

        self.total_buy += trade.buy
        self.total_sell += trade.sell
        trade.mm_rolled_pnl = self.mm_pool.realized_pnl + self.mm_pool.unrealized_pnl(p_token_price)
        self.mm_total_pnl = trade.mm_rolled_pnl
        trade.auto_rolled_pnl = self.auto_pool.realized_pnl + self.auto_pool.unrealized_pnl(p_token_price)
        self.auto_total_pnl = trade.auto_rolled_pnl
        trade.rolled_pnl = -(trade.mm_rolled_pnl + trade.auto_rolled_pnl)
        self.total_pnl = trade.rolled_pnl

        return trade
