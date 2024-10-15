import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors




# Read and open NetCDF file
nc_file = '/Users/wangy/Documents/MACS/Thesis/variables/height_Brussels.nc'
dataset = xr.open_dataset(nc_file)

# Check the structure
print(dataset)

# Get the names of all Data variables and select the first one
variable_name = list(dataset.data_vars)[0]

# Read the data
data = dataset[variable_name]

# Plot the data
plt.figure(figsize=(10, 6))

# Set the color map
cmap = plt.get_cmap('viridis')

# For data only has 0 and 1, set the boundary
# norm = mcolors.BoundaryNorm(boundaries=[0, 1, 2], ncolors=cmap.N)
data_plot = data.plot(cmap='viridis')



# Set the title and axis labels
plt.title("LCZcorine Brussels Visualization")
plt.xlabel("Longitude")
plt.ylabel("Latitude")

# Modify labels
cbar = data_plot.colorbar
cbar.set_label('Measurement Unit')

# For data only has 0 and 1, set the scale to 0 and 1
# cbar.set_ticks([0, 1])
# cbar.set_ticklabels(['0', '1'])
plt.show()
