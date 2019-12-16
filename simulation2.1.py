import pandas as pd
import numpy as np

filename = 'sources/size_with_sign.csv'
chunksize = 10 ** 8
ft_amount = 10 ** 8
init_price = 3812
size_max = 43861045
ft_dai_amount = ft_amount * init_price
price = init_price
result = []
buy = 0
sell = 0
rolled_size = 0
rolled_pnl = 0
rolled_sell = 0
rolled_buy = 0
for chunk in pd.read_csv(filename, chunksize=chunksize):
    df = pd.DataFrame(chunk, columns=['delta_size', 'timestamp'])
    for delta in df.values:
        size = delta[0]
        timestamp = delta[1]
        ft_amount += size
        rolled_size += size
        k = -1 * rolled_size / size_max
        rate = (1 / 4 * k * k) + (3 / 4 * k) + 1
        price = rate * ft_dai_amount / ft_amount
        ft_dai_amount -= size * price
        pnl = size * price
        rolled_pnl += pnl
        sell = pnl if size > 0 else 0
        buy = -pnl if size < 0 else 0
        rolled_sell += sell
        rolled_buy += buy
        result.append([
            size,
            ft_amount,
            price,
            pnl,
            buy,
            sell,
            timestamp,
            k,
            rate,
            rolled_pnl,
            rolled_sell,
            rolled_buy
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
    {'size': data[:, 0], 'ft_amount': data[:, 1], 'price': data[:, 2], 'pnl': data[:, 3], 'buy': data[:, 4], 'sell': data[:, 5], 'timestamp': data[:, 6], 'k': data[:, 7], 'rate': data[:, 8], 'rolled_pnl': data[:, 9], 'rolled_sell': data[:, 10], 'rolled_buy': data[:, 11]},
    columns=['size', 'ft_amount', 'price', 'pnl', 'buy', 'sell', 'timestamp', 'k', 'rate', 'rolled_pnl', 'rolled_sell', 'rolled_buy'])
df2.to_csv('results/sim2.1.csv', index=None, header=True)