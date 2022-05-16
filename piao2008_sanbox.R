y <- co2_day$year[co2_day$station=='BRW' & co2_day$method=='insitu']
y <- co2_eve$year[co2_eve$station=='BRW' & co2_eve$method=='flask']

range(y)
