import numpy as np
import matplotlib
import time
from matplotlib.gridspec import GridSpec
from matplotlib import pyplot as plt
from mpl_toolkits import basemap

fname = 'Global.obstr_lev1'
mskFName = 'g_glb150.mask'
lonlims = (-99, -58)
latlims = (7, 32)
landColor = 'palegreen'

obsAll = np.loadtxt(fname)
mskAll = np.loadtxt(mskFName)
nlat = obsAll.shape[0]/2

allObsX = obsAll[:nlat, :]
allObsY = obsAll[nlat:, :]
allObsX[mskAll == 0] = -1
allObsY[mskAll == 0] = -1
allLons = np.arange(-180, 180, 1.5)
allLats = np.arange(-70, 70, 1.5)

cndlon = np.logical_and(allLons >= lonlims[0], allLons <= lonlims[1])
cndlat = np.logical_and(allLats >= latlims[0], allLats <= latlims[1])
cnd = np.ix_(cndlat, cndlon)
lon = allLons[cndlon]
lat = allLats[cndlat]
obsX = allObsX[cnd]
obsY = allObsY[cnd]
msk = mskAll[cnd]

obsXplt = np.ma.masked_where(msk == 0, obsX)
obsYplt = np.ma.masked_where(msk == 0, obsY)


dlon = (lon[1] - lon[0])/2.
pltlon = lon - dlon
#pltlon = lon

dlat = (lat[1] - lat[0])/2.
pltlat = lat - dlat
#pltlat = lat

fct = 2
mp = basemap.Basemap(llcrnrlon = lonlims[0] + dlon*fct, llcrnrlat = latlims[0] + dlat*fct-1, urcrnrlon = lonlims[1] - dlon*fct, urcrnrlat = latlims[1] - dlat*fct+1, resolution = 'i')

#fig, axs = plt.subplots(2, 1, figsize = [7, 14], sharex = True, tight_layout = True)

gs=GridSpec(2, 2, width_ratios = [1, .5/7.5])
fig = plt.figure(figsize = [8.1, 14], tight_layout = True)

def drawMeridianAndParallels():
  meridians = np.arange(-99, -58, 6)
  parallels = np.arange(7, 32, 6)
  mp.drawmeridians(meridians, ax = ax)
  mrdLblLat = 30
  for lon in meridians[1:]:
    x, y = mp(lon, mrdLblLat)
    ax.text(x, y, str(lon), fontsize = 15, ha = 'center')
  prlLblLon = -97
  mp.drawparallels(parallels, ax = ax)
  for lat in parallels[1:]:
    x, y = mp(prlLblLon, lat)
    ax.text(x, y - .2, str(lat), fontsize = 15, va = 'center')



ax = fig.add_subplot(gs[0,0])
mp.drawcoastlines(linewidth = .5, ax = ax)
mp.fillcontinents(color = landColor, ax = ax)
pcl1 = mp.pcolor(pltlon, pltlat, obsXplt, ax = ax, vmin = 0, vmax = 100, cmap = 'Reds')
drawMeridianAndParallels()
ax.text(-63, 27, 'a', fontsize = 40)

ax = fig.add_subplot(gs[1,0])
mp.drawcoastlines(linewidth = .5, ax = ax)
mp.fillcontinents(color = landColor, ax = ax)
pcl2 = mp.pcolor(pltlon, pltlat, obsYplt, ax = ax, vmin = 0, vmax = 100, cmap = 'Reds')
drawMeridianAndParallels()
ax.text(-63, 27, 'b', fontsize = 40)

ax = fig.add_subplot(gs[:,1])
clbr = plt.colorbar(pcl1, cax = ax)
clbr.ax.tick_params(labelsize=15)
clbr.ax.set_ylabel('Gridgen obstruction level (%)', fontsize=18)

plt.show(block = False)
time.sleep(10)
plt.savefig('gridgen.png', dpi=400, bbox_inches='tight')
