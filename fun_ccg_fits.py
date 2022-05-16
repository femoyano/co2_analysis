# Function to do the ccg fits and return results in a practical format

def ccg_fits(data, pars):
    # data: a dataframe with variables: co2 and dec_year
    # pars: a dictionary with all the parameters used in the ccgFilter function below

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
    