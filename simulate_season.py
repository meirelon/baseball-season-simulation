import os
import argparse
import random
from datetime import datetime
from functools import reduce

import pandas as pd
import numpy as np

from pybaseball import batting_stats
from pybaseball import season_game_logs

from simulation_utils import SCHEDULE_COLUMNS, DISTRIBUTIONS, MLB_DIVISONS

class simulateSeason:
    def __init__(self, season, date_filter=None, gcp=False, pybaseball_schedule=False):
        self.season = int(season)-1
        self.date_filter = date_filter
        self.gcp = gcp
        self.pybaseball_schedule = pybaseball_schedule

    def runs_per_game(self):
        season_string = str(self.season)
        gamelogs = season_game_logs(self.season)

        home_rg = gamelogs[gamelogs["date"] > int(season_string + '0717')]\
        .groupby("home_team")["home_score"]\
        .agg(['mean', 'std'])\
        .reset_index()
        home_rg.columns = ["home_team", "home_mean", "home_std"]

        away_rg = gamelogs[gamelogs["date"] > int(season_string + '0717')]\
        .groupby("visiting_team")["visiting_score"]\
        .agg(['mean', 'std'])\
        .reset_index()
        away_rg.columns = ["visiting_team", "visiting_mean", "visiting_std"]
        return [home_rg, away_rg]

    def get_season_schedule(self, date_filter=None):
        season_to_simulate = str(self.season + 1)
        if self.gcp:
            from gcp_utils import load_gcs_schedule
            schedule = load_gcs_schedule(season=season_to_simulate)
        if self.pybaseball_schedule:
            #NOTE: requires you to setup GH_TOKEN in env: https://github.com/jldbc/pybaseball/commit/1d643649b1310bdb1664fe47863cb90c6b1ad4a7#diff-0afa2103d97955913e8bd0001b682b37bc80d6fa8230b12ed827644eb8261858R28
            from pybaseball import schedules
            schedule = schedules(season_to_simulate).iloc[:,0:10]
        else:
            schedule = pd.read_csv("data/schedule/{}SKED.txt".format(season_to_simulate), header=None).iloc[:,0:10]

        schedule.columns = SCHEDULE_COLUMNS
        if self.date_filter is not None:
            schedule = schedule[schedule["date"] <= int(self.date_filter)]


        visiting_games = schedule.groupby("visiting_team")["number_of_games"].count().reset_index()
        visiting_games.columns = ["team", "visiting_number_of_games"]
        home_games = schedule.groupby("home_team")["number_of_games"].count().reset_index()
        home_games.columns = ["team", "home_number_of_games"]
        total_games_by_team = visiting_games.set_index('team').join(home_games.set_index('team')).reset_index()
        total_games_by_team["total_games_played"] = total_games_by_team["home_number_of_games"] + total_games_by_team["visiting_number_of_games"]

        divisions_list = [total_games_by_team.query(f"team in {MLB_DIVISONS[k]}") for k in MLB_DIVISONS.keys()]

        return schedule, total_games_by_team

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
        # os.mkdir("data/simulations/{}".format(sim_time))
        schedule, total_games_by_team = self.get_season_schedule()
        home_rg, away_rg = self.runs_per_game()

        schedule_rg = schedule\
        .set_index("visiting_team")\
        .join(away_rg.set_index("visiting_team"))\
        .reset_index()\
        .set_index("home_team")\
        .join(home_rg.set_index("home_team"))\
        .reset_index()\
        .sort_values(by="date")

        simulation_list = []
        for dist in DISTRIBUTIONS:
            # print(dist)
            sim_season_df = pd.concat([self.sim_season(schedule_rg = schedule_rg, distribution=dist)
                                       for x in range(0,ntrials)], axis=0).mean(axis=0).round().astype(int).reset_index()
            sim_season_df.columns = ["team", f"{dist}_wins"]
            simulation_list.append(sim_season_df)

        merged = reduce(lambda x, y: pd.merge(x, y, on = 'team'), simulation_list)
        merged["year"] = str(self.season+1)

        summary_df = merged.set_index("team").join(total_games_by_team.set_index("team")).reset_index()

        # merged.to_csv("data/simulations/{time}/sim_{season}.csv".format(season=self.season+1,
        #                                                                                time=sim_time),
        #

        if self.gcp:
            from gcp_utils import export_to_gcs
            export_to_gcs(summary_df, self.date_filter)
        else:
            summary_df.to_html("data/simulations/dev/sim_{season}.html".format(season=self.season+1), index=False)
            summary_df.to_csv("data/simulations/dev/sim_{season}.csv".format(season=self.season+1), index=False)

        return "True"


def main(argv=None):
    parser = argparse.ArgumentParser()

    parser.add_argument('--season',
                        dest='season',
                        default = int(2020),
                        help='Season you wish to simulate')
    parser.add_argument('--ntrials',
                        dest='ntrials',
                        default=int(100),
                        help='Total trials per simulation')
    parser.add_argument('--date_filter',
                        dest='date_filter',
                        default=None,
                        help='Simulate till this date')
    parser.add_argument('--gcp',
                        dest='gcp',
                        default=False,
                        help='Read and Write Data with Google Cloud Platform')
    parser.add_argument('--pybaseball_schedule',
                        dest='pybaseball_schedule',
                        default=True,
                        help='Read Schedule Data from Pybaseball (retrosheet)')

    args, _ = parser.parse_known_args(argv)

    simulation = simulateSeason(season=int(args.season),
                                date_filter=args.date_filter,
                                gcp=bool(args.gcp),
                                pybaseball_schedule=bool(args.pybaseball_schedule))

    simulation.simulate(ntrials=int(args.ntrials))


if __name__ == '__main__':
    main()
