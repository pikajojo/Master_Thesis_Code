import xarray as xr
import pandas as pd

# 打开NetCDF文件
ds = xr.open_dataset('/content/drive/My Drive/thesis/era5/ERA5_2015_07.nc')

# 提取经纬度范围
lon_min, lon_max = 4.0, 4.5
lat_min, lat_max = 50.5, 51.0

# 选择经纬度范围
lon_range = (ds.variables['longitude'][:] >= lon_min) & (ds.variables['longitude'][:] <= lon_max)
lat_range = (ds.variables['latitude'][:] >= lat_min) & (ds.variables['latitude'][:] <= lat_max)

# 初始化一个空的DataFrame来存放所有变量的数据
era5_df = pd.DataFrame()

# 遍历所有变量
for var_name in ds.data_vars:
    # 提取区域数据
    var_region = ds[var_name][:, lat_range, lon_range]

    # 将变量转换为DataArray
    var_region_da = xr.DataArray(
        var_region,
        dims=["time", "latitude", "longitude"],
        coords={
            "time": ds.variables["time"][:],
            "latitude": ds.variables["latitude"][lat_range],
            "longitude": ds.variables["longitude"][lon_range]
        }
    )

    # 将DataArray转换为DataFrame，并重置索引
    var_df = var_region_da.to_dataframe(name=var_name).reset_index()

    # 合并数据
    if era5_df.empty:
        era5_df = var_df
    else:
        era5_df = era5_df.merge(var_df, on=["time", "latitude", "longitude"], how="outer")

# 查看合并后的DataFrame
print(era5_df)