#!/usr/bin/env python
# coding: utf-8

# ### Step 4: temperature averages for the northern latitudes
# - Read in temperature data. File: /Users/moyanofe/BigData/GeoSpatial/Climate/CRU-TS_4.05_1901-2020/cru_ts4.05.1901.2020.tmn.dat.nc
# - Calculate averages for:
#     - above 30ºN and above 50ºN (and below 80ºN)
#     - yearly and seasonally
# Note: check for useful code in trend calculations scripts

# -------
# Load modules
import numpy as np
import pandas as pd
import xarray as xr
import glob
import os
import rioxarray


# -------
# Read in and process data

file = '/Users/moyanofe/BigData/GeoSpatial/Climate/CRU-TS_4.05_1901-2020/cru_ts4.05.1901.2020.tmp.dat.nc'
ds_t = xr.open_dataset(file)
da_t = ds_t['tmp']


# -------
# Get yearly averages 
da_ty = da_t.groupby('time.year').mean()
da_ty3080N = da_ty.sel(lat=slice(30,80))
da_ty3080Nm = da_ty3080N.mean(dim=['lat', 'lon'])


# -------
# Get seasonal averages
# See: https://docs.xarray.dev/en/stable/examples/monthly-means.html

# To be precise, need to weight by the actual month lengths

# First create a year_season coordinate used to group the data
year_np = da_t['time.year'].to_pandas()
season_np = da_t['time.season'].to_pandas()
year_season_idx = pd.MultiIndex.from_arrays([year_np, season_np]) 
da_t.coords['year_season'] = ('time', year_season_idx)

# Create a data array with number of days per month
month_length = da_t.time.dt.days_in_month

# Calculate the weights for each month by grouping by 'year_season'.
weights =  month_length.groupby("year_season") / month_length.groupby("year_season").sum()

# Test that the sum of the weights for each season is 1.0. (No output or None is good)
np.testing.assert_allclose(weights.groupby("year_season").sum().values, np.ones(480))

# Calculate the weighted average for each season and year
da_ts = (da_t * weights).groupby("year_season").sum(dim="time")

# Select latitudes above 3080N
# Use .sel, not .isel, to select based on coordinate names (not dimension index)
da_ts3080N = da_ts.sel(lat=slice(30,80)) 

# Get the average for the entire region (weight by gridcell size)
weights = np.cos(np.deg2rad(da_ts3080N.lat)) # cosine is a proxy of gridcell size
weights.name = "weights"
da_ts3080Nw = da_ts3080N.weighted(weights)
da_ts3080Nwm = da_ts3080Nw.mean(('lat', 'lon'))
# da_ts3080Nwm = da_ts3080Nw.mean(dim=['lat', 'lon'])


# ------
# Convert to pandas df

# First get the year-season coordinate and convert to a pandas MultiIndex
ys = da_ts3080Nwm['year_season'].to_pandas()
index = pd.MultiIndex.from_tuples(ys)
# Second convert arraydata and MultiIndex to dataframe (the latter maybe unnecessary)
df1 = da_ts3080Nwm.to_dataframe(name='tmp')
df2 = index.to_frame()
# Third concat the dfs and add the index
ts3080N = pd.concat([df1, df2], axis=1)
ts3080N = ts3080N.set_index(index)
ts3080N.columns = ['tmp', 'year', 'season']

# del [file, ds_t]
# del [year_np, season_np, year_season_idx]
# del [month_length, weights, da_ts, da_ts3080N]
# del [df1, df2, ys, index]

# Add to the yearly dataframe
ty3080Nm = da_ty3080Nm.to_dataframe(name='tmp_year')

for s in ['DJF', 'MAM', 'JJA', 'SON']:
    name = 'tmp_' + s
    data = ts3080N.loc[ts3080N['season']==s, 'tmp']
    data = data.reset_index(level=1, drop=True)
    ty3080Nm[name] = data

