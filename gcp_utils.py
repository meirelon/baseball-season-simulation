import gcsfs
import pandas as pd

def load_gcs_schedule(season):
    schedule = pd.read_csv(f"gs://draftkings/data/mlb_schedules/{season}SKED.TXT", header=None).iloc[:,0:10]

def export_to_gcs(f, dt):
    f.to_html(f"gs://draftkings/data/mlb_simulations_html/mlb_simulations_{dt}.html")
    f.to_csv(f"gs://draftkings/data/mlb_simulations_csv/mlb_simulations_{dt}.csv")
