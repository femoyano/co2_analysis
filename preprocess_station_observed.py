# OUTPUTS: monthly means of co2
# NOTES:
# CREATION DATE: 2021-04-13
# AUTHOR: Fernando Moyano
# UPDATE: 
#--------------------------------------------------------------------------------

from pathlib import Path
from glob import glob
import os
import pandas as pd
import numpy as np

datain_dir = Path("../../../Data/CO2/data_raw")
dataout_dir = Path("../data/stations/monthly")
if not os.path.exists(dataout_dir):
    os.makedirs(dataout_dir)

# For now working with specific stations that have monthly values. May change in future (check Forkel code)
file_brw = datain_dir/"co2_brw_surface-insitu_1_ccgg_monthly.txt"
file_mlo = datain_dir/"co2_mlo_surface-insitu_1_ccgg_monthly.txt"

file_brw_out = dataout_dir/"BRW_station_co2_observed_insitu.csv"
file_mlo_out = dataout_dir/"MLO_station_co2_observed_insitu.csv"

def read_proc_write(file_in, file_out):
    # Read in the file
    data = pd.read_csv(file_in, delim_whitespace=True)

    # Might want this code if average 'event' based station data.
    # Calculate the total CO2 concentrations and aggregate to monthly means
    # mdata = data.groupby(['Year', 'Month']).agg(np.mean) 
    mdata = data

    # Crate and format dataframe
    co2_df = mdata[['time_decimal', 'value']]
    co2_df.columns = ["decimal_year", "co2_ppm"]
    # Round both variables to two digits
    co2_df = co2_df.round(2)
    # Rename columns
    co2_df.columns = ['decimal_year', 'co2_ppm']
    co2_df.loc[co2_df['co2_ppm'] < 200, 'co2_ppm'] = None
    co2_df.to_csv(file_out, index=False)
    return(co2_df)

df = read_proc_write(file_brw, file_brw_out)
df = read_proc_write(file_mlo, file_mlo_out)
