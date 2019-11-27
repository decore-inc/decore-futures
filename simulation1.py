import pandas as pd
import numpy as np

filename = 'sources/size_with_sign.csv'
chunksize = 10 ** 8
ft_amount = 10 ** 8
init_price = 3812
ft_dai_amount = ft_amount * init_price
price = init_price
result = []
buy = 0
sell = 0
rolled_pnl = 0
total_sell = 0
total_buy = 0
rolled_pnl = 0
for chunk in pd.read_csv(filename, chunksize=chunksize):
    df = pd.DataFrame(chunk, columns=['delta_size', 'timestamp'])
    for delta in df.values:
        size = delta[0]
        timestamp = delta[1]
        ft_amount += size
        ft_dai_amount -= size * price
        price = ft_dai_amount / ft_amount
        pnl = size * price
        rolled_pnl += pnl
        sell = pnl if size > 0 else 0
        buy = -pnl if size < 0 else 0
        total_sell += sell * price
        total_buy += buy * price
        result.append([
            size,
            ft_amount,
            price,
            pnl,
            buy,
            sell,
            timestamp,
            rolled_pnl
        ])
print(total_sell)
print(total_buy)
print(total_buy - total_sell)
print(total_buy + total_sell)
print((total_buy - total_sell)/(total_sell + total_buy))
data = np.array(result)
df2 = pd.DataFrame(
    {'size': data[:, 0], 'ft_amount': data[:, 1], 'price': data[:, 2], 'pnl': data[:, 3], 'buy': data[:, 4], 'sell': data[:, 5], 'timestamp': data[:, 6], 'rolled_pnl': data[:, 7]},
    columns=['size', 'ft_amount', 'price', 'pnl', 'buy', 'sell', 'timestamp', 'rolled_pnl'])
df2.to_csv('results/prices-10**8-pnl.csv', index=None, header=True)