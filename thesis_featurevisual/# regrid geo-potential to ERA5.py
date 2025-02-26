# regrid geo-potential to ERA5 
# convert the geo-potential height to geo-metric height and calculate the temp diff
# bring ERA5 t2m down to the sea level

# 第一步: 把所有城市的ERA5 file放到一起并把 coor 提取出来
# 第二步: 把geo potential的file放到一起 并把相应的geo和相应的era5 coor放到一起
# 第三步: 转换geo
import xesmf as xe
import glob
import os

# 常数：重力加速度 (m/s²)
GRAVITY =  9.81

# Open the dataset
geo_potential_dir = '/vscmnt/brussel_pixiu_data/_data_brussel/vo/000/bvo00029/UrbClim_Emulator/Features/Meteo/ERA_altitude'
ERA5_coor_dir = '/vscmnt/brussel_pixiu_data/_data_brussel/vo/000/bvo00029/UrbClim_Emulator/model_data_yajing/ERA5_per_city_sampled'
output_dir = '/vscmnt/brussel_pixiu_data/_data_brussel/vo/000/bvo00029/UrbClim_Emulator/model_data_yajing/ERA5_per_city_sampled_sea_level'

ERA5_coor_files = sorted(glob.glob(os.path.join(ERA5_coor_dir, "*_sampled_ERA5_2017_12.nc")))
ERA5_sampled_files = sorted(glob.glob(os.path.join(ERA5_coor_dir, "*_sampled_ERA5_*.nc")))
geo_potential_files = sorted(glob.glob(os.path.join(ERA5_coor_dir, "geopot_*_2015_01_v1.0.nc")))

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
    regridder = xe.Regridder(source_ds, target_ds, method="nearest_s2d", reuse_weights=False)

    # 4. Apply the regridder to interpolate the feature
    interpolated_feature = regridder(source_ds[feature_name])

    # 5. Add the interpolated feature to the target dataset
    target_ds[feature_name] = interpolated_feature

    return target_ds

# # Convert `urbclim_coor` to a full Dataset
# urbclim_coor = urbclim_coor.to_dataset()

# store the tem diff for each city
city_values = {}
# Traverse and process accordingly
for era5_file, geopot_file in zip(ERA5_coor_files, geo_potential_files):
    # Read NetCDF file
    era5_ds = xr.open_dataset(era5_file)
    geopot_ds = xr.open_dataset(geopot_file)

    # Get city name
    city_name = os.path.basename(era5_file).split('_')[0] 
    year, month = os.path.basename(era5_file).split('_')[1:3]

    # Run `interpolate()` function
    geopot_regrided = interpolate(geopot_ds, era5_ds, feature_name="z")

    # make sure there is geo potential feature
    if "z" not in geopot_regrided.variables:
        continue

    # calculate the GeoMetric height
    geopot_regrided["geo_metric"] = geopot_regrided["z"] / GRAVITY
    geopot_regrided["geo_metric"].attrs = {
        "units": "m",
        "long_name": "GeoMetric Height"
    }

    tem_diff1 =  geopot_regrided["geo_metric"] / 100 * 0.6
    city_values[city_name] = tem_diff1

    # go through the files and modify the ERA5 to bring it down to the sea level
    for file in ERA5_sampled_files:
        city_name = os.path.basename(file).split('_')[0]  # get the city name
        if city_name not in city_values:
            continue

        tem_diff = city_values[city_name]  

        ds = xr.open_dataset(file)
        ds["t2m"] = ds["t2m"] + tem_diff


        # generate the output file
        output_file = os.path.join(output_dir, f'{city_name}_sampled_ERA5_{year}_{month}_sea_level')

        # save
        ds.to_netcdf(output_file)

