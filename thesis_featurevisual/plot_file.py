import xarray as xr
import matplotlib.pyplot as plt




# read and open NetCDF file
nc_file = '/Users/wangy/Documents/MACS/Thesis/variables/LCZcorine_Brussels_UrbClim_2015_01_v1.0.nc'  # 替换为你的文件路径
dataset = xr.open_dataset(nc_file)

# check the structure
print(dataset)

# Get the names of all Data variables and select the first one
variable_name = list(dataset.data_vars)[0]

# Read the data
data = dataset[variable_name]

# Plot the data
plt.figure(figsize=(10, 6))
data_plot = data.plot(cmap='viridis')

# Setting the title and axis labels
plt.title("LCZcorine Brussels Visualization")
plt.xlabel("Longitude")  # 自定义X轴名称
plt.ylabel("Latitude")   # 自定义Y轴名称

# Modify labels
data_plot.colorbar.set_label('Measurement Unit')  # Replace with actual units
plt.show()
