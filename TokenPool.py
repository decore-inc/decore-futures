class TokenPool:
    def __init__(self):
        self.realized_pnl = 0
        self.trades = []
        self.q = 0
        self.pnl_diff = 0

    def trade(self, p_token_to_buyer, p_token_price):
        assert p_token_to_buyer != 0

        is_buy = p_token_to_buyer < 0
        if is_buy:
            if self.q <= 0:
                self.trades.append(TokenPoolItem(p_token_to_buyer, p_token_price))
            else:
                remaining = -p_token_to_buyer
                while True:
                    p_token_to_buyer_in_trade = self.trades[0].p_token_to_buyer
                    if p_token_to_buyer_in_trade <= remaining:
                        remaining -= p_token_to_buyer_in_trade
                        self.realized_pnl -= p_token_to_buyer_in_trade * (p_token_price - self.trades[0].p_token_price)
                        self.trades.pop(0)
                        if self.trades.__len__() == 0:
                            break
                    else:
                        self.trades[0].p_token_to_buyer -= remaining
                        self.realized_pnl -= remaining * (p_token_price - self.trades[0].p_token_price)
                        remaining = 0
                        break
                if remaining > 0:
                    self.trades.append(TokenPoolItem(-remaining, p_token_price))
        else:
            if self.q >= 0:
                self.trades.append(TokenPoolItem(p_token_to_buyer, p_token_price))
            else:
                remaining = p_token_to_buyer
                while True:
                    p_token_to_buyer_in_trade = -self.trades[0].p_token_to_buyer
                    if p_token_to_buyer_in_trade <= remaining:
                        remaining -= p_token_to_buyer_in_trade
                        self.realized_pnl += p_token_to_buyer_in_trade * (p_token_price - self.trades[0].p_token_price)
                        self.trades.pop(0)
                        if self.trades.__len__() == 0:
                            break
                    else:
                        self.trades[0].p_token_to_buyer += remaining
                        self.realized_pnl += remaining * (p_token_price - self.trades[0].p_token_price)
                        remaining = 0
                        break
                if remaining > 0:
                    self.trades.append(TokenPoolItem(remaining, p_token_price))

        self.q += p_token_to_buyer
        self.pnl_diff += p_token_to_buyer * (0 - p_token_price)

    def unrealized_pnl(self, p_token_price):
        return -(p_token_price * self.q + self.pnl_diff + self.realized_pnl)


class TokenPoolItem:
    def __init__(self, p_token_to_buyer, p_token_price):
        self.p_token_to_buyer = p_token_to_buyer
        self.p_token_price = p_token_price
