# Process co2 data

# Some NA removal
data <- read.csv('ccgcrv_c/co2_brw_monthly_dectime_value.txt', sep = ' ',
                 header = FALSE, na.strings = '-999.99')
data <- data[!is.na(data$V2),]

# Write the data out without headers so it can be read in directly by ccgcrv
write.table(x = data, file = 'co2_brw_monthly_dectime_value.txt', sep = ' ',
            row.names = FALSE, col.names = FALSE)
