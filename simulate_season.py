import os
import argparse
import random
from datetime import datetime

import pandas as pd
import numpy as np

from pybaseball import batting_stats
from pybaseball import season_game_logs

from simulation_utils import SCHEDULE_COLUMNS, DISTRIBUTIONS

class simulateSeason:
    def __init__(self, season):
        self.season = int(season)-1

    def runs_per_game(self):
        season_string = str(self.season)
        gamelogs = season_game_logs(self.season)
        home_rg = gamelogs[gamelogs["date"] > int(season_string + '0717')].groupby("home_team")["home_score"].agg(['mean', 'std']).reset_index()
        home_rg.columns = ["home_team", "home_mean", "home_std"]
        away_rg = gamelogs[gamelogs["date"] > int(season_string + '0717')].groupby("visiting_team")["visiting_score"].agg(['mean', 'std']).reset_index()
        away_rg.columns = ["visiting_team", "visiting_mean", "visiting_std"]
        return [home_rg, away_rg]

    def get_season_schedule(self):
        season_to_simulate = str(self.season + 1)
        schedule = pd.read_csv("data/schedule/{}SKED.txt".format(season_to_simulate), header=None).iloc[:,0:10]
        schedule.columns = SCHEDULE_COLUMNS
        return schedule

    def sim_season(self, schedule_rg, distribution='beta'):
        if distribution.lower() == 'beta':
            schedule_rg['outcome'] = schedule_rg.apply(lambda row: random.betavariate(row['home_mean'],row['home_std']) - random.betavariate(row['visiting_mean'],row['visiting_std']), axis=1)
            schedule_rg['win'] = schedule_rg.apply(lambda row: str(np.where(row['outcome']>0, row['home_team'], row['visiting_team'])), axis=1)
            return schedule_rg.groupby("win")["outcome"].count().reset_index().set_index("win").transpose()
        elif distribution.lower() == 'normal':
            schedule_rg['outcome'] = schedule_rg.apply(lambda row: random.gauss(row['home_mean'],row['home_std']) - random.gauss(row['visiting_mean'],row['visiting_std']), axis=1)
            schedule_rg['win'] = schedule_rg.apply(lambda row: str(np.where(row['outcome']>0, row['home_team'], row['visiting_team'])), axis=1)
            return schedule_rg.groupby("win")["outcome"].count().reset_index().set_index("win").transpose()
        elif distribution.lower() == 'lognormal':
            schedule_rg['outcome'] = schedule_rg.apply(lambda row: random.lognormvariate(row['home_mean'],row['home_std']) - random.lognormvariate(row['visiting_mean'],row['visiting_std']), axis=1)
            schedule_rg['win'] = schedule_rg.apply(lambda row: str(np.where(row['outcome']>0, row['home_team'], row['visiting_team'])), axis=1)
            return schedule_rg.groupby("win")["outcome"].count().reset_index().set_index("win").transpose()
        elif distribution.lower() == 'gamma':
            schedule_rg['outcome'] = schedule_rg.apply(lambda row: random.gammavariate(row['home_mean'],row['home_std']) - random.gammavariate(row['visiting_mean'],row['visiting_std']), axis=1)
            schedule_rg['win'] = schedule_rg.apply(lambda row: str(np.where(row['outcome']>0, row['home_team'], row['visiting_team'])), axis=1)
            return schedule_rg.groupby("win")["outcome"].count().reset_index().set_index("win").transpose()
        elif distribution.lower() == 'weibull':
            schedule_rg['outcome'] = schedule_rg.apply(lambda row: random.weibullvariate(row['home_mean'],row['home_std']) - random.weibullvariate(row['visiting_mean'],row['visiting_std']), axis=1)
            schedule_rg['win'] = schedule_rg.apply(lambda row: str(np.where(row['outcome']>0, row['home_team'], row['visiting_team'])), axis=1)
            return schedule_rg.groupby("win")["outcome"].count().reset_index().set_index("win").transpose()
        else:
            print("Pick one of the following distributions {}".format(" | ".join(sorted(["beta", "normal", "gamma", "weibull"]))))

    def simulate(self, ntrials=100):
        sim_time = datetime.now().strftime("%Y%m%d%H%M%S")
        os.mkdir("data/simulations/{}".format(sim_time))
        home_rg, away_rg = self.runs_per_game()
        schedule = self.get_season_schedule()
        schedule_rg = schedule.set_index("visiting_team").join(away_rg.set_index("visiting_team")).reset_index().set_index("home_team").join(home_rg.set_index("home_team")).reset_index().sort_values(by="date")

        season_simulation = {}
        for dist in DISTRIBUTIONS:
            print(dist)
            sim_season_df = pd.concat([self.sim_season(schedule_rg = schedule_rg, distribution=dist)
                                       for x in range(0,ntrials)], axis=0).mean(axis=0).round().astype(int).reset_index()
            sim_season_df.columns = ["team", "wins"]
            season_simulation[dist] = sim_season_df
            sim_season_df.to_csv("data/simulations/{time}/sim_{season}_{dist}.csv".format(season=self.season+1,
                                                                                           time=sim_time,
                                                                                           dist=dist),
                                                                                           index=False)
        return season_simulation


def main(argv=None):
    parser = argparse.ArgumentParser()

    parser.add_argument('--season',
                        dest='season',
                        default = int(2019),
                        help='Season you wish to simulate')
    parser.add_argument('--ntrials',
                        dest='ntrials',
                        default=int(100),
                        help='Total trials per simulation')

    args, _ = parser.parse_known_args(argv)

    simulation = simulateSeason(args.season)
    simulation.simulate(ntrials=args.ntrials)


if __name__ == '__main__':
    main()
