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
feature_list = []
for feature, ds in datasets.items():
    variable_name = list(ds.data_vars)[0]
    first_value = ds[variable_name].isel(x=0, y=0).values.item()  # Extract the upper left corner value
    feature_list.append([feature, first_value])

df_feature = {item[0]: [item[1]] for item in feature_list}
df_feature = pd.DataFrame(df_feature)

# drop NaN value
df_feature = df_feature.dropna(axis=1)

# Add ERA5 value
df_feature.insert(df_feature.shape[1], 'era5', 3.92624843)

print(df_feature)

##################################Get features value####################


##################################Normalize features value##############
# Initialize StandardScaler
scaler = StandardScaler()

# Standardize data
df_scaled = pd.DataFrame(scaler.fit_transform(df_feature), columns=df_feature.columns)
##################################Normalize features value##############


##################################Get tas value#########################

Brussels_Urb = '/Users/wangy/Documents/MACS/Thesis/tas_Brussels_UrbClim_2015_01_v1.0.nc'

Brussels_tas = xr.open_dataset(Brussels_Urb)
# Calculate the average value of tas in the time dimension
tas_mean_time = Brussels_tas['tas'].mean(dim='time')
tas_mean_time -= 273.15
print(tas_mean_time)

# print(Brussels_tas)

value = tas_mean_time.isel(x=0, y=0).values.item()  # Extract the upper left corner value

y = [{'Brussels_tas': value}]
df_y = pd.DataFrame(y)

print(df_y)

################linear regression model#################
from sklearn.linear_model import LinearRegression

linear_model = LinearRegression()
linear_model.fit(df_scaled, df_y)

# Predict y
y_pred = linear_model.predict(df_scaled)
print(y_pred)


# plt.figure(figsize=(8, 6))
# plt.scatter(df_y, y_pred)
# plt.xlabel("True Values")
# plt.ylabel("Predicted Values")
# plt.title("True Values vs Predictions")
# plt.show()
