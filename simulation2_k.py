import pandas as pd
import numpy as np

filename = 'sources/size_with_sign.csv'
chunksize = 10 ** 8
result = []
rolled_size = 0
for chunk in pd.read_csv(filename, chunksize=chunksize):
    df = pd.DataFrame(chunk, columns=['delta_size', 'timestamp'])
    for delta in df.values:
        size = delta[0]
        timestamp = delta[1]
        rolled_size += size
        result.append([
            rolled_size
        ])

data = np.array(result)
print(data)
print(data.max())