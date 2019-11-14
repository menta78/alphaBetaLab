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

  z = ds.variables['elevation'][:]

  if not llcrnr is None:
    cndLon = np.logical_and(lon >= llcrnr[0], lon <= urcrnr[0])
    cndLat = np.logical_and(lat >= llcrnr[1], lat <= urcrnr[1]) 
    lon = lon[cndLon]
    lat = lat[cndLat]
    z = z[np.ix_(cndLat, cndLon)]

  return lon, lat, z 


