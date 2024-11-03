import xarray as xr
import xarray_regrid
Brussels_urb = '/Users/wangy/Documents/MACS/Thesis/UrbClim_data/reference/tas_Brussels_UrbClim_reference.nc'
Brussels_tas = xr.open_dataset(Brussels_urb)

target_tas = Brussels_tas['tas']

print(target_tas)



source_ds = xr.open_dataset('/Users/wangy/Documents/MACS/Thesis/UrbClim_data/tas_Brussels_UrbClim_2015_07_v1.0.nc')
# 删除 'x' 和 'y' 坐标
source_ds = source_ds.drop_vars(['x', 'y'])
# 设置 'latitude' 和 'longitude' 为新的坐标
source_ds = source_ds.set_coords(['latitude', 'longitude'])
source_ds = source_ds.rename({'latitude': 'y', 'longitude': 'x'})

source_ds['x'] = source_ds['x'].astype('float64')
source_ds['y'] = source_ds['y'].astype('float64')
print(source_ds)
# source_tas = source_ds['tas'].to_dataframe().reset_index()
# source_tas = source_tas.drop(columns = ['y', 'x',])
# source_tas = source_tas.rename(columns={'latitude': 'y', 'longitude': 'x'})
# print(source_tas)


source_ds['tas'].regrid.linear(target_tas)

print(source_ds)
