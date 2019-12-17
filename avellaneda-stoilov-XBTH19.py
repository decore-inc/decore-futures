from math import sqrt
import pandas as pd
import numpy as np
from fractions import Fraction

filename = 'sources/XBTH19_trade.csv'
chunksize = 10 ** 8
init_base_token_in_pool = 10.0 ** 8
base_token_in_pool = init_base_token_in_pool
TWAP_price = 3602
p_token_in_pool = base_token_in_pool / TWAP_price
supply_invariant = base_token_in_pool * p_token_in_pool
q = 0
upper_delta = 1 * 0.01
G = 10 * 0.01

result = []
rolled_pnl = 0
rolled_buy = 0
rolled_sell = 0
mm_rolled_pnl = 0
mm_rolled_buy = 0
mm_rolled_sell = 0
for chunk in pd.read_csv(filename, chunksize=chunksize):
    df = pd.DataFrame(chunk, columns=['size', 'side', 'price', 'timestamp'])
    count = 0
    for delta in df.values:
        if count > 100: break

        side = delta[1]
        p_token_to_buyer = -delta[0] if side == 'Buy' else delta[0]  # Negative if Buy
        target_price = delta[2]
        timestamp = delta[3]
        is_mm = False
        p_token_in_pool += p_token_to_buyer
        base_token_price = p_token_to_buyer / (base_token_in_pool - (supply_invariant / p_token_in_pool))
        p_token_price = 1 / base_token_price
        base_token_from_buyer = - p_token_to_buyer * p_token_price
        base_token_in_pool += base_token_from_buyer
        q -= p_token_to_buyer
        _q = (q * p_token_price - base_token_in_pool) / (q * p_token_price + base_token_in_pool)
        long_p_token_price = p_token_price * (1.0 - _q * G + upper_delta)
        short_p_token_price = p_token_price * (1.0 - _q * G - upper_delta)

        isBuy = p_token_to_buyer < 0
        if isBuy:
            pnl = p_token_to_buyer * long_p_token_price
        else:
            pnl = p_token_to_buyer * short_p_token_price
        rolled_pnl += pnl
        buy = -pnl if isBuy else 0
        sell = pnl if not isBuy else 0
        rolled_buy += buy
        rolled_sell += sell

        result.append([
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
            target_price
        ])

        # Market maker should buy or sell mm_p_token_to_buyer to let market price near to the target_price
        # To get mm_p_token_to_buyer from formulas below:
        # base_token_price = mm_p_token_to_buyer / (base_token_in_pool - (supply_invariant / (p_token_in_pool + mm_p_token_to_buyer)))
        # target_price = 1 / base_token_price
        # Resolve this Quadratic Equation: ax^2 + bx + c = 0
        # target_price * mm_p_token_to_buyer^2 + (target_price * p_token_in_pool  - base_token_in_pool)* mm_p_token_to_buyer - base_token_in_pool * p_token_in_pool + supply_invariant = 0
        a = target_price
        b = target_price * p_token_in_pool - base_token_in_pool
        c = - base_token_in_pool * p_token_in_pool + supply_invariant
        _result = sqrt(b ** 2 - 4 * a * c)
        results = [(-b + _result) / (2 * a), (-b - _result) / (2 * a)]
        mm_p_token_to_buyer = max(results, key=abs) # find the nearest to zero
        mm_p_token_to_buyer = round(mm_p_token_to_buyer)
        if mm_p_token_to_buyer != 0:
            is_mm = True
            p_token_in_pool += mm_p_token_to_buyer
            base_token_price = mm_p_token_to_buyer / (base_token_in_pool - (supply_invariant / p_token_in_pool))
            p_token_price = 1 / base_token_price
            base_token_from_buyer = - mm_p_token_to_buyer * p_token_price
            base_token_in_pool += base_token_from_buyer
            q -= mm_p_token_to_buyer
            _q = (q * p_token_price - base_token_in_pool) / (q * p_token_price + base_token_in_pool)
            long_p_token_price = p_token_price * (1.0 - _q * G + upper_delta)
            short_p_token_price = p_token_price * (1.0 - _q * G - upper_delta)

            isBuy = mm_p_token_to_buyer < 0
            if isBuy:
                mm_pnl = mm_p_token_to_buyer * long_p_token_price
            else:
                mm_pnl = mm_p_token_to_buyer * short_p_token_price
            mm_rolled_pnl += mm_pnl
            mm_buy = -mm_pnl if isBuy else 0
            mm_sell = mm_pnl if not isBuy else 0
            mm_rolled_buy += mm_buy
            mm_rolled_sell += mm_sell
            result.append([
                mm_p_token_to_buyer,
                p_token_in_pool,
                p_token_price,
                base_token_from_buyer,
                base_token_in_pool,
                base_token_price,
                long_p_token_price,
                short_p_token_price,
                mm_pnl,
                mm_buy,
                mm_sell,
                timestamp,
                mm_rolled_pnl,
                mm_rolled_buy,
                mm_rolled_sell,
                is_mm,
                target_price
            ])

        count += 1
total_buy = rolled_buy
total_sell = rolled_sell
total_pnl = rolled_buy - rolled_sell
total_pnl_rate = total_pnl / (total_buy + total_sell)
print(total_buy)
print(total_sell)
print(total_pnl)
print(total_pnl_rate)
data = np.array(result)
df2 = pd.DataFrame(
    {
        'p_token_to_buyer': data[:, 0],
        'p_token_in_pool': data[:, 1],
        'p_token_price': data[:, 2],
        'base_token_from_buyer': data[:, 3],
        'base_token_in_pool': data[:, 4],
        'base_token_price': data[:, 5],
        'long_p_token_price': data[:, 6],
        'short_p_token_price': data[:, 7],
        'pnl': data[:, 8],
        'buy': data[:, 9],
        'sell': data[:, 10],
        'timestamp': data[:, 11],
        'rolled_pnl': data[:, 12],
        'rolled_buy': data[:, 13],
        'rolled_sell': data[:, 14],
        'is_mm': data[:, 15],
        'target_price': data[:, 16]},
    columns=['p_token_to_buyer',
             'p_token_in_pool',
             'p_token_price',
             'base_token_from_buyer',
             'base_token_in_pool',
             'base_token_price',
             'long_p_token_price',
             'short_p_token_price',
             'pnl',
             'buy',
             'sell',
             'timestamp',
             'rolled_pnl',
             'rolled_buy',
             'rolled_sell',
             'is_mm',
             'target_price'])
init_base_token_in_pool = '{:.2e}'.format(init_base_token_in_pool)
TWAP = '{:.2e}'.format(TWAP_price)
df2.to_csv(f'results/XBTH19-base_token_in_pool={init_base_token_in_pool}-TWAP={TWAP}-delta={upper_delta}-G={G}.csv', index=None, header=True)
