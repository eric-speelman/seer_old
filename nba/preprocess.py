import pandas as pd
import numpy as np
from datetime import datetime
import math
import os.path
from os import path

window_size = 10
child_sets = [
    {
        'name': 'points',
        'offset': True,
        'cols': []
    },
    {
        'name': 'home',
        'offset': False,
        'cols': ['team_is_home']
    }
]
data = []
start = datetime.now()
stats = ['dkp']
avgs = []
for child_set in child_sets:
    stats.extend(child_set['cols'])
stats = set(stats)
print(stats)

def scale(X, x_min, x_max):
    nom = (X-X.min(axis=0))*(x_max-x_min)
    denom = X.max(axis=0) - X.min(axis=0)
    denom[denom==0] = 1
    return x_min + nom/denom 

if not path.exists(f'../data/nba_win_{window_size}.csv'):
    print('Window data not found. Generating...')
    df = pd.read_csv(f'../data/nba.csv', index_col=['id', 'game_id'])
    cols = []
    for prior_index in range(window_size):
        cols.append(f'has_value_p{prior_index}')
        for stat in stats:
            cols.append(f'{stat}_p{prior_index}')
    prior_df = pd.DataFrame(columns=cols)
    cnt = 0
    for i, df_row in df.iterrows():
        id = i[0]
        game_id = i[1]
        cnt += 1
        if cnt % 1000 == 1:
            print(f'Window {cnt}/{df.shape[0]}')
        priors = df.loc[[id, 'game_id' <= game_id], :].sort_values('game_id', ascending=False)
        row = {}
        row['id'] = id
        for prior_index in range(window_size):
            has_value = priors.shape[0] > prior_index
            row[f'has_value_p{prior_index}'] = has_value
            for prior_stat in stats:
                stat_val = 0
                if has_value:
                    stat_val = priors.iloc[prior_index][prior_stat]
                row[f'{prior_stat}_p{prior_index}'] = stat_val
        prior_df = prior_df.append(row, ignore_index=True)
    prior_df.to_csv(f'../data/nba_win_{window_size}.csv', index=False)
else:
    prior_df = pd.read_csv(f'../data/nba_win_{window_size}.csv', index_col=False)
print(prior_df['team_is_home_p0'].shape)
players = list(set(list(prior_df['id'])))
for child_set in child_sets:
    matrix = []
    is_offset = child_set['offset']
    for i, row in prior_df.iterrows():
        matrix_row = []
        player_index = players.index(row['id'])
        player_binary = [int(x) for x in list('{0:0b}'.format(player_index))]
        while len(player_binary) < 10:
            player_binary.append(0)
        matrix_row.extend(player_binary)
        matrix.append(matrix_row)
        for prior_index in range(window_size - 1):
            i = prior_index
            if is_offset:
                i += 1
            matrix_row.append(row[f'dkp_p{prior_index+1}'])
            matrix_row.append(row[f'has_value_p{prior_index+1}'])
            for col in child_set['cols']:
                matrix_row.append(row[f'{col}_p{i}'])
    np_matrix = np.matrix(matrix)
    np_matrix = scale(np_matrix, -1, 1)
    np.save('../data/'+ child_set['name'], np_matrix)
    print(np_matrix.shape)
    print(np_matrix)
np.save('../data/y', np.array(prior_df['dkp_p0']))
