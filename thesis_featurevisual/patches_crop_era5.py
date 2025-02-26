# This file is going to crop same size patches for different ERA5 files, different size cities have propotional amount of patches
# larger cities have more patches. 
import xarray as xr
import numpy as np
import pandas as pd
import random

def extract_patches_to_csv(nc_file, output_csv="extracted_patches.csv", var_name='t2m', 
                           patch_size=40, min_patches=1, scale_factor=0.01):
    """
    Extracts 40x40 patches from an NC file and saves the results as a CSV file.
    
    Each row represents a temperature value at a specific time and geographic location.

    Parameters:
    - nc_file: str, path to the NetCDF file
    - output_csv: str, name of the output CSV file
    - var_name: str, name of the variable to extract from the NetCDF file (default: "t2m")
    - patch_size: int, size of each patch (default: 40x40)
    - min_patches: int, minimum number of patches per city
    - scale_factor: float, scaling factor to determine the number of patches based on data point density
    """
    
    # Load NetCDF data
    ds = xr.open_dataset(nc_file)
    
    # Extract the target variable
    data = ds[var_name]  # Typically has the shape (time, lat, lon)
    times = data.time.values
    latitudes = data.lat.values
    longitudes = data.lon.values
    
    records = []  # Stores extracted data

    for t in times:
        city_data = data.sel(time=t)
        lat_size, lon_size = city_data.shape  # Get the grid size at the current timestamp

        # Determine the number of patches based on data density
        num_data_points = lat_size * lon_size
        num_patches = max(min_patches, int(num_data_points * scale_factor))

        # Generate patches
        for _ in range(num_patches):
            # Randomly select a starting point, ensuring the patch remains within bounds
            lat_start = random.randint(0, max(0, lat_size - patch_size))
            lon_start = random.randint(0, max(0, lon_size - patch_size))

            # Extract a 40x40 patch
            patch = city_data.isel(lat=slice(lat_start, lat_start + patch_size),
                                   lon=slice(lon_start, lon_start + patch_size))

            # Iterate over the patch and store values in CSV format
            for i in range(patch_size):
                for j in range(patch_size):
                    lat_value = latitudes[lat_start + i]
                    lon_value = longitudes[lon_start + j]
                    temp_value = patch.values[i, j]
                    
                    records.append([t, lat_value, lon_value, temp_value])

    ds.close()

    # Convert to DataFrame and save as CSV
    df = pd.DataFrame(records, columns=["time", "latitude", "longitude", "t2m"])
    df.to_csv(output_csv, index=False)

    print(f"CSV file saved: {output_csv}")

# Example usage
nc_file_path = "your_file.nc"
extract_patches_to_csv(nc_file_path, output_csv="extracted_patches.csv")
