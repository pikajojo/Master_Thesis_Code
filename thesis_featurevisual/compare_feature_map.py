import matplotlib.pyplot as plt
import xarray as xr

###### Plot the target and source map ######
source = xr.open_dataset('/Users/wangy/Documents/MACS/Thesis/features/Coast_Brussels.nc')
target = xr.open_dataset('/Users/wangy/Documents/MACS/Thesis/features/LCZ_Brussels_UrbClim_2015_01_v1.0.nc')

target = target.to_dataframe().reset_index()
source = source.to_dataframe().reset_index()
print(source)
print(target)


plt.figure(figsize=(10, 8))

# plot the target coordinates
plt.scatter(target['x'], target['y'], color='blue', label='Target Urb', alpha=0.9)

# plot the source coordinates
plt.scatter(source['x'], source['y'], color='red', label='Source Urb', alpha=0.9)

# Title and labels
plt.title('Coordinate Points from Two Tables')
plt.xlabel('Longitude (x)')
plt.ylabel('Latitude (y)')

plt.legend()
plt.show()