import matplotlib.pyplot as plt
import xarray as xr



input = '/Users/wangy/Documents/MACS/Thesis/ERA5_variables/ERA5_Brussels_t2m_2015_01.nc'
output = '/Users/wangy/Documents/MACS/Thesis/ERA5_variables'




# Open the file
dataset = xr.open_dataset(input)
print(dataset.data_vars)


for variable in dataset.data_vars:

    # For t2m, transform it into Celsius
    if variable == 't2m':
        data = dataset[variable] - 273.15
    else:
        data = dataset[variable]

    # Calculate the average value of the time dimension
    mean_data = data.mean(dim='time')

    print(mean_data)

    # Plot the time-averaged variables
    data_plot = mean_data.plot(cmap='viridis')
    data_plot.axes.set_xlabel('Longitude')
    data_plot.axes.set_ylabel('Latitude')

    #Save the file to the specified path, or create it if it does not exist
    # if not os.path.exists(output):
    #     os.makedirs(output)
    # file_path = os.path.join(output, f'ERA5_Brussels_{variable}.png')
    # plt.savefig(file_path)

    # Set titles
    plt.title(f'Average {variable} Brussels')
    plt.show()


