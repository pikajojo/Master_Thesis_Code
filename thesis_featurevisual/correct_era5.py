import xarray as xr
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import griddata



# 打开NetCDF文件
ds = xr.open_dataset('/Users/wangy/Documents/MACS/Thesis/ERA5_variables/ERA5_2015_07.nc')
urbclim_cor = pd.read_csv('/Users/wangy/Documents/MACS/Thesis/UrbClim_data/Brussels/urbclim_coordinates.csv',index_col=0)

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

# -----------------------------------------------#
# interpolate the ERA5
# 假设第一个df是df1，第二个df是df2
# 加载您的数据
# df1 和 df2 可以替换为您已经加载的 DataFrame

# 第一个 DataFrame (低分辨率)
# 示例 df1 = pd.DataFrame({'x': [...], 'y': [...], 'value': [...]})
# 第二个 DataFrame (高分辨率)
# 示例 df2 = pd.DataFrame({'x': [...], 'y': [...], 'value': [...]})

# 获取 df2 中的目标坐标

def interpolate_era5(era5_df, urbclim_cor):
    points = np.array([era5_df['longitude'], era5_df['latitude']]).T
    values = era5_df.drop(columns=['time', 'latitude', 'longitude']).values  # 取所有需要插值的列，去掉时间和坐标列
    target_points = np.array([urbclim_cor['x'], urbclim_cor['y']]).T

    # 对每一列插值
    interpolated_data = []
    for i in range(values.shape[1]):
        interpolated_column = griddata(points, values[:, i], target_points, method='cubic')
        interpolated_data.append(interpolated_column)

    # 将插值后的数据添加到df2中
    for i, col_name in enumerate(era5_df.columns[3:]):  # 跳过 'time', 'latitude', 'longitude'
        urbclim_cor[col_name] = interpolated_data[i]

    # 查看插值后的结果
    # print(urbclim_cor)


# 定义一个函数用于按时间分组运行插值
def interpolate_by_time(era5_df, urbclim_cor):
    results = []

    # 按时间分组并对每个组应用插值函数
    for time, group_df in era5_df.groupby('time'):
        print(f"Processing time group: {time}")

        # 对该时间组进行插值
        interpolated_urbclim = urbclim_cor.copy()  # 复制 urbclim_cor 防止覆盖原数据
        interpolate_era5(group_df, interpolated_urbclim)

        # 添加时间列以便区分不同时间组的结果
        interpolated_urbclim['time'] = time

        # 将结果存入列表
        results.append(interpolated_urbclim)

    # 合并所有时间组的结果
    final_result = pd.concat(results, ignore_index=True)
    return final_result

# 调用函数
interpolated_era5_df = interpolate_by_time(era5_2015_07_df, urbclim_cor)

# 查看结果
print(interpolated_era5_df)
print(interpolated_era5_df.isna().sum())
# interpolated_era5_df.to_csv('/Users/wangy/Documents/MACS/Thesis/ERA5_variables/ERA5_2015_07_Brussels_Interpolated_final.csv', index=False)

# -----------------------------------------------#
tem_diff_df = pd.read_csv('/Users/wangy/Documents/MACS/Thesis/ERA5_variables/Brussels/ERA5_Corrected/Brussels_ERA5_tem_diff.csv')
print(tem_diff_df)
print(tem_diff_df.isna().sum())

# # compute the group number
# ghent 63001
# Charleroi 40401
num_groups = len(interpolated_era5_df) // 90601

# copy t2m to a new column
interpolated_era5_df['t2m_corrected'] = interpolated_era5_df['t2m'].copy()
tem_diff_value = tem_diff_df.loc[:, 'tem_diff'].values

# 遍历每一组，并减去对应的 tem_diff 值
for i in range(num_groups):
    # 获取当前组的起始和结束索引
    start_idx = i * 90601
    end_idx = (i + 1) * 90601
    # 对当前组进行减法操作
    interpolated_era5_df.loc[start_idx:end_idx-1, 't2m_corrected'] = interpolated_era5_df.loc[start_idx:end_idx-1, 't2m'] - tem_diff_value
#
#
interpolated_era5_df['t2m_corrected'] -= 273.15
# check the result
print(interpolated_era5_df.head())
print(interpolated_era5_df.tail())
#
# check the NaN number
print(interpolated_era5_df.isna().sum())
#
# # #interpolated_era5_df.to_csv('/Users/wangy/Documents/MACS/Thesis/ERA5_variables/ERA5_2015_07_Brussels_Interpolated_Corrected.csv', index=False)
start_time = '2015-07-01 00:00:00'
end_time = '2015-7-10 23:00:00'
selected_data = interpolated_era5_df[(interpolated_era5_df['time'] == start_time)]
# selected_data = interpolated_era5_df[(interpolated_era5_df['time'] >= start_time) & (interpolated_era5_df['time'] <= end_time)]
# # # # selected_data = filtered_data [(filtered_data ['time'] >= start_time) & (filtered_data['time'] <= end_time)]
# # selected_data =selected_data.reset_index(drop=True)
# #
# #
print(selected_data)
# # interpolated_era5_df.to_csv('/Users/wangy/Documents/MACS/Thesis/ERA5_variables/ERA5_Corrected/ERA5_2015_07_Brussels_t2m_Corrected.csv')
# selected_data.to_csv('/Users/wangy/Documents/MACS/Thesis/ERA5_variables/ERA5_2015_07_01to10_Charleroi_Corrected.csv')








def plot_feature(data,feature):
  # Plot the data
  plt.figure(figsize=(10, 8))
  plt.scatter(data['x'], data['y'], c=data[feature], cmap='viridis',
              marker='o', alpha=0.7)
  plt.colorbar(label=feature)
  plt.xlabel('Longitude (x)')

  plt.ylabel('Latitude (y)')
  plt.legend()
  plt.title(f'Brussels {feature} map after correction')
  plt.show()

plot_feature(selected_data, 't2m')