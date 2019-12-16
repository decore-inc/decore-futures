import pandas as pd
import numpy as np

filename = 'sources/TRXZ19_size_with_sign.csv'
chunksize = 10 ** 8
base_token_in_pool = 10.0 ** 8
TWAP = 60
p_token_in_pool = base_token_in_pool / TWAP
supply_invariant = base_token_in_pool * p_token_in_pool
minted_long_p_token = p_token_in_pool / 2
minted_short_p_token = p_token_in_pool / 2
q = minted_long_p_token - minted_short_p_token
upper_delta = 1 * 0.01
G = 10 * 0.01

result = []
rolled_pnl = 0
rolled_buy = 0
rolled_sell = 0
for chunk in pd.read_csv(filename, chunksize=chunksize):
    df = pd.DataFrame(chunk, columns=['size', 'timestamp'])
    for delta in df.values:
        size = delta[0]  # Negative if Buy
        timestamp = delta[1]

        base_token_in_pool += size
        p_token_in_pool = base_token_in_pool / TWAP
        p_token_price = size / (p_token_in_pool - (supply_invariant / base_token_in_pool))
        supply_invariant = base_token_in_pool * p_token_in_pool
        if size > 0:
            minted_long_p_token = (minted_long_p_token - size) / TWAP
        else:
            minted_short_p_token = (minted_short_p_token + size) / TWAP
        q = minted_long_p_token - minted_short_p_token
        _q = (q * p_token_price - base_token_in_pool) / (q * p_token_price + base_token_in_pool)
        long_p_token_price = p_token_price * (1.0 - _q * G + upper_delta)
        short_p_token_price = p_token_price * (1.0 - _q * G - upper_delta)

        pnl = size * p_token_price
        rolled_pnl += pnl
        buy = -pnl if size < 0 else 0
        sell = pnl if size > 0 else 0
        rolled_buy += buy
        rolled_sell += sell

        result.append([
            size,
            base_token_in_pool,
            p_token_price,
            minted_long_p_token,
            minted_short_p_token,
            long_p_token_price,
            short_p_token_price,
            pnl,
            buy,
            sell,
            timestamp,
            rolled_pnl,
            rolled_buy,
            rolled_sell
        ])
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
        'size': data[:, 0],
        'base_token_in_pool': data[:, 1],
        'p_token_price': data[:, 2],
        'minted_long_p_token': data[:, 3],
        'minted_short_p_token': data[:, 4],
        'long_p_token_price': data[:, 5],
        'short_p_token_price': data[:, 6],
        'pnl': data[:, 7],
        'buy': data[:, 8],
        'sell': data[:, 9],
        'timestamp': data[:, 10],
        'rolled_pnl': data[:, 11],
        'rolled_buy': data[:, 12],
        'rolled_sell': data[:, 13]},
    columns=['size',
             'base_token_in_pool',
             'p_token_price',
             'minted_long_p_token',
             'minted_short_p_token',
             'long_p_token_price',
             'short_p_token_price',
             'pnl',
             'buy',
             'sell',
             'timestamp',
             'rolled_pnl',
             'rolled_buy',
             'rolled_sell'])
df2.to_csv('results/avellaneda-stoilov-TRXZ19.csv', index=None, header=True)
