obsmod <- read.csv("obsmod.csv")
X <- obsmod$decimal_year
y <- obsmod$co2_ppm_obs
lmod1 <- lm(y~X)
obsmod$co2_ppm_obs_tr <- predict(lmod1)
obsmod$co2_ppm_obs_dt <- obsmod$co2_ppm_obs - obsmod$co2_ppm_obs_tr
y <- obsmod$co2_ppm_sim
lmod1 <- lm(y~X)
obsmod$co2_ppm_sim_tr <- predict(lmod1)
obsmod$co2_ppm_sim_dt <- obsmod$co2_ppm_sim - obsmod$co2_ppm_sim_tr

plot(obsmod$co2_ppm_sim_dt, type='l')
lines(obsmod$co2_ppm_obs_dt, type='l', col=2)
