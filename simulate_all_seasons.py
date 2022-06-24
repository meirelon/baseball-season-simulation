import pandas as pd

from simulate_season import simulateSeason


def main():
    season_list = [x for x in range(1970, 2020)]

    all_seasons_sim = pd.DataFrame()

    for season in season_list:
        print(season)
        simulation = simulateSeason(season)
        sim_tmp = simulation.simulate(ntrials=100)
        all_seasons_sim = pd.concat([all_seasons_sim, sim_tmp], axis=0)

    all_seasons_sim.to_csv("data/simulations/all/all_simulations.csv", index=False)


if __name__ == "__main__":
    main()
