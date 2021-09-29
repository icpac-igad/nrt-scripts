## ICPAC Weekly Forecast Data Script

This file describes the near real-time script that retrieves and processes the ICPAC's Weekly Forecast Data for display
on the East Africa Hazards Watch.

The data is synced weekly from the ICPAC Computing Cluster to a local filesystem where processing is done.

After syncing, the following is a series of steps followed to process the data:

- Check for latest files that have been downloaded
- For each new file, the file is clipped to the East Africa region, generate any derived layers like total rainfall from
  daily data and saved to a specified data output directory
- Once all the files have been processed, a command is sent to GSKY Web server to ingest the
  layers.[GSKY](https://github.com/nci/gsky) is an Open Source WMS server for timeseries NetCDF datasets that is used at
  [ICPAC](https://www.icpac.net/).

Please see
the [Python script](https://github.com/icpac-igad/nrt-scripts/blob/main/clim_icpac_weekly_forecast/contents/src/__init__.py)
for more details on this processing.

You can view the processed weekly forecasts datasets [on Hazards Watch](https://eahazardswatch.icpac.net/).

**Schedule**

This script is run 3 times a day. This is to make sure that if data is not available at an expected time due to some
reason e.g power failure, the script can try again at sometime. The exact time that the script is run to update the
dataset can be found in the the `time.cron` file. This time is in Coordinated Universal Time (UTC), expressed in cron
format.

###### Note: This script was originally written by [Erick Otenyo](mailto:erick.otenyo@igad.int).
 