import os
import numpy as np
from matplotlib import pyplot as plt
#import cartopy.crs as ccrs
#import cartopy.feature as cfeature

import netCDF4

from alphaBetaLab import abTriangularMesh as trmsh


def plotMapAtTime(ncfilepath, timeIndex):
  ds = netCDF4.Dataset(ncfilepath)
  hs = ds.variables['WWM_1'][timeIndex, :]
 #hs = ds.variables['elev'][timeIndex, :]
 #hs = ds.variables['vwnd'][timeIndex, :]
 #xs = ds.variables['SCHISM_hgrid_node_x'][:]
 #ys = ds.variables['SCHISM_hgrid_node_y'][:]
  msh = trmsh.loadFromGr3File('hgrid.gr3')
  ndid = list(msh.nodes.keys())
  ndid.sort()
  xs = np.array([msh.nodes[k][0] for k in ndid])
  ys = np.array([msh.nodes[k][1] for k in ndid])



  tm = ds.variables['time']
 #dtm = netCDF4.num2date(tm[timeIndex], tm.units, 'standard')
 #print('printing for date ' + str(dtm))
  
  f = plt.figure(figsize=[12, 6])
 #ax = plt.axes(projection=ccrs.PlateCarree())
  ax = plt.axes()
 #ax.coastlines(resolution='10m')

 #mx = np.percentile(hs.flatten(), 99.99) + .6
 #hs[hs > mx - .1] = mx - .1
  hs[hs > 100] = np.nan
  mx = np.nanmax(hs)
  mx = .22
  cnd =  ~np.isnan(hs)
  levels = np.arange(0., mx, .005)
 #levels = np.arange(0., 10, .02)
  cmap = 'ocean_r'
  cmap = 'jet'
 #xs[xs < 0] = xs[xs < 0] + 360
  cf = plt.tricontourf(xs[cnd], ys[cnd], hs[cnd], levels, cmap=cmap)
  cf.cmap.set_over([.5,0,0])
  plt.triplot(xs, ys, linewidth=.1, color='k')
 #lnd = cfeature.NaturalEarthFeature('physical', 'land', '10m', facecolor='lightgray')
 #lndmsk = ax.add_feature(lnd)
 #lndmsk.set_zorder(1)

 #cf.set_clim(0, 1.6)
  cb = plt.colorbar()
  cb.ax.set_ylabel('Hs (m)', fontsize=15)
  f.tight_layout()
  plt.savefig('hs_t=' + str(timeIndex) + '.png', dpi=400)
  plt.show()


if __name__ == '__main__':
  ncfilepath = 'outputs/schout_0000_1.nc'
  timeIndex = 719
  import pdb; pdb.set_trace()
  plotMapAtTime(ncfilepath, timeIndex)

