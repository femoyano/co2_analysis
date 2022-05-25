#!/usr/bin/env python
# coding: utf-8

# 1. Create daily dataset by aggregating event data and adding to daily file
# 2. Create monthly data by aggregating the daily file and adding to monthly

def proc_co2data(file_co2='../data/piao_2008/piao2008_co2_flask.csv',
    fileout_co2='../data/piao_2008/co2_fm.csv'):

    # Required modules
    from ccgcrv import ccg_dates
    import pandas as pd
    from copy import deepcopy

    # Read in the data
    co2_f = pd.read_csv(file_co2)

    # One station has two names: SSL and SCH. Set all to SSL (newer name)
    co2_f.loc[co2_f['station'] == 'SCH', 'station'] = 'SSL'

    # Separate monthly from event data
    co2_fm = co2_f.loc[co2_f['freq'] == 'monthly', :]
    co2_fe = co2_f.loc[co2_f['freq'] == 'event', :]

    # Get daily averages from event data and remove the averaged hour column
    co2_fd = co2_fe.groupby(['station','year','month','day'], as_index=False).mean() 
    co2_fd.drop(['hour'], axis=1, inplace=True)

    # Get monthly averages from daily data and remove unnecessary columns
    co2_fm2 = co2_fd.groupby(['station','year','month'], as_index=False).mean()
    co2_fm2.drop(['day', 'stdev'], axis=1, inplace=True)


    # Merge and select data
    # The calculated averages have many outliers, so monthly values as downloaded are used when available.  

    # Merge monthly dataframes
    co2_fm1 = deepcopy(co2_fm)
    co2_fm1['key'] = co2_fm1['station'] + co2_fm1['year'].astype(str) + co2_fm1['month'].astype(str)
    co2_fm2['key'] = co2_fm2['station'] + co2_fm2['year'].astype(str) + co2_fm2['month'].astype(str)
    co2_fm = co2_fm1.join(co2_fm2.set_index('key'), on='key', how='outer', lsuffix='_orig', rsuffix='_calc')
    co2_fm.reset_index(inplace=True)


    # Restructure and select the data

    co2_fm['station'] = co2_fm['station_orig']
    co2_fm['year'] = co2_fm['year_orig']
    co2_fm['month'] = co2_fm['month_orig']
    co2_fm['co2'] = co2_fm['co2_orig']

    is_na = co2_fm['station_orig'].isna()
    co2_fm.loc[is_na, 'station'] = co2_fm['station_calc'].loc[is_na]
    is_na = co2_fm['year_orig'].isna()
    co2_fm.loc[is_na, 'year'] = co2_fm['year_calc'].loc[is_na]
    is_na = co2_fm['month_orig'].isna()
    co2_fm.loc[is_na, 'month'] = co2_fm['month_calc'].loc[is_na]
    is_na = co2_fm['co2_orig'].isna()
    co2_fm.loc[is_na, 'co2'] = co2_fm['co2_calc'].loc[is_na]
    del is_na

    co2_fm.drop(['station_orig', 'station_calc', 'year_orig', 'year_calc', 'month_orig', 'month_calc', 'key'], axis=1, inplace=True)

    # Calculate the decimal year
    from ccgcrv import ccg_dates
    co2_fm['dec_year'] = co2_fm.apply(lambda row: ccg_dates.decimalDate(int(row['year']),
            int(row['month']), 15), axis=1)

    # Write out results
    co2_fm.to_csv(fileout_co2)



def select_piao2008(file_co2='../data/piao_2008/co2_fm.csv', file_stations='../data/co2_station_summary.csv',
    fileout_co2='../data/piao_2008/piao_stations.csv', fileout_stations='../data/piao_2008/piao_co2_fm.csv'):

    import pandas as pd

    # Select stations for analysis -----
    # Information about each station is in the file data/co2_station_summary.csv
    # Steps:
    # - Add dates to station description file
    # - Read file
    # - Create new dataframe with selection according to dates

    co2 = pd.read_csv(file_co2)

    # Read in station summary
    stations = pd.read_csv(file_stations)
    # Select stations used by piao2008
    piao_stations = stations.loc[stations['piao_2008']==True,:]
    # Select data for the selected stations
    is_sel = co2['station'].isin(piao_stations['name'])
    piao_co2_fm = co2.loc[is_sel, :] # at the moment they are all piao stations

    piao_stations.to_csv(fileout_co2)
    piao_co2_fm.to_csv(fileout_stations)
