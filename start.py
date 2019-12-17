from AMMFactory import AMMFactory

source_symbol = 'XBTU19'
init_base_token_in_pool = 10 ** 8
twap_price = 3812
delta = 0.01
g = 0.1
limit = 100

# source_symbol = input(f'source_symbol({source_symbol}): ')
# init_base_token_in_pool = float(input(f'init_base_token_in_pool({init_base_token_in_pool}): '))
# twap_price = float(input(f'twap_price({twap_price}): '))
# delta = float(input(f'delta({delta}): '))
# g = float(input(f'G({g}): '))
# limit = int(input(f'limit({limit}):'))

print(f'source_symbol: {source_symbol}')
print(f'init_base_token_in_pool: {init_base_token_in_pool}')
print(f'twap_price: {twap_price}')
print(f'delta: {delta}')
print(f'G: {g}')
print(f'limit: {limit}')

AMMFactory.create_AMM(source_symbol, init_base_token_in_pool, twap_price, delta, g, limit)
