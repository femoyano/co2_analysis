# This is the main executable script that calls the python script
# to fit co2 model to observations and creates plots

library(reticulate)
library(ggplot2)

# Data should already be in two columns, decimal_year and co2_ppm, and without rows with missing values

# obsfile <- 'data/'
# obsfile <- 'data/co2_brw_surface-insitu_1_ccgg_monthly.txt'
obsfiles <- dir('data_subset1/')

sites <- NA
colors <- c(black="black", red="red", blue='blue', green='green')
# colors <- terrain.colors(length(obsfiles))

df_out <- data.frame(site = character(), x0=double(), y1=double(), y2=double(), y3=double(), y4=double())
df_orig <- data.frame(site = character(), xp=double(), yp=double())
df_amp <- data.frame(site = character(), year=double(), amplitude=double())

for (i in 1:length(obsfiles)) {
  
  filein <- obsfiles[i]
  site <- tools::file_path_sans_ext(filein)
  names(colors)[i] <- site
  data <- read.csv(file.path('data', filein), sep = '', header = TRUE, na.strings = '-999.99')
  data <- data[!is.na(data$co2_ppm),]
  
  # Write the data out without headers so it can be read in directly by ccgcrv
  write.table(x = data, file = 'co2_filein.txt', sep = ' ', row.names = FALSE)
  
  source_python('fit_co2.py')
  
  year <- sapply(amps,"[[",1)
  amplitude <- sapply(amps,"[[",2)
  
  df_out <- rbind(df_out, data.frame(site = site, x0=x0, y1=y1, y2=y2, y3=y3, y4=y4)) 
  df_orig <- rbind(df_orig, data.frame(site = site, xp=xp, yp=yp)) 
  df_amp <- rbind(df_amp, data.frame(site = site, year=year, amplitude=amplitude))
}

# Plot the measured and modeled CO2
co2_plot <- ggplot(data = df_out, aes(x0, y1, colour = site)) + geom_line() + theme_bw()
print(co2_plot)

co2_amp <- ggplot(data = df_amp, aes(year, amplitude, colour = site)) +
  geom_line(alpha = 0.5) + 
  geom_point() +
  geom_line(stat="smooth", method = "lm", se = FALSE, linetype = "dashed", alpha = 0.5) +
  theme_bw() +
  theme(legend.position = c(0.2, 0.8))
print(co2_amp)
