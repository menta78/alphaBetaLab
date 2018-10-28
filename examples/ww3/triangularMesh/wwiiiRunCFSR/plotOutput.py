from mpl_toolkits import basemap
import netCDF4
from matplotlib import pyplot as plt
import numpy as np


def plotMapAtTime(ncfilepath, timeIndex):
  ds = netCDF4.Dataset(ncfilepath)
  hs = ds.variables['hs'][timeIndex, :]
 #hs = ds.variables['vwnd'][timeIndex, :]
  xs = ds.variables['longitude'][:]
  ys = ds.variables['latitude'][:]
  hs[hs.mask] = 0

  tm = ds.variables['time']
  dtm = netCDF4.num2date(tm[timeIndex], tm.units, 'standard')
  print('printing for date ' + str(dtm))
  
  f = plt.figure(figsize=[12, 6])

  bm = basemap.Basemap(llcrnrlon=min(xs), llcrnrlat=min(ys), urcrnrlon=max(xs), urcrnrlat=max(ys), resolution='i')
  bm.drawcoastlines()
  mx = np.percentile(hs.flatten(), 99.5) + .6
  hs[hs > mx - .1] = mx - .1
  levels = np.arange(0., mx, .02)
  cmap = 'ocean_r'
  cf = bm.contourf(xs, ys, hs, levels, tri=True, cmap=cmap)
  cf.cmap.set_over([.5,0,0])
  plt.triplot(xs, ys, linewidth=.1, color='k')
  fc = bm.fillcontinents(color=[.8, .8, .8],lake_color=[.8, .8, .8])
  [fci.set_zorder(20) for fci in fc]
 #cf.set_clim(0, 1.6)
  cb = bm.colorbar()
  cb.ax.set_ylabel('Hs (m)', fontsize=15)
  f.tight_layout()
  plt.savefig('pltTriMed_t=' + str(timeIndex) + '.png', dpi=400)
  plt.show()


if __name__ == '__main__':
  ncfilepath = 'tmp/ww3.200001.nc'
 #ncfilepath = 'outNonUOST/ww3.200001.nc'
 #timeIndex = 299 #+
  timeIndex = 349 #++
 #timeIndex = 324 #--
 #timeIndex = 374 #-
 #timeIndex = 274 #-
 #timeIndex = 374 #-
 #timeIndex = 399 #-
 #timeIndex = 354 #++
 #timeIndex = 344 #++
 #import pdb; pdb.set_trace()
  plotMapAtTime(ncfilepath, timeIndex)

