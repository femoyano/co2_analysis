#!/usr/bin/env python
# coding: utf-8

def get_tmp_mean(
    tmp_file='/Users/moyanofe/BigData/GeoSpatial/Climate/CRU-TS_4.05_1901-2020/cru_ts4.05.1901.2020.tmp.dat.nc',
    limS=30,
    limN=80):
    # Function calculates averages for yearly and seasonally for region of interest saves to file.
    # limS: southernmost latidude to determine region of interest
    # limN: northernmost latidude to determine region of interest


    # Load modules ----

    import numpy as np
    import pandas as pd
    import xarray as xr


    # Load the data adn select region ----

    ds_t = xr.open_dataset(tmp_file)
    da_t = ds_t['tmp']
    da_tr = da_t.sel(lat=slice(limS,limN)) # Get values only for the region of interest


    # Get yearly averages for the region ----

    # See https://docs.xarray.dev/en/stable/examples/area_weighted_temperature.html

    # First average in time
    da_try = da_tr.groupby('time.year').mean() # try = temperature, region, yearly
    # Then average for the region (weight by gridcell size)
    weights = np.cos(np.deg2rad(da_try.lat)) # cosine of latitude is a proxy of gridcell size
    weights.name = "weights" # Not sure why this is required 
    da_tryw = da_try.weighted(weights) # Get weighted values
    da_trym = da_tryw.mean(('lat', 'lon')) # Get the average over lat and lon


    # Get seasonal averages ----

    # See: https://docs.xarray.dev/en/stable/examples/monthly-means.html

    # To be precise, need to weight by the actual month lengths

    # First create a year_season coordinate used to group the data
    year_np = da_tr['time.year'].to_pandas()
    season_np = da_tr['time.season'].to_pandas()
    year_season_idx = pd.MultiIndex.from_arrays([year_np, season_np])
    da_tr.coords['year_season'] = ('time', year_season_idx)

    # Create a data array with number of days per month
    month_length = da_tr.time.dt.days_in_month

    # Calculate the weights for each month by grouping by 'year_season'.
    weights =  month_length.groupby("year_season") / month_length.groupby("year_season").sum()

    # Test that the sum of the weights for each season is 1.0. (No output or None is good)
    np.testing.assert_allclose(weights.groupby("year_season").sum().values, np.ones(480))

    # Calculate the weighted average for each season and year (i.e. the sum of the weighted values)
    da_trs = (da_tr * weights).groupby("year_season").sum(dim="time")

    # Get the average for the entire region (weight by gridcell size)
    weights = np.cos(np.deg2rad(da_trs.lat)) # cosine of latitude is a proxy of gridcell size
    weights.name = "weights"
    da_trsw = da_trs.weighted(weights) # Get weighted values
    da_trsm = da_trsw.mean(('lat', 'lon')) # Get the average over lat and lon


    # Convert to pandas df ----

    # First get the year-season coordinate and convert to a pandas MultiIndex
    ys = da_trsm['year_season'].to_pandas()
    index = pd.MultiIndex.from_tuples(ys)
    # Second convert arraydata and MultiIndex to dataframe (the latter maybe unnecessary)
    df1 = da_trsm.to_dataframe(name='tmp')
    df2 = index.to_frame()
    # Third concat the dfs and add the index
    ts = pd.concat([df1, df2], axis=1)
    ts = ts.set_index(index)
    ts.columns = ['tmp', 'year', 'season']


    # Add to the yearly dataframe ----

    tm = da_trym.to_dataframe(name='tmp_year')

    for s in ['DJF', 'MAM', 'JJA', 'SON']:
        name = 'tmp_' + s
        data = ts.loc[ts['season']==s, 'tmp']
        data = data.reset_index(level=1, drop=True)
        tm[name] = data


    # Save to file ----
    # file_out = 'tmp_yearly_means_' + str(limS) + str(limN) + 'N.csv'
    # tm.to_csv('../data/piao_2008/' + file_out)

    return tm
