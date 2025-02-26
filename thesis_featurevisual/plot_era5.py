import matplotlib.pyplot as plt
import xarray as xr



input = '/Users/wangy/Documents/MACS/Thesis/landseamask_Alicante_UrbClim_v1.0.nc'
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


    # Plot the time-averaged variables
    data_plot = plt.pcolormesh(mean_data.longitude, mean_data.latitude, mean_data.squeeze(), cmap="viridis", shading="auto")
    plt.colorbar()
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title(f"Alicante average {variable}")
    plt.show()

    #Save the file to the specified path, or create it if it does not exist
    # if not os.path.exists(output):
    #     os.makedirs(output)
    # file_path = os.path.join(output, f'ERA5_Brussels_{variable}.png')
    # plt.savefig(file_path)




