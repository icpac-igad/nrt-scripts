import codecs
import hashlib
import hmac
import logging
import os
import sys
import time
from datetime import datetime
from glob import glob

import numpy as np
import requests
import xarray as xr
import rioxarray as rxr

from .util_nc import clip_to_ea

DATA_FILES_CONFIG = {
    "daily_rainfall_forecast": {
        "file_match": "PrecDaily.nc",
        "interval": "daily",
        "variable": "dailyrain",
        "gsky_path": "gdata/RAINFALL/DAILY",
        "volume_path": "RAINFALL/DAILY",
        "prefix": "PrecDaily",
        "derived": {
            "name": "weekly_rainfall_forecast",
            "stats": "sum",
            "interval": "weekly",
            "gsky_path": "gdata/RAINFALL/WEEKLY",
            "volume_path": "RAINFALL/WEEKLY",
            "prefix": "PrecWeekly",
            "variable": "weeklytotalrain"
        }
    },
    "daily_temperature_forecast": {
        "file_match": "TavgDaily.nc",
        "variable": "dailyt2c",
        "gsky_path": "gdata/TEMPERATURE/DAILY",
        "volume_path": "TEMPERATURE/DAILY",
        "prefix": "TavgDaily",
        "interval": "daily",
        "derived": {
            "name": "weekly_temperature_forecast",
            "variable": "weeklyt2c",
            "stats": "mean",
            "gsky_path": "gdata/TEMPERATURE/WEEKLY",
            "volume_path": "TEMPERATURE/WEEKLY",
            "prefix": "TavgWeekly",
            "interval": "weekly",
        }
    },
    "weekly_exceptional_rainfall": {
        "file_match": "PrecExtreme.nc",
        "is_multivariable": True,
        "variables": ["f90", "f95", "f99"],
        "gsky_path": "gdata/RAINFALL/WEEKLY_EXCEPTIONAL",
        "volume_path": "RAINFALL/WEEKLY_EXCEPTIONAL",
        "prefix": "PrecExtreme",
        "interval": "weekly",
        "db_import": {
            "variable": "f90,f95,f99",
            "product": "weekly_extreme_rain",
            "host_base_dir": "/home/eahw/data/gskydata"
        }
    },
    "weekly_temp_anom": {
        "file_match": "TavgAnomaly.nc",
        "variables": ["temp_anom"],
        "gsky_path": "gdata/TEMPERATURE/WEEKLY_ANOMALY",
        "volume_path": "TEMPERATURE/WEEKLY_ANOMALY",
        "prefix": "TavgAnomaly",
        "interval": "weekly",
    }
}

# script root folder name
NAME = os.getenv("NAME")

# Data Directory
DATA_DIR = f"/opt/{NAME}/data"

LOCAL_WEEKLY_DATA_PATH = f"/opt/{NAME}/input"

GSKY_WEBHOOK_URL = os.getenv("GSKY_WEBHOOK_URL")
GSKY_WEBHOOK_SECRET = os.getenv("GSKY_WEBHOOK_SECRET")

EAHW_WEBHOOK_URL = os.getenv("EAHW_WEBHOOK_URL")
EAHW_WEBHOOK_SECRET = os.getenv("EAHW_WEBHOOK_SECRET")


def get_latest_date_for_dataset(gsky_path, namespace):
    res = requests.get(
        f"https://eahazardswatch.icpac.net/gsky/data_api/v1/gsky/latest_time?data_path={gsky_path}&namespace={namespace}")

    latest_time = res.json().get("latest_time")

    return latest_time


def get_weekly_date_from_path(path):
    date_str = path[-8:]
    date = datetime.strptime(date_str, '%Y%m%d')
    return date, date_str


def send_forecast_sync_command():
    if EAHW_WEBHOOK_URL and EAHW_WEBHOOK_SECRET:
        logging.info(f"[SYNC COMMAND]: Sending forecast sync command ")
        payload = {"now": time.time()}
        request = requests.Request(
            'POST', f"{EAHW_WEBHOOK_URL}/weekly-forecast-sync",
            data=payload, headers={})

        prepped = request.prepare()
        signature = hmac.new(codecs.encode(EAHW_WEBHOOK_SECRET), codecs.encode(prepped.body),
                             digestmod=hashlib.sha256)
        prepped.headers['X-Icpac-Signature'] = signature.hexdigest()

        with requests.Session() as session:
            response = session.send(prepped)
            logging.info(response.text)
        return response
    else:
        return None


def send_gsky_ingest_command():
    if GSKY_WEBHOOK_URL and GSKY_WEBHOOK_SECRET:
        logging.info(f"[INGEST COMMAND]: Sending gsky ingest command ")
        payload = {"now": time.time()}
        request = requests.Request(
            'POST', f"{GSKY_WEBHOOK_URL}/ingest-data",
            data=payload, headers={})

        prepped = request.prepare()
        signature = hmac.new(codecs.encode(GSKY_WEBHOOK_SECRET), codecs.encode(prepped.body), digestmod=hashlib.sha256)
        prepped.headers['X-Gsky-Signature'] = signature.hexdigest()

        with requests.Session() as session:
            response = session.send(prepped)
            logging.info(response.text)


def db_import(config):
    if EAHW_WEBHOOK_URL and EAHW_WEBHOOK_SECRET:
        request = requests.Request(
            'POST',
            f"{EAHW_WEBHOOK_URL}/import-weekly-exceptional-rain",
            data=config,
            headers={})

        prepped = request.prepare()
        signature = hmac.new(codecs.encode(EAHW_WEBHOOK_SECRET), codecs.encode(prepped.body), digestmod=hashlib.sha256)
        prepped.headers['X-Icpac-Signature'] = signature.hexdigest()

        logging.info(f'Sending Import to DB command')
        with requests.Session() as session:
            response = session.send(prepped)
            logging.info(response.text)


def main():
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    logging.info('STARTING')

    logging.info('SYNCING FORECAST DATA')
    send_forecast_sync_command()

    folders = sorted(glob(f"{LOCAL_WEEKLY_DATA_PATH}/202?????"))

    logging.info('Getting latest date from GSKY ...')
    latest_gsky_week = get_latest_date_for_dataset("gdata/RAINFALL/WEEKLY", "weeklytotalrain")

    logging.info(f'Latest ingested date from GSKY is: {latest_gsky_week}')

    if latest_gsky_week:
        latest_gsky_week = latest_gsky_week[:10]
        latest_gsky_week = datetime.strptime(latest_gsky_week, '%Y-%m-%d')

        new_folders = []

        for folder in folders:
            try:
                folder_date, date_str = get_weekly_date_from_path(folder)

                if folder_date > latest_gsky_week:
                    new_folders.append({"date": folder_date, "dir": folder, 'date_str': date_str})
            except Exception as e:
                logging.warning(f'Error getting date from file: {e}')

        logging.info(f'Total number of folders with new data: {len(new_folders)}')

        for folder in new_folders:
            data_date = folder.get("date")
            logging.info(f'Processing data for date {data_date}')

            for layer, config in DATA_FILES_CONFIG.items():
                file_path = f"{folder.get('dir')}/{config.get('file_match')}"
                date_str = folder.get('date_str')

                if os.path.exists(file_path):
                    ds = xr.open_dataset(file_path)

                    # rename lon and lat to x and y
                    if ds.get("lon", None) is not None and ds.get("lat", None) is not None:
                        ds = ds.rename({"lon": "x", "lat": "y"})

                    if config.get('interval') == 'weekly':
                        t = np.datetime64(folder.get('date'))
                        ds = ds.expand_dims(time=[t])

                    logging.info(f'clipping file: {file_path}')
                    ds = clip_to_ea(ds)

                    volume_dir = f"{DATA_DIR}/{config.get('volume_path')}"

                    # make dir if does not exist
                    if not os.path.exists(f"{volume_dir}"):
                        os.makedirs(volume_dir)

                    out = f"{volume_dir}/{config.get('prefix')}_{date_str}.nc"

                    # save to file
                    logging.info(f'saving file: {out}')
                    ds.to_netcdf(out)

                    ds.close()

                    logging.info(f'Finished processing {layer} for date {data_date}')

                    if config.get("db_import"):
                        logging.info(f'Importing to database: {layer}')

                        volume_path = config.get("volume_path")
                        d_config = config.get("db_import")

                        variable = d_config.get("variable")
                        product = d_config.get("product")
                        host_base_dir = d_config.get("host_base_dir")

                        if variable and product and host_base_dir:
                            file_name = f"{config.get('prefix')}_{date_str}.nc"

                            d_year = date_str[:4]
                            d_month = date_str[4:6]
                            d_day = date_str[6:]
                            full_date = f"{d_year}-{d_month}-{d_day}"

                            db_import_config = {
                                "volume": f"{host_base_dir}/{volume_path}/{file_name}",
                                "file": f"{file_name}",
                                "product": f"-p={product}",
                                "variable": f"-v={variable}",
                                "date": f"-d={full_date}"
                            }

                            logging.info(f"importing with config: {db_import_config}")

                            db_import(db_import_config)

                    if config.get('derived'):
                        logging.info(f'Processing derived data for date {data_date}')
                        derived_config = config.get('derived')

                        stats = derived_config.get('stats')

                        if stats and derived_config.get('prefix'):
                            ds = create_derived(out, stats, "time")

                        if derived_config.get('variable', None) is not None:
                            # convert to dataset if DataArray
                            if isinstance(ds, xr.DataArray):
                                ds = ds.to_dataset()

                            ds = ds.rename({config.get('variable'): derived_config.get('variable')})

                            if derived_config.get('interval') == 'weekly':
                                t = np.datetime64(folder.get('date'))
                                ds = ds.expand_dims(time=[t])

                            # clip again
                            ds = clip_to_ea(ds)

                            volume_dir = f"{DATA_DIR}/{derived_config.get('volume_path')}"

                            # make dir if does not exist
                            if not os.path.exists(f"{volume_dir}"):
                                os.makedirs(volume_dir)

                            ds.to_netcdf(f"{volume_dir}/{derived_config.get('prefix')}_{date_str}.nc",
                                         encoding={derived_config.get('variable'): {"_FillValue": -9999.0,
                                                                                    "grid_mapping": "spatial_ref"}})

                            logging.info(f'Finished processing derived data for date {data_date}')

                    ds.close()

                else:
                    logging.warn(f'File not found {file_path}. No clipping done')

        logging.info(f'Finished processing')

        if len(new_folders) > 0:
            logging.info(f'Sending Ingest command to GSKY')
            send_gsky_ingest_command()


def create_derived(data_path, method, dimension):
    with xr.open_dataset(data_path) as ds:
        try:
            if method == 'sum':
                ds = ds.sum(dim=dimension)
            elif method == 'mean':
                ds = ds.mean(dim=dimension)
            else:
                # TODO: implement other computations
                raise NotImplementedError()
        except Exception as e:
            raise e
        return ds
