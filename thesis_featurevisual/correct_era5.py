import xarray as xr
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import griddata


# 打开NetCDF文件
ds = xr.open_dataset('/Users/wangy/Documents/MACS/Thesis/ERA5_variables/ERA5_2015_07.nc')
urbclim_cor = pd.read_csv('/Users/wangy/Documents/MACS/Thesis/UrbClim_data/urbclim_coordinates.csv')
# 提取经纬度范围
lon_min, lon_max = 4.0, 4.5
lat_min, lat_max = 50.5, 51.0

# 选择经纬度范围
lon_range = (ds.variables['longitude'][:] >= lon_min) & (ds.variables['longitude'][:] <= lon_max)
lat_range = (ds.variables['latitude'][:] >= lat_min) & (ds.variables['latitude'][:] <= lat_max)

# 初始化一个空的DataFrame来存放所有变量的数据
# era5_t2m_df = pd.DataFrame()


var_region = ds['t2m'][:, lat_range, lon_range]

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

era5_t2m_df = var_region_da.to_dataframe('t2m').reset_index()
era5_t2m_df['t2m'] = era5_t2m_df['t2m'] - 273.15

# 查看合并后的DataFrame
print(era5_t2m_df)

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
        interpolated_column = griddata(points, values[:, i], target_points, method='nearest')
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
interpolated_era5_df = interpolate_by_time(era5_t2m_df, urbclim_cor)

# 查看结果
print(interpolated_era5_df)

# interpolated_era5_df.to_csv('/Users/wangy/Documents/MACS/Thesis/ERA5_variables/ERA5_2015_07_Brussels_Interpolated_final.csv', index=False)

# # -----------------------------------------------#
tem_diff_df = pd.read_csv('/Users/wangy/Documents/MACS/Thesis/ERA5_variables/ERA5_Corrected/Brussels_ERA5_tem_diff.csv')
#
#
# # for ERA5 data of different month, the way to correct it is the process following:
#
# 计算有多少组
num_groups = len(interpolated_era5_df) // 90601

# 创建一个新的列用于存储减去 tem_diff 后的结果
interpolated_era5_df['t2m_corrected'] = interpolated_era5_df['t2m']  # 复制 t2m 列

# 遍历每一组，并减去对应的 tem_diff 值
for i in range(num_groups):
    # 获取当前组的起始和结束索引
    start_idx = i * 90601
    end_idx = (i + 1) * 90601

    # 获取对应的 tem_diff 值
    tem_diff_value = tem_diff_df.loc[i, 'tem_diff']

    # 对当前组进行减法操作
    interpolated_era5_df.loc[start_idx:end_idx-1, 't2m_corrected'] -= tem_diff_value

# 查看结果
print(interpolated_era5_df.head())
print(interpolated_era5_df.tail())


# interpolated_era5_df.to_csv('/Users/wangy/Documents/MACS/Thesis/ERA5_variables/ERA5_2015_07_Brussels_Interpolated_Corrected.csv', index=False)

selected_data = interpolated_era5_df[interpolated_era5_df['time'] == '2015-07-01 00:00:00']

# 查看结果
print(selected_data)

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