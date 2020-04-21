import os
import argparse
import random
from datetime import datetime
from functools import reduce

import pandas as pd
import numpy as np

from pybaseball import batting_stats
from pybaseball import season_game_logs

from simulation_utils import SCHEDULE_COLUMNS, DISTRIBUTIONS

from simulate_season import simulateSeason

def main():
    season_list = [x for x in range(1970,2020)]

    all_seasons_sim = pd.DataFrame()

    for season in season_list:
        print(season)
        simulation = simulateSeason(season)
        sim_tmp = simulation.simulate(ntrials=100)
        all_seasons_sim = pd.concat([all_seasons_sim,sim_tmp], axis=0)

    all_seasons_sim.to_csv("data/simulations/all/all_simulations.csv", index=False)


if __name__ == '__main__':
    main()
