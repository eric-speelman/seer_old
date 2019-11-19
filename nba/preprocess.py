import pandas as pd
import numpy as np
from datetime import datetime

window_size = 10
df = pd.read_csv(f'../data/nba.csv', index_col=False)

data = []
start = datetime.now()
prior_stats = ['dkp']
for i, row in df.iterrows():
    if i % 1000 == 0:
        print(f'{i+1}/{df.shape[0]}')
    x = []
    data.append(x)
    x.append(row['dkp'])
    priors = df[(df['id'] == row['id']) & (df['game_id'] < row['game_id'])]
    for prior_index in range(10):
        has_value = priors.shape[0] > prior_index
        x.append(1 if has_value else 0)
        for prior_stat in prior_stats:
            if not has_value:
                x.append(0)
            else:
                x.append(priors.iloc[prior_index][prior_stat])
print('creating matrix')
matrix = np.matrix(data, dtype='f')
print(matrix.shape)
np.save('../data/matrix', matrix)
print('done')