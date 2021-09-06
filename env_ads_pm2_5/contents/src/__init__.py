import logging
import sys
import os
import tempfile

import cdsapi
import urllib3
import datetime
import xarray as xr
from .util_nc import clip_to_ea

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

EA_SHP_PATH = "shp/gha_admin0.shp"


def main():
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    logging.info('STARTING')

    client = cdsapi.Client(url=COPERNICUS_ADS_URL, key=COPERNICUS_ADS_KEY)

    date_today_str = datetime.date.today().strftime("%Y-%m-%d")

    temp_dir = tempfile.TemporaryDirectory()

    temp_file_path = f"{temp_dir.name}/{date_today_str}.nc"

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

    client.retrieve(request.get("dataset"), request.get("options"), temp_file_path)

    if os.path.exists(temp_file_path):
        ds = xr.open_dataset(temp_file_path, decode_times=False)
        # ads data comes with short data type. try to convert all types to float
        for var in ds.data_vars:
            if var != "spatia_ref":
                ds[var] = ds[var].astype(float)
                ds[var].attrs['_FillValue'] = -9999.0

        ds.to_netcdf(temp_file_path)
        ds.close()

        ds = clip_to_ea(temp_file_path, shp_path=EA_SHP_PATH, x_dim='longitude', y_dim='latitude')

        date_today_str = date_today_str.replace("-", '')

        file_path = f"{DATA_DIR}/PM25_{date_today_str}.nc"

        ds.to_netcdf(file_path)
