from math import sqrt
from Trade import Trade


class AMM:
    trades = []
    total_buy = 0
    total_sell = 0
    total_pnl = 0
    total_pnl_rate = 0
    mm_total_buy = 0
    mm_total_sell = 0
    mm_total_pnl = 0
    mm_total_pnl_rate = 0

    def __init__(self, init_base_token_in_pool, twap_price, delta, g):
        self.base_token_in_pool = init_base_token_in_pool
        self.twap_price = twap_price
        self.delta = delta
        self.g = g
        self.p_token_in_pool = self.base_token_in_pool / twap_price
        self.supply_invariant = self.base_token_in_pool * self.p_token_in_pool
        self.q = 0

    def make_trade(self, base_token_from_buyer, target_price, timestamp, is_mm=False):
        trade = self._bonding_curve(base_token_from_buyer, timestamp, target_price, is_mm)
        trade = self._ans_model(trade)
        trade = self._pnl(trade)
        self.trades.append(trade)
        return trade

    def market_maker(self, target_price, timestamp):
        """
        Market maker should buy or sell mm_p_token_to_buyer to let market price near to the target_price.
        To get mm_p_token_to_buyer as X from formulas below:
        target_price = mm_base_token_from_buyer /( (p_token_in_pool - supply_invariant / (base_token_in_pool + mm_base_token_from_buyer)))
        Resolve this Quadratic Equation: aX^2 + bX + c = 0
        X**2 + (base_token_in_pool - p_token_in_pool * target_price) * X - p_token_in_pool * target_price * base_token_in_pool + supply_invariant * target_price = 0
        """
        a = 1
        b = self.base_token_in_pool - self.p_token_in_pool * target_price
        c = - self.p_token_in_pool * target_price * self.base_token_in_pool + self.supply_invariant * target_price
        """
        c = 0 because self.p_token_in_pool * self.base_token_in_pool = self.supply_invariant
        """
        _result = sqrt(b ** 2 - 4 * a * c)
        results = [(-b + _result) / (2 * a), (-b - _result) / (2 * a)]
        mm_base_token_from_buyer = max(results, key=abs)  # find the nearest to zero
        mm_base_token_from_buyer = round(mm_base_token_from_buyer)
        if mm_base_token_from_buyer != 0:
            self.make_trade(mm_base_token_from_buyer, target_price, timestamp, True)

    def _bonding_curve(self, base_token_from_buyer, timestamp, target_price, is_mm=False):
        self.base_token_in_pool += base_token_from_buyer
        p_token_price = base_token_from_buyer / (self.p_token_in_pool - self.supply_invariant/self.base_token_in_pool)
        base_token_price = 1 / p_token_price
        p_token_to_buyer = - base_token_from_buyer / p_token_price
        self.p_token_in_pool += p_token_to_buyer
        return Trade(
            p_token_to_buyer,
            self.p_token_in_pool,
            p_token_price,
            base_token_from_buyer,
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
            target_price
        )

    def _ans_model(self, trade):
        self.q -= trade.p_token_to_buyer
        _q = (self.q * trade.p_token_price - self.base_token_in_pool) / (
                    self.q * trade.p_token_price + self.base_token_in_pool)
        trade.long_p_token_price = trade.p_token_price * (1.0 - _q * self.g + self.delta)
        trade.short_p_token_price = trade.p_token_price * (1.0 - _q * self.g - self.delta)
        return trade

    def _pnl(self, trade):
        isBuy = trade.p_token_to_buyer < 0
        if isBuy:
            trade.pnl = trade.p_token_to_buyer * trade.long_p_token_price
        else:
            trade.pnl = trade.p_token_to_buyer * trade.short_p_token_price
        trade.rolled_pnl += trade.pnl
        trade.buy = -trade.pnl if isBuy else 0
        trade.sell = trade.pnl if not isBuy else 0
        trade.rolled_buy += trade.buy
        trade.rolled_sell += trade.sell
        if trade.is_mm:
            self.mm_total_buy += trade.buy
            self.mm_total_sell += trade.sell
            self.mm_total_pnl += trade.pnl
            self.mm_total_pnl_rate = self.mm_total_pnl / (self.mm_total_buy + self.mm_total_sell)
        self.total_buy += trade.buy
        self.total_sell += trade.sell
        self.total_pnl += trade.pnl
        self.total_pnl_rate = self.total_pnl / (self.total_buy + self.total_sell)
        return trade
