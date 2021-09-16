# MLB Season Simulations

Quick and easy MLB team standings simulations. All you have to do is clone this repo, input a year you wish to simulate, and the results will be placed in a local directory.

## 2020 Results
![alt text](https://raw.githubusercontent.com/meirelon/baseball-season-simulation/master/imgs/results_2020.png)

## 2020 Predictions
![alt text](https://raw.githubusercontent.com/meirelon/baseball-season-simulation/master/imgs/predictions_2020.png)

## 2019 Results

![alt text](https://raw.githubusercontent.com/meirelon/baseball-season-simulation/master/imgs/results_2019.png)

![alt text](https://raw.githubusercontent.com/meirelon/baseball-season-simulation/master/imgs/results_2019_errors.png)

## Getting Started

Season data can be found [here](https://www.retrosheet.org/schedule/index.html)
```
git clone https://github.com/meirelon/baseball-season-simulation.git
cd baseball-season-simulation
pip install -r requirements.txt
python simulate_season.py --season=2019 --ntrials=100
```

Feel free to play with different seasons and/or number of trials.

## Contributing

Please reach out via email or send me a pull request.

## Authors

* **Michael Nestel**
