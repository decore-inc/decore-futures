from unittest import TestCase

from TokenPool import TokenPool


class TestTokenPool(TestCase):
    def test_trade_buy(self):
        pool = TokenPool()

        pool.trade(-1, 100)
        self.assertEqual(pool.unrealized_pnl(110), 10)
        self.assertEqual(pool.realized_pnl, 0)
        self.assertEqual(pool.q(), -1)

        pool.trade(-2, 120)
        self.assertEqual(pool.unrealized_pnl(130), 50)
        self.assertEqual(pool.realized_pnl, 0)
        self.assertEqual(pool.q(), -3)

    def test_trade_sell(self):
        pool = TokenPool()

        pool.trade(1, 100)
        self.assertEqual(pool.unrealized_pnl(110), -10)
        self.assertEqual(pool.realized_pnl, 0)
        self.assertEqual(pool.q(), 1)

        pool.trade(2, 120)
        self.assertEqual(pool.unrealized_pnl(130), -50)
        self.assertEqual(pool.realized_pnl, 0)
        self.assertEqual(pool.q(), 3)

    def test_trade_even(self):
        pool = TokenPool()

        pool.trade(-1, 100)
        self.assertEqual(pool.unrealized_pnl(110), 10)
        self.assertEqual(pool.realized_pnl, 0)
        self.assertEqual(pool.q(), -1)

        pool.trade(1, 120)
        self.assertEqual(pool.unrealized_pnl(130), 0)
        self.assertEqual(pool.realized_pnl, 20)
        self.assertEqual(pool.q(), 0)

    def test_trade_even_2(self):
        pool = TokenPool()

        pool.trade(1, 100)
        self.assertEqual(pool.unrealized_pnl(110), -10)
        self.assertEqual(pool.realized_pnl, 0)
        self.assertEqual(pool.q(), 1)

        pool.trade(-1, 120)
        self.assertEqual(pool.unrealized_pnl(130), 0)
        self.assertEqual(pool.realized_pnl, -20)
        self.assertEqual(pool.q(), 0)

    def test_trade_sell_more(self):
        pool = TokenPool()

        pool.trade(-1, 100)
        self.assertEqual(pool.unrealized_pnl(110), 10)
        self.assertEqual(pool.realized_pnl, 0)
        self.assertEqual(pool.q(), -1)

        pool.trade(2, 120)
        self.assertEqual(pool.unrealized_pnl(130), -10)
        self.assertEqual(pool.realized_pnl, 20)
        self.assertEqual(pool.q(), 1)

        pool.trade(3, 140)
        self.assertEqual(pool.unrealized_pnl(150), -60)
        self.assertEqual(pool.realized_pnl, 20)
        self.assertEqual(pool.q(), 4)

        pool.trade(-5, 160)
        self.assertEqual(pool.unrealized_pnl(170), 10)
        self.assertEqual(pool.realized_pnl, 20-20*3-40*1)
        self.assertEqual(pool.q(), -1)

    def test_trade_buy_more(self):
        pool = TokenPool()

        pool.trade(1, 100)
        self.assertEqual(pool.unrealized_pnl(110), -10)
        self.assertEqual(pool.realized_pnl, 0)
        self.assertEqual(pool.q(), 1)

        pool.trade(-2, 120)
        self.assertEqual(pool.unrealized_pnl(130), 10)
        self.assertEqual(pool.realized_pnl, -20)
        self.assertEqual(pool.q(), -1)

        pool.trade(-3, 140)
        self.assertEqual(pool.unrealized_pnl(150), 60)
        self.assertEqual(pool.realized_pnl, -20)
        self.assertEqual(pool.q(), -4)

        pool.trade(5, 160)
        self.assertEqual(pool.unrealized_pnl(170), -10)
        self.assertEqual(pool.realized_pnl, -(20-20*3-40*1))
        self.assertEqual(pool.q(), 1)

    def test_trade_buy_sell_half(self):
        pool = TokenPool()

        pool.trade(-2, 100)
        self.assertEqual(pool.unrealized_pnl(110), 20)
        self.assertEqual(pool.realized_pnl, 0)
        self.assertEqual(pool.q(), -2)

        pool.trade(1, 120)
        self.assertEqual(pool.unrealized_pnl(130), 30)
        self.assertEqual(pool.realized_pnl, 20)
        self.assertEqual(pool.q(), -1)

        pool.trade(1, 140)
        self.assertEqual(pool.unrealized_pnl(150), 0)
        self.assertEqual(pool.realized_pnl, 60)
        self.assertEqual(pool.q(), 0)

    def test_trade_sell_buy_half(self):
        pool = TokenPool()

        pool.trade(2, 100)
        self.assertEqual(pool.unrealized_pnl(110), -20)
        self.assertEqual(pool.realized_pnl, 0)
        self.assertEqual(pool.q(), 2)

        pool.trade(-1, 120)
        self.assertEqual(pool.unrealized_pnl(130), -30)
        self.assertEqual(pool.realized_pnl, -20)
        self.assertEqual(pool.q(), 1)

        pool.trade(-1, 140)
        self.assertEqual(pool.unrealized_pnl(150), 0)
        self.assertEqual(pool.realized_pnl, -60)
        self.assertEqual(pool.q(), 0)
