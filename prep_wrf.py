from netCDF4 import Dataset
import datetime as dt
import numpy as np
from sys import argv

filename = argv[1]
print('procesando:', filename)

with  Dataset(filename, 'r', format='NETCDF4_CLASSIC') as ds:
    data_u = ds['U10'][:]
    data_v = ds['V10'][:]
    data_lat = ds['XLAT'][0,:,0]
    data_lon = ds['XLONG'][0,0,:]
    secs = ds['Time'][:]

time = []
for s in secs:
    time.append(dt.datetime.fromtimestamp(s, dt.timezone.utc))
t_units = time[0].strftime("hours since %Y-%m-%d %H:%M:%S UTC")
print(t_units)
hours = []
for t in time:
    hours.append((t-time[0]).total_seconds()/3600)
hours = np.array(hours)
print(hours)

#filename = 'WRF_forecast_.nc'
fillValue = 1.267651e+30

print(hours.shape)
print(data_lat.shape)
with Dataset(filename, 'w', format='NETCDF3_CLASSIC') as dataset:
    dataset.createDimension('time', hours.shape[0])
    dataset.createDimension('lat', data_lat.shape[0])
    dataset.createDimension('lon', data_lon.shape[0])
    time = dataset.createVariable('time', np.float64, ('time', ))
    lon = dataset.createVariable('lon', np.float32, ('lon', ))
    lat = dataset.createVariable('lat', np.float32, ('lat', ))
    u = dataset.createVariable('u', (np.float32), ('time', 'lat', 'lon'), fill_value=fillValue)
    v = dataset.createVariable('v', (np.float32), ('time', 'lat', 'lon'), fill_value=fillValue)
    dataset.grid_type = 'REGULAR'
    lat.long_name = 'Latitude'
    lat.units = 'degrees_north'
    lat.standard_name = 'latitude'
    lon.long_name = 'Longitude'
    lon.units = 'degrees_east'
    lon.standard_name = 'longitude'
    time.long_name = 'Time'
    time.units = t_units
    time.standard_name = 'time'
    u.long_name = 'Eastward Air Velocity'
    u.standard_name = 'eastward_wind'
    u.units = 'm/s'
    v.long_name = 'Northward Air Velocity'
    v.standard_name = 'northward_wind'
    v.units = 'm/s'
    lat[:] = data_lat
    lon[:] = data_lon
    time[:] = hours
    u[:] = data_u
    v[:] = data_v

