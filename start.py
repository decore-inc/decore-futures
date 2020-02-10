import os

import pandas as pd
from AMMFactory import AMMFactory


def run_simulations():
    for source_symbol in ['ETHM18']:
        run_simulation(source_symbol)


def run_simulation(source_symbol):
    twap_price = 0.04264
    fee_rate = 0  # 0.05 * 10 ** -2
    limit = None  # None if unlimited

    init_base_token_in_pool_list = [10 ** 7]
    delta_list = [0]
    g_list = [0]
    samples = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    amm_factory = AMMFactory()
    data = []
    for init_base_token_in_pool in init_base_token_in_pool_list:
        for delta in delta_list:
            for g in g_list:
                for sample in samples:
                    print(f'source_symbol: {source_symbol}')
                    print(f'init_base_token_in_pool: {init_base_token_in_pool}')
                    print(f'twap_price: {twap_price}')
                    print(f'delta: {delta}')
                    print(f'G: {g}')
                    print(f'fee_rate: {fee_rate}')
                    print(f'limit: {limit}')
                    amm = amm_factory.create_AMM(source_symbol, init_base_token_in_pool, twap_price, delta, g, fee_rate,
                                                 limit, sample)
                    amm.init_base_token_in_pool = init_base_token_in_pool
                    amm.calculate_max_rolled_pnl()
                    # noinspection PyTypeChecker
                    amm.trades = len(amm.trades)
                    data.append(amm.__dict__)
    df = pd.DataFrame(data)
    filename = f'{source_symbol}/delta={delta_list}-g={g_list}.csv'
    df.to_csv(f'results/{filename}', index=None, header=True)
    print(f'Output file: {filename}')


run_simulations()
