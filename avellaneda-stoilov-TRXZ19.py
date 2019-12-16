import pandas as pd
import numpy as np

filename = 'sources/TRXZ19_size_with_sign.csv'
chunksize = 10 ** 8
init_base_token_in_pool = 10.0 ** 7
base_token_in_pool = init_base_token_in_pool
TWAP_price = 2.41 * 10 ** -6
p_token_in_pool = base_token_in_pool / TWAP_price
supply_invariant = base_token_in_pool * p_token_in_pool
q = 0
upper_delta = 1 * 0.01
G = 10 * 0.01

result = []
rolled_pnl = 0
rolled_buy = 0
rolled_sell = 0
for chunk in pd.read_csv(filename, chunksize=chunksize):
    df = pd.DataFrame(chunk, columns=['size', 'timestamp'])
    count = 0
    for delta in df.values:
        if count > 100: break
        p_token_to_buyer = delta[0]  # Negative if Buy
        timestamp = delta[1]

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
            rolled_sell
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
        'rolled_sell': data[:, 14]},
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
             'rolled_sell'])
init_base_token_in_pool = '{:.2e}'.format(init_base_token_in_pool)
TWAP = '{:.2e}'.format(TWAP_price)
df2.to_csv(f'results/TRXZ19-base_token_in_pool={init_base_token_in_pool}-TWAP={TWAP}-delta={upper_delta}-G={G}.csv', index=None, header=True)
