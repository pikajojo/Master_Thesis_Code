import xarray as xr
from scipy.interpolate import griddata
import os
# import xarray as xr
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression

urbclim_and_feature = pd.read_csv('/Users/wangy/Documents/MACS/Thesis/UrbClim_data/Brussles_urbclim_and_features_2015_07_01to10.csv')
era5 = pd.read_csv('/Users/wangy/Documents/MACS/Thesis/ERA5_variables/ERA5_Corrected/ERA5_2015_07_01to10_Brussels_Corrected.csv')

era5_new = era5.drop(columns=['x','y','time'])
era5_new[['t2m_corrected']] -= 273.15
urbclim_and_feature = urbclim_and_feature.drop(columns=[ 'Unnamed: 0','Unnamed: 0.1','y.1','x.1'])
print(urbclim_and_feature.columns)
all_variables = pd.concat([urbclim_and_feature,era5_new], axis=1)

y_train = pd.DataFrame()
# 计算新的 'tas' 列
y_train['tas'] = all_variables['tas'] - all_variables['t2m_corrected']

X_train = all_variables.drop(columns=['x','y','time','tas'])

print(y_train)
print(X_train)



urbclim_and_feature = pd.read_csv('/Users/wangy/Documents/MACS/Thesis/UrbClim_data/Brussles_urbclim_and_features_2016_07_01to03.csv')
# urbclim_cor_2016 = xr.open_dataset('/content/drive/My Drive/thesis/urbclim/tas_Brussels_UrbClim_2016_07_v1.0.nc')
era5 = pd.read_csv('/Users/wangy/Documents/MACS/Thesis/ERA5_variables/ERA5_Corrected/ERA5_2016_07_01to03_Brussels_Corrected.csv')
urbclim_and_feature = urbclim_and_feature.drop(columns=[ 'Unnamed: 0','Unnamed: 0.1','y.1','x.1'])
print(urbclim_and_feature.columns)

era5_new = era5.drop(columns=['x','y','time'])
# era5_new[['t2m_corrected']] -= 273.15
all_variables = pd.concat([urbclim_and_feature,era5_new], axis=1)

y_test = pd.DataFrame()
# 计算新的 'tas' 列
y_test['tas'] = all_variables['tas'] - all_variables['t2m_corrected']
X_test = all_variables.drop(columns=['x','y','time','tas'])

print(y_test)
print(X_test)





