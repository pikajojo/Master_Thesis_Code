import numpy as np
from scipy.interpolate import RegularGridInterpolator
import matplotlib.pyplot as plt
import pandas as pd
import xarray as xr

# 打开NetCDF文件
ds = xr.open_dataset('/Users/wangy/Documents/MACS/Thesis/ERA5_variables/ERA5_2015_07.nc')
urbclim_coor = pd.read_csv('/Users/wangy/Documents/MACS/Thesis/UrbClim_data/Brussels/urbclim_coordinates.csv',
                          index_col=0)

# extract the min and max of latitude and longitude

# lat_min = urbclim_cor['y'].min()
# lat_max = urbclim_cor['y'].max()
#
# lon_min = urbclim_cor['x'].min()
# lon_max = urbclim_cor['x'].max()

# 选择经纬度范围
lon_range = (ds.variables['longitude'][:] >= 3.9) & (ds.variables['longitude'][:] <= 4.6)
lat_range = (ds.variables['latitude'][:] >= 50.4) & (ds.variables['latitude'][:] <= 51.1)

# 初始化一个空的DataFrame来存放所有变量的数据

era5_2015_07_df = pd.DataFrame()
# ds = ds[['t2m']]
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
    if era5_2015_07_df.empty:
        era5_2015_07_df = var_df
    else:
        era5_2015_07_df = era5_2015_07_df.merge(var_df, on=["time", "latitude", "longitude"], how="outer")

# 查看合并后的DataFrame
print(era5_2015_07_df)
t2m = era5_2015_07_df[['t2m']]

# 1. 创建低分辨率 map 的网格和数据
low_res_x = np.array(era5_2015_07_df[['longitude']])  # x 方向有 5 个点
low_res_y = np.array(era5_2015_07_df[['latitude']]) # y 方向有 5 个点
low_res_values = t2m # 5x5 的随机数据（低分辨率 map）

# 2. 创建目标高分辨率网格
high_res_x = np.array(urbclim_coor[['x']])  # x 方向扩展到 50 个点
high_res_y = np.array(urbclim_coor[['y']])  # y 方向扩展到 50 个点
high_res_mesh = np.meshgrid(high_res_x, high_res_y, indexing='ij')  # 创建网格

# 3. 初始化 RegularGridInterpolator
interpolator = RegularGridInterpolator((low_res_x, low_res_y), low_res_values, method='linear')

# 4. 将高分辨率网格点展开为坐标数组（输入给插值器）
points = np.array([high_res_mesh[0].ravel(), high_res_mesh[1].ravel()]).T  # 每个点的坐标 (x, y)

# 5. 插值计算
high_res_values = interpolator(points).reshape(50, 50)  # 插值结果重塑为高分辨率 50x50 的 map

# 6. 可视化结果
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.title("Low-Resolution Map")
plt.imshow(low_res_values, extent=[0, 4, 0, 4], origin='lower', cmap='viridis')
plt.colorbar()

plt.subplot(1, 2, 2)
plt.title("High-Resolution Map (Bilinear Interpolation)")
plt.imshow(high_res_values, extent=[0, 4, 0, 4], origin='lower', cmap='viridis')
plt.colorbar()

plt.tight_layout()
plt.show()


def interpolate_era5_bilinear(era5_df, urbclim_cor):
    # 原始网格
    low_res_x = np.array([era5_df['longitude']]).T
    low_res_y = np.array([era5_df['latitude']]).T
    low_res_values = era5_df[['t2m']].values  # 原始数据

    # 2. 创建目标高分辨率网格
    high_res_x = np.array([urbclim_cor['x']]).T # x 方向扩展到 50 个点
    high_res_y = np.array([urbclim_cor['y']]).T # y 方向扩展到 50 个点
    high_res_mesh = np.meshgrid(high_res_x, high_res_y, indexing='ij')  # 创建网格

    # 3. 初始化 RegularGridInterpolator
    interpolator = RegularGridInterpolator((low_res_x, low_res_y), low_res_values, method='linear')

    # 4. 将高分辨率网格点展开为坐标数组（输入给插值器）
    points = np.array([high_res_mesh[0].ravel(), high_res_mesh[1].ravel()]).T  # 每个点的坐标 (x, y)

    # 5. 插值计算
    high_res_values = interpolator(points).reshape(len(high_res_x),len(high_res_y))  # 插值结果重塑为高分辨率 50x50 的 map
    urbclim_cor['t2m'] = high_res_values

interpolate_era5_bilinear(era5_2015_07_df, urbclim_coor)
start_time = '2015-07-01 00:00:00'
selected_data = era5_2015_07_df[(era5_2015_07_df['time'] == start_time)][['t2m']]
