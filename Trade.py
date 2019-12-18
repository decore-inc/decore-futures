class Trade:
    def __init__(self,
                 p_token_to_buyer,
                 p_token_in_pool,
                 p_token_price,
                 base_token_from_buyer,
                 base_token_in_pool,
                 base_token_price,
                 long_p_token_price,
                 short_p_token_price,
                 pnl,
                 buy,
                 sell,
                 timestamp,
                 rolled_pnl,
                 rolled_buy,
                 rolled_sell,
                 is_mm,
                 target_price,
                 q):
        self.p_token_to_buyer = p_token_to_buyer
        self.p_token_in_pool = p_token_in_pool
        self.p_token_price = p_token_price
        self.base_token_from_buyer = base_token_from_buyer
        self.base_token_in_pool = base_token_in_pool
        self.base_token_price = base_token_price
        self.long_p_token_price = long_p_token_price
        self.short_p_token_price = short_p_token_price
        self.pnl = pnl
        self.buy = buy
        self.sell = sell
        self.timestamp = timestamp
        self.rolled_pnl = rolled_pnl
        self.rolled_buy = rolled_buy
        self.rolled_sell = rolled_sell
        self.is_mm = is_mm
        self.target_price = target_price
        self.q = q


