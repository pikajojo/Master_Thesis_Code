import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import numpy as np

######pre process the data########
features_cor = '/Users/wangy/Documents/MACS/Thesis/UrbClim_data/reference/tas_Brussels_UrbClim_reference.nc'
features_cor_tas = xr.open_dataset(features_cor)

features_cor_tas = features_cor_tas['tas']
# Select only one timestamp
features_cor_tas = features_cor_tas.sel(time="2015-01-01T00:00:00")

features_cor_tas = features_cor_tas.to_dataframe().reset_index()
features_cor_tas['time'] = pd.to_datetime(features_cor_tas['time'])
print(features_cor_tas)

urbclim_cor = xr.open_dataset('/Users/wangy/Documents/MACS/Thesis/UrbClim_data/tas_Brussels_UrbClim_2015_07_v1.0.nc')
urbclim_cor = urbclim_cor.sel(time="2015-07-01T00:00:00")

urbclim_cor['x'] = urbclim_cor['x'].astype('float64')
urbclim_cor['y'] = urbclim_cor['y'].astype('float64')

urbclim_cor_tas = urbclim_cor['tas'].to_dataframe().reset_index()
urbclim_cor_tas = urbclim_cor_tas.drop(columns=['y', 'x'])
urbclim_cor_tas = urbclim_cor_tas.rename(columns={'latitude': 'y', 'longitude': 'x'})
urbclim_cor_tas['time'] = pd.to_datetime(urbclim_cor_tas['time'])

print(urbclim_cor_tas)


###### Plot the target and source map ######
plt.figure(figsize=(10, 8))
# plot the source coordinates
plt.scatter(features_cor_tas['x'], features_cor_tas['y'], color='red', label='Source Urb', alpha=0.9)
# plot the target coordinates
plt.scatter(urbclim_cor_tas['x'], urbclim_cor_tas['y'], color='blue', label='Target Urb', alpha=0.9)



# Title and labels
plt.title('Coordinate Points from Two Tables')
plt.xlabel('Longitude (x)')
plt.ylabel('Latitude (y)')

plt.legend()
plt.show()

###### Regrid the urbclim ######
def interpolate(source, target):
    # 1. Extract x, y and tas values from source data
    source_points = source[['x', 'y']].values
    source_values = source['tas'].values

    # 2. Extract x and y values from the target data (i.e. interpolated target coordinates)
    target_points = target[['x', 'y']].values

    # 3. using griddata to interpolate
    interpolated_values = griddata(
        source_points,  # 源坐标
        source_values,  # 源值（tas）
        target_points,  # 目标坐标
        method='nearest'  # 使用线性插值方法
    )
    # 4. add the interpolated_values to target
    target['tas'] = interpolated_values


interpolate(features_cor_tas, urbclim_cor_tas)
# Change the 'time' to July
# target_tas['time'] = target_tas['time'].apply(lambda dt: dt.replace(month=7))

# # Plot
# plt.figure(figsize=(10, 8))
# plt.scatter(target_tas['x'], target_tas['y'], c=target_tas['tas'], cmap='viridis', label='Interpolated on Target Grid',
#             marker='o', alpha=0.7)
# plt.colorbar(label='tas (Interpolated)')
# plt.xlabel('Longitude (x)')
# plt.ylabel('Latitude (y)')
# plt.legend()
# plt.title('Interpolated Data on Target (Blue) Grid')
# plt.show()
#
# print(target_tas)
