import gcsfs
import pandas as pd
from google.cloud import storage

def load_gcs_schedule(season):
    schedule = pd.read_csv(f"gs://draftkings/data/mlb_schedules/{season}SKED.TXT",
                                        header=None).iloc[:,0:10]
    return schedule

def export_to_gcs(results, dt):
    client = storage.Client()
    bucket = client.get_bucket('draftkings')
    bucket.blob(f"data/mlb_simulations_html/mlb_simulations_{dt}.html").upload_from_string(results.to_html(), 'text/html')
    bucket.blob(f"data/mlb_simulations_csv/mlb_simulations_{dt}.csv").upload_from_string(results.to_html(), 'text/csv')
