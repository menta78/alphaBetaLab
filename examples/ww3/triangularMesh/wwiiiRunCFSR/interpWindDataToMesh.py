import numpy as np
from scipy.interpolate import RegularGridInterpolator
import netCDF4

from alphaBetaLab import abFiniteElementsMesh

#from matplotlib import pyplot as plt


def interpWindDataToMesh():
  print('loading mesh file')
  meshfile = 'med.msh'
  mesh = abFiniteElementsMesh.loadFromMshFile(meshfile)

  nodeIds = mesh.nodes.keys()
  nodeIds.sort()
  nodeCrds = np.array([mesh.nodes[nid] for nid in nodeIds])
  nodeCrds = nodeCrds[:,::-1]
  
  windDs = netCDF4.Dataset('wind_g_glb150w.nc')
  wlon = windDs.variables['lon'][:]
  wlat = windDs.variables['lat'][:]
  tmnc = windDs.variables['time']
  u10 = windDs.variables['u10'][:]
  v10 = windDs.variables['v10'][:]
  tms = netCDF4.num2date(tmnc[:], tmnc.units, tmnc.calendar)
  windDs.close()
 
  outFl = open('wind.raw', 'w')
  for tm, itm in zip(tms, range(len(tms))):
    ln = tm.strftime('%Y%m%d %H%M%S\n')
    outFl.write(ln)

    u10i = u10[itm, :, :]
   #plt.figure()
   #plt.contourf(wlon, wlat, u10i)
   #plt.colorbar()
   #plt.xlim([-10, 40])
   #plt.ylim([30, 46])
    intpFunc = RegularGridInterpolator((wlat, wlon), u10i)
    u10intp = intpFunc(nodeCrds)
   #plt.figure()
   #plt.tricontourf(nodeCrds[:, 1], nodeCrds[:, 0], u10intp, tri=True)
   #plt.colorbar()
   #plt.show()

    v10i = v10[itm, :, :]
    intpFunc = RegularGridInterpolator((wlat, wlon), v10i)
    v10intp = intpFunc(nodeCrds)

    for u10nd in u10intp:
      outFl.write(str(u10nd) + '\n') 

    for v10nd in v10intp:
      outFl.write(str(v10nd) + '\n') 
  outFl.close()
  


if __name__ == '__main__':
  interpWindDataToMesh()

