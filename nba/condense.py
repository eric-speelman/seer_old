import pandas as pd
from datetime import datetime

start_year = 2001
end_year = 2020


def mp_map(mp):
    mp_parts = mp.split(':')
    return int(mp_parts[0]) * 60 + int(mp_parts[1])
def game_day_map(day_str, season):
    dt = datetime.strptime(day_str, '%I:%M %p, %B %d, %Y')
    start = datetime(season - 1, 1, 1)
    return (dt - start).days
year = start_year
frames = []
while year <= end_year:
    print(f'Loading {year}...')
    df = pd.read_csv(f'../data/nba_{year}.csv', index_col=False)
    df['game_season'] = year
    df['game_day'] = df['game_date'].map(lambda x: game_day_map(x, year))
    frames.append(df)
    pd.read_csv(f'../data/nba_{year}.csv')
    year += 1
df = pd.concat(frames, ignore_index=True)
df.reindex()
df['mp'] = df['mp'].map(lambda mp: mp_map(mp))
df['dkp'] = 0.0
double_cols = ['pts', 'trb', 'ast', 'stl', 'blk']
for i, row in df.iterrows():
    dkp = row['pts'] + row['fg3'] * 0.5 + row['trb'] * 1.25 + row['ast'] * 1.5 + row['stl'] * 2 + row['blk'] * 2 + row['tov'] * -0.5
    double_cnt = 0
    for stat in double_cols:
        if row[stat] >= 10:
            double_cnt += 1
    if double_cnt >= 3:
        dkp += 3
    if double_cnt >= 2:
        dkp += 1.5
    df.at[i, 'dkp'] = dkp
df.to_csv('../data/nba.csv', index=False)