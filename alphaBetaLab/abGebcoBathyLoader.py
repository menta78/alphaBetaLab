import numpy as np
import netCDF4

from .abUtils import abException

def loadBathy(gbcFilePath, llcrnr = None, urcrnr = None):
  """
  loadBathy: z is negative in sea and positive on land.
  llcrnr and urcrnr are the low left/up right corner, as a tuple (lon, lat). If they are None the global dataset is returned
  """
  ds = netCDF4.Dataset(gbcFilePath)
  if 'lon' in ds.variables:
    lon = ds.variables['lon'][:]
  elif 'x' in ds.variables:
    lon = ds.variables['x'][:]
  else:
    raise abException('abGebcoBathyLoader: lon coordinate not found in file')

  if 'lat' in ds.variables:
    lat = ds.variables['lat'][:]
  elif 'y' in ds.variables:
    lat = ds.variables['y'][:]
  else:
    raise abException('abGebcoBathyLoader: lat coordinate not found in file')

  if not llcrnr is None:
    lon_ = np.array(lon)
    urcrnr_ = np.array(urcrnr)
    if llcrnr[0] > urcrnr_[0]: # the rectange starts W of 180degE and finishes E of 180degE
      lon_[lon_ < 0] = lon_[lon_ < 0] + 360
      urcrnr_[0] = urcrnr_[0] + 360
    cndLon = np.logical_and(lon_ >= llcrnr[0], lon_ <= urcrnr_[0])
    cndLat = np.logical_and(lat >= llcrnr[1], lat <= urcrnr_[1]) 
    lon = lon[cndLon]
    lat = lat[cndLat]
    z = ds.variables['elevation'][cndLat, cndLon]
  else:
    z = ds.variables['elevation'][:]

  return lon, lat, z 


