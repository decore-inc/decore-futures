from AMM import AMM
import pandas as pd
import numpy as np

class AMMFactory:

    @classmethod
    def create_AMM(cls, source_symbol, init_base_token_in_pool, twap_price, delta, g, limit=None):
        amm = AMM(init_base_token_in_pool, twap_price, delta, g)
        chunksize = 10 ** 8  # processing 10 ** 8 rows at a time
        count = 0
        for chunk in pd.read_csv(f'sources/{source_symbol}.csv', chunksize=chunksize):
            df = pd.DataFrame(chunk, columns=['size', 'side', 'price', 'timestamp'])
            if len(df.values) == 0: raise ValueError("Trade length is Zero, there is no output csv.")
            for value in df.values:
                if (limit > 0) and (count > limit):
                    break
                side = value[1]
                p_token_to_buyer = -value[0] if side == 'Buy' else value[0]  # Negative if Buy
                target_price = value[2]
                timestamp = value[3]

                amm.make_trade(p_token_to_buyer, target_price, timestamp)
                amm.market_maker(target_price, timestamp)
                count += 1

        data = np.array(amm.trades)
        data_frame = {}
        keys = data[0].__dict__.keys()
        for key in keys:
            data_frame[key] = [trade.__dict__[key] for trade in data]

        df2 = pd.DataFrame(
            data_frame,
            columns=keys)
        init_base_token_in_pool = '{:.2e}'.format(init_base_token_in_pool)
        twap_price = '{:.2e}'.format(twap_price)
        output_filename = f'{source_symbol}-base_token_in_pool={init_base_token_in_pool}-TWAP={twap_price}-delta={delta}-G={g}'
        df2.to_csv(f'results/{output_filename}.csv',index=None, header=True)
        print(f'Output file: {output_filename}.csv')
