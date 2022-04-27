# This scripts uses the ccg_filter python module to fit a model of co2 to measured data
# Measured data must be in ´fileien´ and needs to have two columns without headers: 
# the first in decimal year format and the second in co2 concentrations (ppm)

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from ccgcrv_python import ccg_filter

# filein should have missing value rows removed since it doesn't seem to work otherwise.
filein = 'co2_filein.txt'
# data = pd.read_csv(filein, delimiter = ' ', header=None, names=['time_decimal', 'co2_ppm'])
data = pd.read_csv(filein, delimiter = ' ', header = 0, names = ['time_decimal', 'co2_ppm'])

xp = data["time_decimal"].to_numpy()
yp = data["co2_ppm"].to_numpy()

shortterm = 80
longterm = 667
sampleinterval = 30
numpolyterms=3
numharmonics=4
timezero=-1
gap=0
use_gain_factor=False,
use_gain_factor=False,
debug=False

# create the ccgfilt object
# filt = ccg_filter.ccgFilter(xp=xp, yp=yp, shortterm=shortterm, longterm=longterm,
#     sampleinterval=sampleinterval, numpolyterms=numpolyterms,
#     numharmonics=numharmonics, timezero=timezero, gap=gap, debug=debug)
filt = ccg_filter.ccgFilter(xp=xp, yp=yp)
#
mm = filt.getMonthlyMeans()
amps = filt.getAmplitudes()
tcup, tcdown = filt.getTrendCrossingDates()

# get x,y data for plotting
x0 = filt.xinterp
y1 = filt.getFunctionValue(x0)
y2 = filt.getPolyValue(x0)
y3 = filt.getSmoothValue(x0)
y4 = filt.getTrendValue(x0)

# plt.plot(x0, y1)


""" 
# Seasonal Cycle
# x and y are original data points
trend = filt.getTrendValue(x)
detrend = y - trend
harmonics = filt.getHarmonicValue(x0)
smooth_cycle = harmonics + filt.smooth - filt.trend
# residuals from the function
resid_from_func = filt.resid
# smoothed residuals
resid_smooth = filt.smooth
# trend of residuals
resid_trend = filt.trend
# residuals about the smoothed line
resid_from_smooth = filt.yp - filt.getSmoothValue(x)
# equally spaced interpolated data with function removed
x1 = filt.xinterp
y9 = filt.yinterp
 """
