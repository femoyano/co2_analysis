#!/usr/bin/env python
# coding: utf-8

def get_ccgcrv(co2_file, stations_file, start_col = 'start_total', end_col = 'end_total'):
    # Function takes a list of stations and respective co2 time series and outputs ccgcrv fitted data.
    # ccgcrv module function is used and results saved in a dictionary, with keys being station names
    # co2_file: file with the co2 data
    # stations_file: file with station summary data
    # start_col: column in stations_file with starting year
    # end_col: column in stations_file with ending year

    from fun_ccg_fits import ccg_fits
    import pandas as pd
    from copy import deepcopy
    import numpy as np

    # Read in data
    co2_fm = pd.read_csv(co2_file)
    stations = pd.read_csv(stations_file)

    # Default parameter values as used in the ccgcrv code.
    ccg_pars_def = {
        'shortterm': 80,
        'longterm': 667,
        'sampleinterval': 0,
        'numpolyterms': 3,
        'numharmonics': 4,
        'timezero': -1,
        'gap': 0,
        'use_gain_factor': False,
        'debug': False
    }

    # Set sampleinterval to 1
    ccg_pars1 = deepcopy(ccg_pars_def)
    ccg_pars1['sampleinterval'] = 1

    # Get ccgcrv fits for each station and save to a dictionary
    ccg_output = dict()

    for s in stations['name'].unique():
        ystart = int(stations.loc[stations['name'] == s, start_col])
        yend = int(stations.loc[stations['name'] == s, end_col])
        sel = (co2_fm['station'] == s) & (co2_fm['year'].between(ystart, yend, inclusive='both'))
        input = co2_fm.loc[sel, ['co2', 'dec_year']]
        
        # Need to add one row with value for following year. Otherwise no results returned for last year (bug in ccvcrg?).
        ar = np.arange(len(input))
        input = input.iloc[np.append(ar, ar[-1])]
        col_y = input.columns.get_loc('dec_year')
        input.iloc[-1, col_y] = np.round(input.iloc[-1, col_y]+1)

        # Now call ccgcrv
        out = ccg_fits(data=input, pars=ccg_pars1)
        ccg_output[s] = out


    # Create dataframe with stations and results ----

    # Here could remove bad years e.g. by using the Gini coefficient as in Forkel 2016

    ccgmeans = deepcopy(pd.DataFrame(stations['name']))
    ccgmeans['amp_mean'] = np.nan
    ccgmeans['min_mean'] = np.nan
    ccgmeans['max_mean'] = np.nan
    ccgmeans['szc_mean'] = np.nan
    ccgmeans['azc_mean'] = np.nan

    for s in stations['name'].unique():
        res = ccg_output[s]
        amp_mean = res['yearly']['amp'].mean()
        min_mean = res['yearly']['min_value'].mean()
        max_mean = res['yearly']['max_value'].mean()
        szc_mean = res['yearly']['tcd_doy'].mean()
        azc_mean = res['yearly']['tcu_doy'].mean()
        ccgmeans.loc[ccgmeans['name']==s, 'amp_mean'] = np.round(amp_mean, 2)
        ccgmeans.loc[ccgmeans['name']==s, 'min_mean'] = np.round(min_mean, 2)
        ccgmeans.loc[ccgmeans['name']==s, 'max_mean'] = np.round(max_mean, 2)
        ccgmeans.loc[ccgmeans['name']==s, 'szc_mean'] = int(szc_mean)
        ccgmeans.loc[ccgmeans['name']==s, 'azc_mean'] = int(azc_mean)

    return ccg_output, ccgmeans
