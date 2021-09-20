## ICPAC Weekly Forecast Data Script

This file describes the near real-time script that retrieves and processes the ICPAC's Weekly Forecast Data for display
on the East Africa Hazards Watch.

The data is synced weekly from the ICPAC Computing Cluster to a local filesystem where processing is done

{Describe the steps used to process the data, e.g., "convert variable X from the original netcdf file for ingestion in
GSKY."}

Please see the [Python script]({link to Python script on Github}) for more details on this processing.

You can view the processed {EA Hazards Watch public title}
dataset [on Hazards Watch]({link to dataset's metadata page on Hazards Watch}).

**Schedule**

This script is run {frequency of execution}. The exact time that the script is run to update the dataset can be found in
the the `time.cron` file. This time is in Coordinated Universal Time (UTC), expressed in cron format.

###### Note: This script was originally written by [Erick Otenyo](mailto:erick.otenyo@igad.int).
 