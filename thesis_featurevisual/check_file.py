import xarray as xr
import netCDF4
import h5netcdf

# read the file
data = xr.open_dataset('/Users/wangy/Documents/MACS/Thesis/variables/LCZ_Brussels_UrbClim_2015_01_v1.0.nc')
# check the structure
print(data)


