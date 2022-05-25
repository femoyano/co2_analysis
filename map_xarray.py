# Plot xarray

def map_xarray(da):
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import xarray as xr
    import cartopy.crs as ccrs

    p = da.isel(time=0).plot(
    subplot_kws=dict(projection=ccrs.Orthographic(-80, 90), facecolor="white"),
    transform=ccrs.PlateCarree(),
    )
    p.axes.set_global()
    p.axes.coastlines()
