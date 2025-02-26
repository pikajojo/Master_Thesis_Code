# This file is to regird elevation & ERA5(at sea level) to urbclim coordinates
# Calculate the tem-diff2 between sea level and elevation and bring the ERA5 up to the elevation level
# Open the dataset
elevation_dir = '/vscmnt/brussel_pixiu_data/_data_brussel/vo/000/bvo00029/UrbClim_Emulator/Features/Geo/elevation/mood'
ERA5_sea_level_dir = '/vscmnt/brussel_pixiu_data/_data_brussel/vo/000/bvo00029/UrbClim_Emulator/model_data_yajing/ERA5_per_city_sampled_sea_level'
urb_coor_dir = '/vscmnt/brussel_pixiu_data/_data_brussel/vo/000/bvo00029/UrbClim_Emulator/Urbclim_data/Urbclim_non_projected'

output_dir1 = '/vscmnt/brussel_pixiu_data/_data_brussel/vo/000/bvo00029/UrbClim_Emulator/model_data_yajing/ERA5_per_city_sampled_elevation'
output_dir2 = '/vscmnt/brussel_pixiu_data/_data_brussel/vo/000/bvo00029/UrbClim_Emulator/model_data_yajing/elevation_regrided'
os.makedirs(output_dir1, exist_ok=True)
os.makedirs(output_dir2, exist_ok=True)
ERA5_sea_level_files = sorted(glob.glob(os.path.join(ERA5_sea_level_dir, "*_sampled_ERA5_*_sea_level.nc")))[:20]
urb_coor_files = sorted(glob.glob(os.path.join(urb_coor_dir, "tas_*_2008_01_v1.0.nc")))[:5]
elevation_files = sorted(glob.glob(os.path.join(elevation_dir, "elevation_*_2015_01_v1.0.nc")))[:5]

# ERA5_sea_level_files = [ERA5_sea_level_dir + '/Alicante_sampled_ERA5_2008_01_sea_level.nc',
#                         ERA5_sea_level_dir + '/Alicante_sampled_ERA5_2008_02_sea_level.nc',
#                         ERA5_sea_level_dir + '/Amsterdam_sampled_ERA5_2008_01_sea_level.nc',
#                         ERA5_sea_level_dir + '/Amsterdam_sampled_ERA5_2008_02_sea_level.nc']
# urb_coor_files = [urb_coor_dir + '/tas_Alicante_UrbClim_2015_01_v1.0.nc', urb_coor_dir + '/tas_Amsterdam_UrbClim_2015_01_v1.0.nc']
# elevation_files = [elevation_dir + '/elevation_Alicante_UrbClim_2015_01_v1.0.nc', elevation_dir + '/elevation_Amsterdam_UrbClim_2015_01_v1.0.nc']

def interpolate(source_ds, target_ds, file_type, feature_name):
    """
    Interpolate `feature_name` from the source dataset to the target dataset using xESMF.
    """
    # 1. Rename dimensions and coordinates to match xESMF expectations
    if file_type == 'elevation':
        source_ds = source_ds.rename({'x': 'lon', 'y': 'lat'})
    if file_type == 'era':
        source_ds = source_ds.rename({'longitude': 'lon', 'latitude': 'lat'})
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

# # Convert `urbclim_coor` to a full Dataset
# urbclim_coor = urbclim_coor.to_dataset()


# store the tem diff for each city
city_values = {}
# Traverse three file lists
for elev_file, urb_file in zip(elevation_files, urb_coor_files):
    # Open NetCDF file
    elev_ds = xr.open_dataset(elev_file)
    urb_ds = xr.open_dataset(urb_file)

    # Get city name to make sure the sequence are the same
    # city_name1 = os.path.basename(era_file).split('_')[0] 
    city_name2 = os.path.basename(elev_file).split('_')[1]
    city_name3 = os.path.basename(urb_file).split('_')[1]

    # print(city_name1)
    print(city_name2)
    print(city_name3)

    filename = os.path.basename(era_file)

    
    # rename variable
    elev_ds = elev_ds.rename({"__xarray_dataarray_variable__": "elevation"})

    # Run `interpolate()` function
    elev_regrided = interpolate(elev_ds, urb_ds,'elevation', feature_name="elevation")

    # make sure there is geo potential feature
    if "elevation" not in elev_regrided.variables:
        print("pupu")
        continue

    output_elevation = os.path.join(output_dir2, f'{city_name1}_elevation_rergrided.nc')
    # save
    elev_regrided.to_netcdf(output_elevation)

    # calculate the tem diff2
    tem_diff2 = elev_regrided["elevation"] / 100 * 0.6
    city_values[city_name2] = tem_diff2



for era_file in ERA5_sea_level_files:
    era_ds = xr.open_dataset(era_file)
    city_name = os.path.basename(era_file).split('_')[0]
    print(city_name)
    year, month = os.path.basename(era_file).split('_')[3:5]

    #only regrid the t2m
    era_regrided = interpolate(era_ds, urb_ds,'era',feature_name="t2m")
    # make sure there is geo potential feature
    if "t2m" not in era_regrided.variables:
        print("bubu")
        continue

    # regrid every variable
    # era_regrided_all = urb_ds
    # for var_name in era_ds.data_vars:
    #     print(f"Interpolating variable: {var_name}")
    #     era_regrided_all = interpolate(era_ds, era_regrided_all, var_name)

    tem_diff = city_values[city_name]
    # Make sure the dimensions of tem_diff2 are consistent with era_regrided["t2m"]
    tem_diff = tem_diff.broadcast_like(era_regrided["t2m"])
    # Perform overall subtraction
    era_regrided["t2m"] = era_regrided["t2m"] - tem_diff

    # generate the output file
    output_era = os.path.join(output_dir1, f'{city_name1}_sampled_ERA5_{year}_{month}_elev_level.nc')


    # save
    # era_regrided.to_netcdf(output_era)