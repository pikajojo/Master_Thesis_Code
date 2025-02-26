import xarray as xr
from scipy.interpolate import griddata
import numpy as np
import pandas as pd
import xesmf as xe
import os

# Open the dataset
cities_dir = '/vscmnt/brussel_pixiu_data/_data_brussel/vo/000/bvo00029/UrbClim_Emulator/Urbclim_data/UrbClim_reference'
items_urb = os.listdir(directory)

output_dir = '/vscmnt/brussel_pixiu_data/_data_brussel/vo/000/bvo00029/UrbClim_Emulator/model_data_yajing/ERA_per_city'


# Obtain ERA5 for each city
era5_dir = '/vscmnt/brussel_pixiu_data/_data_brussel/vo/000/bvo00029/UrbClim_Emulator/Features/Meteo/ERA'
items_era = os.listdir(era5_directory)


# city_files = [os.path.join(directory, f) for f in items_urb if os.path.isfile(os.path.join(directory, f))]
city_files = sorted(glob.glob(os.path.join(cities_dir, "tas_*.nc")))

for file in city_files:
    urbclim_cor = xr.open_dataset(file)   
    print(urbclim_cor)
    # Extract and print the coordinates
    urbclim_coor = urbclim_cor[['y', 'x']].coords

    # Extract the city name
    city_name = os.path.basename(file).split('_')[1]
    print(urbclim_coor)
 
    # Select the latitude and longitude range
    lat_min = urbclim_coor['y'].min() - 1
    lat_max = urbclim_coor['y'].max() + 1
    lon_min = urbclim_coor['x'].min() - 1 
    lon_max = urbclim_coor['x'].max() + 1

    # era5_files =  [os.path.join(era5_directory, f) for f in items_era if os.path.isfile(os.path.join(era5_directory, f))]
    era5_files = sorted(glob.glob(os.path.join(era5_dir, "ERA5_*.nc")))
    for file_era in era5_files:
        # if not file_era.endswith(".nc"):
        #     continue
        era5 = xr.open_dataset(file_era, engine="netcdf4")   
        era_filename = os.path.basename(file_era)
        year, month = era_filename.split('_')[1:3]
        print(era5)


        # Cut off the range data from the whole map
        subset = era5.sel(longitude=slice(lon_min, lon_max))
        lat_indices = ((subset['latitude'] >= lat_min) & (subset['latitude'] <= lat_max))

        # Use the latitude indices to subset the dataset
        subset = subset.isel(latitude=lat_indices)

        # Randomly select 24 different time points

        all_times = subset["time"].values
        if len(all_times) < 24:
            selected_times = all_times # If there are less than 24 data points, use all
        else:
            selected_times = np.random.choice(all_times, 24, replace=False) # Randomly select 24 hour points

        subset = subset.sel(time=selected_times)




        # Define the output filename
        output_filename = os.path.join(output_dir, f'{city_name}_ERA5_{year}_{month}')

        # Save the downsampled dataset
        subset.to_netcdf(output_filename)