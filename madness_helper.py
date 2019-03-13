import pandas as pd
from nba_utilities.db_connection_manager import establish_db_connection

def get_teams():
    teams = pd.read_sql('SELECT team FROM kenpom_four_factors_data', con=conn)
    teams = [ row['team'] for index, row in teams.iterrows() ]
    teams = list(set(teams))
    teams = [ {'label': team, 'value': team} for team in sorted(teams) ]
    return teams

def four_factors_algo(team_a, team_b):
    conn = establish_db_connection('sqlalchemy').connect()

    ## fetch data
    cols = {'Team':'team', 'eFG Perc':'efg_perc', 'Turnover Perc':'tov_perc',
            'Off Rebound Perc':'orb_perc', 'FTRate':'ft_rate',
            'Opp eFG Perc':'opp_efg_perc', 'Opp Turnover Perc':'opp_tov_perc',
            'Opp Off Rebound Perc':'opp_orb_perc', 'Opp FTRate': 'opp_ft_rate'
            }
    sql_str = 'SELECT `{}` FROM kenpom_four_factors_data WHERE Year = 2019'.format('`, `'.join(cols.keys()))
    df = pd.read_sql(sql_str, con=conn)
    df.rename(index=str, columns=cols, inplace=True)

    ## clean data
    for col in [ col for col in df.columns if col != 'team' ]:
        df[col] = df[col] / 100

    df = df[df['team'].isin([team_a, team_b])].copy()

    ## run algo
    weights_dict = {'efg':0.40, 'tov':0.25, 'orb':0.20, 'ft_rate':0.15}

    temp = {}
    for index, row in df.iterrows():
        efg = (row['efg_perc'] - row['opp_efg_perc']) * 100
        tov = (row['tov_perc'] - row['opp_tov_perc']) * 100
        orb = (row['tov_perc'] - row['opp_tov_perc']) * 100
        ft_rate = (row['ft_rate'] - row['opp_ft_rate']) * 100
        temp[row['team']] = {'efg':efg, 'tov':tov, 'orb':orb,'ft_rate':ft_rate}

    algo_dict = {}
    for s, w in weights_dict.iteritems():
        algo_dict[s] = (temp[team_a].get(s) - temp[team_b].get(s)) * w

    spread = round((sum(algo_dict.values()) * 2), 3)

    return spread


if __name__ == "__main__":
    four_factors_algo('Duke', 'Gonzaga')
