# coding: utf-8

# Function to make correlation and time series plots

def make_plots(station, stations, start_year, end_year, ccg_output, tmp_per_station, common_tmp_file, data_dir, detrend=False, name="", tx=0.5):
    # station: station abbreviation as given in file
    # start_year: earliest starting year to select either as integer or as column in file with starting years
    # end_year: same as start_year but for latest year to select
    # name: string to add in file names

    from scipy import stats
    import pandas as pd
    import matplotlib.pyplot as plt

    # Prepare the data and calculate anomalies ----

    # Select time period for temperature data
    
    if isinstance(start_year, int):
        year_beg = start_year
    else:
        year_beg = int(stations.loc[stations['name']==station, start_year])

    if isinstance(end_year, int):
        year_end = end_year
    else:
        year_end = int(stations.loc[stations['name']==station, end_year])

    # Get the ccg data
    ccg_y = ccg_output[station]['yearly']
    azc = ccg_y['tcu_doy'].loc[ccg_y['year'].between(year_beg, year_end)]
    azc.loc[azc < 150] = azc.loc[azc < 150] + 365
    years = ccg_y['year'].loc[ccg_y['year'].between(year_beg, year_end)]

    # Get temperature data
    if tmp_per_station:
        tmp_file = data_dir + 'tmp_yearly_means_' + station + '.csv'
    else:
        tmp_file = common_tmp_file
    tmp_mean = pd.read_csv(tmp_file, index_col='year')
    tmp = tmp_mean.loc[years.iloc[0]:years.iloc[len(years)-1],'tmp_SON']

    # Calculate anomalies
    tmp_ano = tmp - tmp.mean()
    azc_ano = azc - azc.mean()

    xy = pd.DataFrame({'year': years, 'tmp_ano': tmp_ano.to_numpy(), 'azc_ano': azc_ano.to_numpy()})

    # Calculate regression and plot ----
    if detrend:
        lm = stats.linregress(xy['year'], xy['tmp_ano'])
        pred = lm.intercept + lm.slope * xy['year']
        xy.loc[:,'tmp_ano'] = xy['tmp_ano'] - pred

        lm = stats.linregress(xy['year'], xy['azc_ano'])
        pred = lm.intercept + lm.slope * xy['year']
        xy.loc[:,'azc_ano'] = xy['azc_ano'] - pred

    # Use scipy to get stats            
    # t, p = stats.kendalltau(x_in, y_in)[0] # used for ordinal data
    reg = stats.linregress(xy['tmp_ano'], xy['azc_ano'])
    r_val = "r = {:.3f}".format(reg.rvalue)
    p_val = "p = {:.3f}".format(reg.pvalue)
    azc_pred = reg.intercept + reg.slope * xy['tmp_ano']
    # r = np.sqrt(model.score(x, y))

    # Plot the correlation
    # xy = xy.sort_values(by='tmp_ano')
    plt.rcParams['figure.figsize'] = [5, 5]
    plt.plot(xy['tmp_ano'], xy['azc_ano'], 'o', color='grey', alpha=1, label='Temp anomaly vs AZC anomaly'+'\n'+r_val+'; '+p_val)
    plt.plot(xy['tmp_ano'], azc_pred, '--', color='grey')
    plt.title(label=station)
    plt.legend(loc='upper right')
    plt.show()

    # Plot the time series
    plt.rcParams['figure.figsize'] = [8, 5]
    fig,ax=plt.subplots()
    ax.plot(years, xy['azc_ano'], '--', color='red', label='AZC anomaly')
    ax.set_ylabel("Autumn zero crossing anomaly (days)", color="red")
    # ax.set_ylim([-15, 15])
    ax2=ax.twinx()
    ax2.plot(years, xy['tmp_ano'], '--', color='black', label='Autumn temperature anomaly', linewidth=2)
    ax2.set_ylabel("Autumn temperature anomaly (ºC)")
    # ax2.set_ylim([-2, 2])
    ax2.invert_yaxis()
    plt.title(station)
    plt.text(tx, 0.95, r_val+'; '+p_val, transform=ax.transAxes)
    plt.show()

    # Save the plot
    fig.savefig('../plots/' + name + '_' + station + '_azc-tmp.jpg',
                format='jpeg',
                dpi=100,
                bbox_inches='tight')   
    