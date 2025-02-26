import matplotlib as plt
import pandas as pd
import xarray as xr
import xesmf as xe
import os
import glob

# Open the dataset
urbclim_directory = '/vscmnt/brussel_pixiu_data/_data_brussel/vo/000/bvo00029/UrbClim_Emulator/Urbclim_data/Urbclim_non_projected'
city_files = sorted(glob.glob(os.path.join(urbclim_directory, "tas_*_2008_01_v1.0.nc")))[:5]

# special case : NDVI
# Attention!!!
# land_Sea_Mask no need for regriding
# rural_urban_mask/urban_OR_rural no need for regriding
geo_folders = ['AHF', 'coast/COAST_reprojected', 'imperv', 'rural_urban_mask/urban_OR_rural', 'CORINE',
               'elevation/DMET', 'land_water_mask/LANDORSEA/land_or_sea', 'surface',
               'LCZ', 'albedo', 'height', 'population', 'volume']
geo_dir_root = '/vscmnt/brussel_pixiu_data/_data_brussel/vo/000/bvo00029/UrbClim_Emulator/Features/Geo/'

output_dir = '/vscmnt/brussel_pixiu_data/_data_brussel/vo/000/bvo00029/UrbClim_Emulator/model_data_yajing/features_regrided'
os.makedirs(output_dir, exist_ok=True)

# section 1
all_features_each_city = {}
for urb_coor in city_files:
    city_name = os.path.basename(urb_coor).split('_')[1]
    all_features_each_city[city_name] = []


# Interpolation utility code
def interpolate(source_ds, target_ds, feature_name):
    """
    Interpolate `feature_name` from the source dataset to the target dataset using xESMF.
    """
    # 1. Rename dimensions and coordinates to match xESMF expectations
    source_ds = source_ds.rename({'x': 'lon', 'y': 'lat'})
    target_ds = target_ds.rename({'x': 'lon', 'y': 'lat'})

    # 2. Flatten latitude and longitude coordinates in the target dataset
    target_ds = target_ds.assign_coords(
        lon=target_ds['longitude'].isel(lat=0),
        lat=target_ds['latitude'].isel(lon=0),
    )

    # 3. Create an xESMF regridder
    regridder = xe.Regridder(source_ds, target_ds, method="bilinear", reuse_weights=False)

    # 4. Apply the regridder to interpolate the feature
    interpolated_feature = regridder(source_ds[feature_name])

    # 5. Add the interpolated feature to the target dataset
    target_ds[feature_name] = interpolated_feature

    return target_ds


# section 2
for geo_feature in geo_folders:
    geo_directory = geo_dir_root + geo_feature
    feature_name = geo_feature.split("/")[-1]
    print(feature_name)
    feature_files = sorted(glob.glob(os.path.join(geo_directory, "*.nc")))

    # Now city_dict contains all files related to each city
    for urb_ds, feature in zip(city_files, feature_files):
        # make sure there is only one timestamp for urbclim coordinates
        city_name = os.path.basename(urb_ds).split('_')[1]
        if feature_name == "land_or_sea" or feature_name == "urban_OR_rural":
            feature = xr.open_dataset(feature)

            all_features_each_city[city_name].append(feature)
            print("direct added")
        else:
            urb_ds = xr.open_dataset(urb_ds)
            urb_ds['time'] = xr.decode_cf(urb_ds)['time']
            urbclim_coor = urb_ds.isel(time=0)  # choose the first timestamp
            urbclim_coor = urb_ds[['y', 'x']].coords
            urbclim_coor = urbclim_coor.to_dataset()

            feature = xr.open_dataset(feature)
            variable_name = list(feature.data_vars.keys())[0]
            feature_new = interpolate(feature, urbclim_coor, variable_name)
            feature_new = feature_new.rename({variable_name: feature_name})

            all_features_each_city[city_name].append(feature_new)
            print("didi")

# Traverse the data of each city
for city_name, new_features in all_features_each_city.items():
    datasets = []  # Stores xarray data corresponding to all features

    for new_feature in new_features:
        # Ensure new_feature is an xarray object
        if isinstance(new_feature, xr.Dataset) or isinstance(new_feature, xr.DataArray):
            feature_var = list(new_feature.data_vars.keys())[0]  # Get first variable name
            ds = xr.Dataset({feature_var: new_feature[feature_var]})
            ds = ds.set_coords(["latitude", "longitude"])

            if "x" in ds.coords and "y" in ds.coords:
                ds = ds.rename({"x": "lon", "y": "lat"})
            ds = ds.drop_vars(["lon", "lat"], errors="ignore")

            if "time" in ds:
                ds = ds.drop_vars("time")
            if "band" not in ds.dims:
                ds = ds.expand_dims(dim="band")

            print("pupu")
            datasets.append(ds)
        else:
            print(f"Warning: Skipping invalid feature for {city_name}")

    try:
        merged_ds = xr.combine_by_coords(datasets)
    except Exception as e:
        print(f"Error merging datasets for {city_name}: {e}")
        continue  # Skip saving if merging fails

    # Save the merged data to a NetCDF file
    output_file = os.path.join(output_dir, f"{city_name}_features_regrid_merged.nc")
    merged_ds.to_netcdf(output_file)




