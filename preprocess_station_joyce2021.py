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
dataout_dir = Path("../data/stations/monthly")
if not os.path.exists(dataout_dir):
    os.makedirs(dataout_dir)

files_const = sorted(glob(os.path.realpath(datain_dir/"BRW_station_co2_atmos_const*")))
files_vary = sorted(glob(os.path.realpath(datain_dir/"BRW_station_co2_atmos_vary*")))

file_vary_out = dataout_dir / "BRW_station_co2_joyce_varyall.csv"
file_const_out = dataout_dir / "BRW_station_co2_joyce_constmet.csv"

def read_proc_write(files, file_out):
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

    # Then calculate the total CO2 concentrations and aggregate to monthly means
    data['co2'] = data["Background"] + data["FF"] + data["Ocean"] + data["NEE_ctrl"] + data["FIRE_ctrl"]
    mdata = data.groupby(['Year', 'Month']).agg(np.mean)
    
    # Crate and format dataframe
    co2_df = mdata[['Dec_year', 'co2']]
    co2_df.columns = ["decimal_year", "co2_ppm"]
    # Round both variables to two digits to match observation monthly file
    co2_df = co2_df.round(2)
    # Adjust time of month to match observation file
    co2_df['decimal_year'] = co2_df['decimal_year'] - 0.04 
    co2_df.columns = ['decimal_year', 'co2_ppm_sim']
    co2_df.to_csv(file_out)
    return(co2_df)

df_vary = read_proc_write(files_vary, file_vary_out)
df_const = read_proc_write(files_const, file_const_out)

