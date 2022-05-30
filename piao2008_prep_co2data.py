# coding: utf-8

def proc_co2data(file_co2raw, file_co2_proc, co2_avg_freq):

    # 1. Create daily dataset by aggregating event data and adding to daily file
    # 2. Create monthly data by aggregating the daily file and adding to monthly

    # co2_avg_freg should be monthly, daily or raw

    # Required modules
    from ccgcrv import ccg_dates
    import pandas as pd

    # Read in the data
    co2_f = pd.read_csv(file_co2raw)

    # One station has two names: SSL and SCH. Set all to SSL (newer name)
    co2_f.loc[co2_f['station'] == 'SCH', 'station'] = 'SSL'

    # Separate monthly from event data
    co2_fm = co2_f.loc[co2_f['freq'] == 'monthly', :]
    # co2_fd = co2_f.loc[co2_f['freq'] == 'daily', :]
    co2_fe = co2_f.loc[co2_f['freq'] == 'event', :]

    # Get daily averages from event data and remove the averaged hour column
    co2_fd2 = co2_fe.groupby(['station','year','month','day'], as_index=False).mean() 
    co2_fd2.drop(['hour'], axis=1, inplace=True)

    # Get monthly averages from daily data and remove unnecessary columns
    co2_fm2 = co2_fd2.groupby(['station','year','month'], as_index=False).mean()
    co2_fm2.drop(['stdev'], axis=1, inplace=True)

    # Merge and select data
    # The calculated averages have many outliers, so raw monthly values (as downloaded) are used when available.  
    
    # Chose frequency: the averaged values are merged with the raw monthly values
    if co2_avg_freq == 'daily' or co2_avg_freq == 'monthly':

        if co2_avg_freq == 'daily':
            co2_1 = co2_fm
            co2_2 = co2_fd2
            co2_1['key'] = co2_1['station'] + co2_1['year'].astype(str) + co2_1['month'].astype(str) + co2_1['day'].astype(str)
            co2_2['key'] = co2_2['station'] + co2_2['year'].astype(str) + co2_2['month'].astype(str) + co2_2['day'].astype(str)

        if co2_avg_freq == 'monthly':
            co2_1 = co2_fm
            co2_2 = co2_fm2
            co2_1['key'] = co2_1['station'] + co2_1['year'].astype(str) + co2_1['month'].astype(str)
            co2_2['key'] = co2_2['station'] + co2_2['year'].astype(str) + co2_2['month'].astype(str)

        
        co2_out = co2_1.join(co2_2.set_index('key'), on='key', how='outer', lsuffix='_orig', rsuffix='_calc')
        co2_out.drop(['key'], axis=1, inplace=True)
        co2_out.reset_index(inplace=True)

        # Select raw when available, otherwise calculated and select the data
        for col in ['station', 'year', 'month', 'day', 'co2']:
            col_orig = col+'_orig'
            col_calc = col+'_calc'
            co2_out[col] = co2_out[col_orig]
            is_na = co2_out[col_orig].isna()
            co2_out.loc[is_na, col] = co2_out[col_calc].loc[is_na]
            co2_out.drop([col_orig, col_calc], axis=1, inplace=True)

    # If freq is raaw, just take the raw data
    elif co2_avg_freq == 'raw':
        co2_out = co2_f

    # Calculate the decimal year
    from ccgcrv import ccg_dates
    co2_out['dec_year'] = co2_out.apply(lambda row: ccg_dates.decimalDate(int(row['year']),
            int(row['month']), 15), axis=1)

    # Write out results
    co2_out.to_csv(file_co2_proc)



def select_piao2008(file_co2, file_stations, fileout_co2, fileout_stations):

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
    piao_co2_out = co2.loc[is_sel, :] # at the moment they are all piao stations

    piao_stations.to_csv(fileout_stations)
    piao_co2_out.to_csv(fileout_co2)
