from ccgcrv import ccg_filter
from ccgcrv import ccg_dates
import pandas as pd
import numpy as np
from copy import deepcopy

# Naming:
# brw = Point Barrow; (method) i,f,m=insitu,flask,merge; (frequency) d,m,h,e=daily,monthly,hourly,event; 
# (origin) uk,no,sc=unkown,noaa,scripps
brw_i_d_uk = pd.read_csv('../data/piao_test/brw-insitu_day.csv')
brw_i_m_uk = pd.read_csv('../data/piao_test/brw-insitu_mon.csv')
brw_f_m_uk = pd.read_csv('../data/piao_test/brw-flask_mon.csv')
brw_f_e_no = pd.read_csv('../data/piao_test/co2_brw_surface-flask_1_ccgg_event.csv')
brw_f_m_no = pd.read_csv('../data/piao_test/co2_brw_surface-flask_1_ccgg_month.csv')
brw_i_h_no = pd.read_csv('../data/piao_test/co2_brw_surface-insitu_1_ccgg_HourlyData.csv')
brw_i_d_no = pd.read_csv('../data/piao_test/co2_brw_surface-insitu_1_ccgg_DailyData.csv')
brw_i_m_sc = pd.read_csv('../data/piao_test/co2_brw_surface-insitu_1_ccgg_MonthlyData.csv')
brw_f_d_sc = pd.read_csv('../data/piao_test/scripps_daily_flask_co2_ptb.csv')
brw_m_d_sc = pd.read_csv('../data/piao_test/scripps_daily_merge_co2_ptb.csv')
brw_f_m_sc = pd.read_csv('../data/piao_test/scripps_monthly_flask_co2_ptb.csv')
brw_m_m_sc = pd.read_csv('../data/piao_test/scripps_monthly_merge_co2_ptb.csv')

data = deepcopy(brw_f_e_no)

data.columns = ['site_code', 'year', 'month', 'day', 'hour', 'co2']
data['dec_year'] = data.apply(lambda row: ccg_dates.decimalDate(row['year'], row['month'], row['day'], row['hour']), axis=1)

data =  data[['dec_year', 'co2']]
data.loc[data['co2'] < 0, 'co2'] = np.nan

brw_f_e_no.columns = ['site_code', 'year', 'month', 'day', 'hour', 'co2']
brw_f_e_no['dec_year'] = np.round(brw_f_e_no.apply(lambda row: ccg_dates.decimalDate(row['year'],
        row['month'], row['day'], row['hour']), axis=1), 2)
brw_f_e_no['dec_year'] = brw_f_e_no.apply(lambda row: ccg_dates.decimalDate(row['year'],
        row['month'], row['day'], row['hour']), axis=1)
brw_f_e_no = brw_f_e_no[['dec_year', 'co2']]
brw_f_e_no.to_csv('../data/piao_test/brw_f_e_no.csv')

brw_fl_er1['dec_year'] = np.round(brw_fl_er1.apply(lambda row: ccg_dates.decimalDate(row['year'].astype(int),
        row['month'].astype(int), row['day'].astype(int), row['hour'].astype(int)), axis=1), 2)


# # Read in Joyce data
# joyce_yrly = pd.read_csv('../data/ccgcrv_testing/BRW_SZC_JoyceGRL2021.csv')

# joyce_monthly = pd.read_csv('../data/ccgcrv_testing/BRW_CO2_monthly_joyce_varyall.csv')
# joyce_monthly['dec_year'] = np.round(joyce_monthly.apply(lambda row: ccg_dates.decimalDate(row['year'].astype(int),
#         row['month'].astype(int), 1), axis=1), 2) + 0.08 # Adding 0.08 so it ends in 2013.0. Otherwise 2012 amp is not calculated.

# joyce_daily = pd.read_csv('../data/ccgcrv_testing/BRW_CO2_daily_joyce_varyall.csv')
# joyce_daily['dec_year'] = np.round(joyce_daily.apply(lambda row: ccg_dates.decimalDate(row['year'].astype(int),
#         row['month'].astype(int), row['day'].astype(int)), axis=1), 2)

# joyce_hourly = pd.read_csv('../data/ccgcrv_testing/BRW_CO2_3hourly_joyce_constmet.csv')
# joyce_hourly['dec_year'] = np.round(joyce_hourly.apply(lambda row: ccg_dates.decimalDate(row['year'].astype(int),
#         row['month'].astype(int), row['day'].astype(int), row['hour'].astype(int)), axis=1), 2)
