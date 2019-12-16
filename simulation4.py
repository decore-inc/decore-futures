import pandas as pd
import numpy as np

filename = 'sources/sim1.csv'
chunksize = 10 ** 8
ft_amount = 10 ** 8
init_price = 3812
spread = 10
size_max = 43861045
ft_dai_amount = ft_amount * init_price
result = []
rolled_pnl = 0
rolled_sell = 0
rolled_buy = 0
mm_rolled_pnl = 0
mm_rolled_sell = 0
mm_rolled_buy = 0
for chunk in pd.read_csv(filename, chunksize=chunksize):
    df = pd.DataFrame(chunk, columns=['size', 'ft_amount', 'price', 'pnl', 'buy', 'sell', 'timestamp', 'rolled_pnl', 'rolled_sell', 'rolled_buy'])
    for delta in df.values:
        size, target_price, timestamp = [delta[i] for i in (0, 2, 6)]
        # Market maker should buy or sell mm_size of ft to let market price near to the target_price
        # ft_dai_amount / (ft_amount + mm_size) = target_price
        mm_size = (ft_dai_amount / target_price) - ft_amount
        # See round numbers in Python: https://www.knowledgehut.com/blog/programming/python-rounding-numbers
        mm_size = round(mm_size)
        ft_amount += mm_size
        price = ft_dai_amount / ft_amount
        ft_dai_amount -= mm_size * price
        mm_pnl = mm_size * price
        mm_rolled_pnl += mm_pnl
        mm_buy = -mm_pnl if mm_size < 0 else 0
        mm_sell = mm_pnl if mm_size > 0 else 0
        mm_rolled_buy += mm_buy
        mm_rolled_sell += mm_sell

        if mm_size != 0:
            is_mm = True
            result.append([
                is_mm,
                timestamp,
                mm_size,
                ft_amount,
                price,
                target_price,
                mm_pnl,
                mm_buy,
                mm_sell,
                mm_rolled_pnl,
                mm_rolled_buy,
                mm_rolled_sell,
            ])

        is_mm = False
        ft_amount += size
        price = ft_dai_amount / ft_amount
        ft_dai_amount -= size * price
        pnl = size * price
        rolled_pnl += pnl
        buy = -pnl if size < 0 else 0
        sell = pnl if size > 0 else 0
        rolled_buy += buy
        rolled_sell += sell
        result.append([
            is_mm,
            timestamp,
            size,
            ft_amount,
            price,
            target_price,
            pnl,
            buy,
            sell,
            rolled_pnl,
            rolled_buy,
            rolled_sell,
        ])

total_buy = rolled_buy
total_sell = rolled_sell
total_pnl = rolled_buy - rolled_sell
total_pnl_rate = total_pnl / (total_buy + total_sell)
print(f'total_buy = {rolled_buy}')
print(f'total_sell = {total_sell}')
print(f'total_pnl = {total_pnl}')
print(f'total_pnl_rate = {total_pnl_rate}')

mm_total_buy = mm_rolled_buy
mm_total_sell = mm_rolled_sell
mm_total_pnl = mm_rolled_buy - mm_rolled_sell
mm_total_pnl_rate = mm_total_pnl / (mm_total_buy + mm_total_sell)
print(f'mm_total_buy = {mm_rolled_buy}')
print(f'mm_total_sell = {mm_total_sell}')
print(f'mm_total_pnl = {mm_total_pnl}')
print(f'mm_total_pnl_rate = {mm_total_pnl_rate}')
data = np.array(result)
df2 = pd.DataFrame(
    {
        'is_mm': data[:, 0],
        'timestamp': data[:, 1],
        'size': data[:, 2],
        'ft_amount': data[:, 3],
        'price': data[:, 4],
        'target_price': data[:, 5],
        'pnl': data[:, 6],
        'buy': data[:, 7],
        'sell': data[:, 8],
        'rolled_pnl': data[:, 9],
        'rolled_buy': data[:, 10],
        'rolled_sell': data[:, 11],
    },
    columns=['is_mm', 'timestamp', 'size', 'ft_amount', 'price', 'target_price', 'pnl', 'buy', 'sell', 'rolled_pnl',
             'rolled_buy', 'rolled_sell'])
df2.to_csv('results/sim4.csv', index=None, header=True)
