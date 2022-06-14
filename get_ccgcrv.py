# coding: utf-8

def ccgcrv_fit_mult(co2_file, stations_file, ccg_pars, start_col = 'start_total', end_col = 'end_total'):
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
        out = ccg_fits(data=input, pars=ccg_pars)
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


# Define function to do the ccg fits and return results in a practical format
def ccgcrv_fit_one(data, pars):
    from ccgcrv import ccg_filter
    from ccgcrv import ccg_dates
    import pandas as pd

    data = data.loc[data['co2'].notna(), :] # Data cannot have missing values.
    xp = data["dec_year"].to_numpy()
    yp = data["co2"].to_numpy()

    # create the ccgfilt object
    filt = ccg_filter.ccgFilter(xp=xp, yp=yp, shortterm=pars['shortterm'],
                                longterm=pars['longterm'], sampleinterval=pars['sampleinterval'],
                                numpolyterms=pars['numpolyterms'], numharmonics=pars['numharmonics'],
                                timezero=pars['timezero'], gap=pars['gap'], debug=pars['debug'])
    # filt = ccg_filter.ccgFilter(xp=xp, yp=yp)

    pred1 = pd.DataFrame({
        'x': xp,
        'func': filt.getFunctionValue(xp),
        'smooth': filt.getSmoothValue(xp),
        'trend': filt.getTrendValue(xp),
        'harm': filt.getHarmonicValue(xp),
        'poly': filt.getPolyValue(xp)
        })
    
    x0 = filt.xinterp
    pred2 = pd.DataFrame({
        'x0': x0,
        'func': filt.getFunctionValue(x0),
        'smooth': filt.getSmoothValue(x0),
        'trend': filt.getTrendValue(x0),
        'harm': filt.getHarmonicValue(x0),
        'poly': filt.getPolyValue(x0)
        })

    # mm = filt.getMonthlyMeans()
    amps = filt.getAmplitudes()
    yearly = pd.DataFrame(amps,
        columns=['year', 'amp', 'max_date', 'max_value', 'min_date', 'min_value']) # Returns a list of tuples, each tuple has 6 values (year, total_amplitude, max_date, max_value, min_date, min_value)

    tcup, tcdown = filt.getTrendCrossingDates()

    decyear = pd.Series(tcdown)
    cal = decyear.transform(ccg_dates.calendarDate)
    tcd = pd.DataFrame(cal.to_list(), 
        columns=['year', 'month', 'day', 'hour', 'minute', 'second'])
    tcd['doy'] = tcd.apply(lambda row: ccg_dates.dayOfYear(row['year'].astype(int),
        row['month'].astype(int), row['day'].astype(int)), axis=1)

    decyear = pd.Series(tcup)
    cal = decyear.transform(ccg_dates.calendarDate)
    tcu = pd.DataFrame(cal.to_list(),
        columns=['year', 'month', 'day', 'hour', 'minute', 'second'])
    tcu['doy'] = tcu.apply(lambda row: ccg_dates.dayOfYear(row['year'].astype(int),
        row['month'].astype(int), row['day'].astype(int)), axis=1)
    
    yearly['tcd_doy'] = tcd['doy']
    yearly['tcd_dec'] = pd.Series(tcdown)
    yearly['tcu_doy'] = tcu['doy']
    yearly['tcu_dec'] = pd.Series(tcup)

    out = {'pred_xobs':pred1, 'pred_xint':pred2, 'yearly':yearly}

    return(out)

