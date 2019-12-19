import pandas as pd
from AMMFactory import AMMFactory


def run_simulations():
    source_symbol = 'XBTH19'
    twap_price = 6850
    fee_rate = 0 # 0.05 * 10 ** -2
    limit = None # None if unlimited

    init_base_token_in_pool_list = [10 ** 10, 10 ** 8, 10 ** 6]
    delta_list = [0]
    g_list = [0]

    amm_factory = AMMFactory()
    data = []
    for init_base_token_in_pool in init_base_token_in_pool_list:
        for delta in delta_list:
            for g in g_list:
                print(f'source_symbol: {source_symbol}')
                print(f'init_base_token_in_pool: {init_base_token_in_pool}')
                print(f'twap_price: {twap_price}')
                print(f'delta: {delta}')
                print(f'G: {g}')
                print(f'fee_rate: {fee_rate}')
                print(f'limit: {limit}')
                amm = amm_factory.create_AMM(source_symbol, init_base_token_in_pool, twap_price, delta, g, fee_rate, limit)
                amm.init_base_token_in_pool = init_base_token_in_pool
                amm.trades = len(amm.trades)
                data.append(amm.__dict__)
    df = pd.DataFrame(data)
    filename = f'{source_symbol}/base_token_in_pool={init_base_token_in_pool_list}-delta={delta_list}-g={g_list}.json'
    df.to_json(f'results/{filename}', orient='records')
    print(f'Output file: {filename}')

run_simulations()
