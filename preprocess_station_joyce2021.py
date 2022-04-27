#--------------------------------------------------------------------------------
# NAME: "preprocess_station_joyce2021.py"
# PROJECT: Analyze CO2 data
# PURPOSE: Preprocess station data from Joyce et al. 2021 
# CATEGORY: 
# CALLING SEQUENCE:
# INPUTS: 
# PARAMETERS: 
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

datain_dir = Path("../../../Data/Joyce_et_al_2021_GRL")
dataout_dir = Path("../data/stations")
if not os.path.exists(dataout_dir):
    os.makedirs(dataout_dir)

files_const = sorted(glob(os.path.realpath(datain_dir/"BRW_station_co2_atmos_const*")))
files_vary = sorted(glob(os.path.realpath(datain_dir/"BRW_station_co2_atmos_vary*")))

fileout_vary_monthly = dataout_dir / "BRW_CO2_monthly_joyce_varyall.csv"
fileout_const_monthly = dataout_dir / "BRW_CO2_monthly_joyce_constmet.csv"

fileout_vary_daily = dataout_dir / "BRW_CO2_daily_joyce_varyall.csv"
fileout_const_daily = dataout_dir / "BRW_CO2_daily_joyce_constmet.csv"
fileout_vary_hourly = dataout_dir / "BRW_CO2_3hourly_joyce_constmet.csv"
fileout_const_hourly = dataout_dir / "BRW_CO2_3hourly_joyce_constmet.csv"

def read_proc_write(files, file_out_monthly, file_out_daily, file_out_hourly):
    # First read in the files
    for i in range(0, len(files)):
        f = files[i]
        # print(f)
        data_in = pd.read_csv(f, delim_whitespace=True, header=None, skiprows=3)
        if i == 0:
            colnames = pd.read_csv(f, sep=',', skiprows=2, nrows=0, skipinitialspace=True).columns.tolist()
            data_in.columns = colnames
            data = data_in  
        else:
            data_in.columns = colnames
            data = pd.concat([data, data_in])

    # Then calculate the total CO2 concentrations
    data['co2'] = data["Background"] + data["FF"] + data["Ocean"] + data["NEE_ctrl"] + data["FIRE_ctrl"]

    # Aggregate to monthly and daily means
    mdata = data.groupby(['Year', 'Month'], as_index=False).agg(np.mean)
    ddata = data.groupby(['Year', 'Month', 'Day'], as_index=False).agg(np.mean)

    # Crate and format dataframe
    mdata = mdata[['Year', 'Month', 'co2']]
    mdata.columns = ['year', 'month', 'co2_ppm']
    ddata = ddata[['Year', 'Month', 'Day', 'co2']]
    ddata.columns = ['year', 'month', 'day', 'co2_ppm']
    data = data[['Year', 'Month', 'Day', 'Hour', 'co2']]
    data.columns = ['year', 'month', 'day', 'hour', 'co2_ppm']

    # Adjust time of month to match observation file
    mdata.loc[:, 'year'] = mdata['year'].astype(int)
    mdata.loc[:, 'month'] = mdata['month'].astype(int)
    ddata.loc[:, 'year'] = ddata['year'].astype(int)
    ddata.loc[:, 'month'] = ddata['month'].astype(int)
    ddata.loc[:, 'day'] = ddata['day'].astype(int)
    data.loc[:, 'year'] = data['year'].astype(int)
    data.loc[:, 'month'] = data['month'].astype(int)
    data.loc[:, 'day'] = data['day'].astype(int)
    data.loc[:, 'hour'] = data['hour'].astype(int)

    # Round co2 and dec year to two digits
    mdata.loc[:,'co2_ppm'] = mdata['co2_ppm'].round(2)
    ddata.loc[:,'co2_ppm'] = ddata['co2_ppm'].round(2)
    data.loc[:,'co2_ppm'] = data['co2_ppm'].round(2)

    mdata.to_csv(file_out_monthly, index=False)
    ddata.to_csv(file_out_daily, index=False)
    data.to_csv(file_out_hourly, index=False)
    return mdata, ddata

df_vary = read_proc_write(files_vary, fileout_vary_monthly, fileout_vary_daily, fileout_vary_hourly)
df_const = read_proc_write(files_const, fileout_const_monthly, fileout_const_daily, fileout_const_hourly)
