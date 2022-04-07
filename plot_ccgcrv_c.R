# This script reads and plots output from the ccgcrv C executable
# Check the ccgcrv documentation to determine output file columns and adjust the column names (colnames) accordingly 

colnames <- c('decyear', 'orig', 'func', 'poly', 'smooth', 'trend', 'detrend',
           'smscycle', 'harm', 'res', 'smres', 'trres', 'ressm', 'gr')
data <- read.delim('ccgcrv_c/out.txt', sep = ' ', header = FALSE, col.names = colnames)

plot(data$orig~data$decyear, type='l')
lines(data$func~data$decyear, col=2)

plot(data$decyear, data$detrend, type='l')
lines(data$decyear, data$smscycle, col=2)

plot(data$decyear, data$gr, type='l')
plot(data$decyear, data$harm, type='l')
plot(data$decyear, data$smooth, type='l')
plot(data$decyear, data$trend, type='l')
plot(data$decyear, data$poly, type='l')
plot(data$decyear, data$func, type='l')
plot(data$decyear, data$smscycle, type='l')

# Write function to get amplitudes by looping over years

data$year <- floor(data$decyear)
