import xarray as xr
import netCDF4
import h5netcdf

# read the file
data = xr.open_dataset('/Users/wangy/Documents/MACS/Thesis/Alicante_features_regrid_merged.nc')
# check the structure
print(data)



