import logging
import sys
import os

import cdsapi
import urllib3
import datetime

urllib3.disable_warnings()

# Copernicus Atmospheric Data Store (ADS) API URL
COPERNICUS_ADS_URL = "https://ads.atmosphere.copernicus.eu/api/v2"

# Copernicus Atmospheric Data Store API KEY
COPERNICUS_ADS_KEY = os.getenv("COPERNICUS_ADS_KEY")

# script root folder name
NAME = os.getenv("NAME")

# Data Directory
DATA_DIR = f"/opt/{NAME}/data"

# Variable we are interested in from Copernicus ADS
VARIABLE = "particulate_matter_2.5um"

# are of Interest bbox
AOI_BBOX = [-12.5, 21, 24, 52]  # IGAD region


def main():
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    logging.info('STARTING')

    client = cdsapi.Client(url=COPERNICUS_ADS_URL, key=COPERNICUS_ADS_KEY)

    date_today_str = datetime.date.today().strftime("%Y-%m-%d")

    file_path = f"{DATA_DIR}/{date_today_str}.nc"

    request = {
        "dataset": "cams-global-atmospheric-composition-forecasts",
        "options": {
            'variable': f'{VARIABLE}',
            'date': f'{date_today_str}',
            'time': '00:00',
            'leadtime_hour': ['0', '24', '48', '72', '96', '120'],
            'type': 'forecast',
            'format': 'netcdf',
            'area': AOI_BBOX
        }
    }

    client.retrieve(request.get("dataset"), request.get("options"), file_path)
