import os
import xarray as xr
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.preprocessing import StandardScaler

##################################Get features value#################
input = '/Users/wangy/Documents/MACS/Thesis/features'

# Traverse all feature files in the folder
feature_files = [file for file in os.listdir(input) if file.endswith('.nc')]

# Read every feature file and store it in the dictionary
datasets = {}
for feature in feature_files:
    file_path = os.path.join(input, feature)
    ds = xr.open_dataset(file_path)
    datasets[feature] = ds


# Traverse and extract the data of the first lat and first lon of each file
# and store it in the feature list
df = pd.DataFrame(columns=['band', 'y', 'x'])
feature_list = []

for feature, ds in datasets.items():
    variable_name = list(ds.data_vars)[0]

    # Only keep the features having same structure at this moment
    if variable_name == '__xarray_dataarray_variable__':
        data_var = ds[variable_name].to_dataframe().reset_index()

        # Rename the column or the name will all be '__xarray_dataarray_variable__'
        data_var = data_var.rename(columns={'__xarray_dataarray_variable__': feature})
        if 'spatial_ref' in data_var.columns:
            data_var = data_var.drop(columns=['spatial_ref'])
        print(data_var)

        df = pd.merge(df, data_var, on=['band','y', 'x'], how='outer')

# df = df.rename(columns={'y': 'latitude','x':'longitude'})
print(df)

##################################Get ERA5 value#################


era5_input = '/Users/wangy/Documents/MACS/Thesis/ERA5_variables/ERA5_Brussels_t2m_2015_01.nc'


# Open the file
dataset = xr.open_dataset(era5_input)
print(dataset.data_vars)

# Transform into df and t2m to Celsius
era5_data = dataset['t2m'].to_dataframe().reset_index()
era5_data['t2m'] -= 273.15
print(era5_data)

# Extract the data at 2015-01-01 00:00:00
era5_data_frag = era5_data[
    (era5_data['time'] == pd.to_datetime('2015-01-01 00:00:00'))&
    (era5_data['latitude'] == 51.00) &
    (era5_data['longitude'] == 4.00)
]

era5_data_frag = era5_data_frag.drop(columns={'time'})
# 打印结果
print(era5_data_frag)

##################################Merge 2 table#########################

# lat_min, lat_max = 50.9, 51.0
# lon_min, lon_max = 4.0, 4.1
#
#
# features_filter = df[(df['y'] >= lat_min) & (df['y'] <= lat_max) &
#                    (df['x'] >= lon_min) & (df['x'] <= lon_max)]
#
# print(features_filter)


t2m_value = era5_data_frag['t2m'].iloc[0]  # 获取 df1 中的 t2m 值


df['t2m'] = t2m_value
print(df)


df_cleaned = df.dropna()
df_feature_final = df_cleaned.drop(columns=['band','x','y'])
print(df_feature_final)






##################################Normalize features value##############
# Initialize StandardScaler
scaler = StandardScaler()

# Standardize data
df_feature_final = pd.DataFrame(scaler.fit_transform(df_feature_final), columns=df_feature_final.columns)

df_feature_final['x'] = df_cleaned['x']
df_feature_final['y'] = df_cleaned['y']

print(df_feature_final)

##################################Get tas value#########################

Brussels_Urb = '/Users/wangy/Documents/MACS/Thesis/UrbClim_data/tas_Brussels_UrbClim_2015_01_v1.0.nc'

Brussels_tas = xr.open_dataset(Brussels_Urb)
# Calculate the average value of tas in the time dimension
tas = Brussels_tas['tas'].to_dataframe().reset_index()
print(tas)

# tas_frag = tas[
#     (tas['time'] == pd.to_datetime('2015-01-01 00:00:00'))]
# tas_frag= tas_frag.drop(columns=['time','y','x'])
#
# tas_frag['tas'] -= 273.15
# tas_frag = tas_frag.rename(columns={'latitude': 'y', 'longitude':'x'})
#
# print(tas_frag)

################align input and output#################
# df_feature_final = df_feature_final.dropna(subset=['x', 'y'])
#
#
# # 2. 根据 x 和 y 列进行合并
# # how='left' 以确保保留 df1_cleaned 中的所有数据
# merged_df = pd.merge(df_feature_final, tas_frag, on=['x', 'y'], how='left')
#
# # 打印合并后的结果
# print(merged_df)



################linear regression model#################
# from sklearn.linear_model import LinearRegression
#
# linear_model = LinearRegression()
# linear_model.fit(df_scaled, df_y)
#
# # Predict y
# y_pred = linear_model.predict(df_scaled)
# print(y_pred)


# plt.figure(figsize=(8, 6))
# plt.scatter(df_y, y_pred)
# plt.xlabel("True Values")
# plt.ylabel("Predicted Values")
# plt.title("True Values vs Predictions")
# plt.show()
