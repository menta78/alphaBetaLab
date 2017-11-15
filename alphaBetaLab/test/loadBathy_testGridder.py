import os
import numpy as np
from matplotlib.mlab import griddata
import itertools

def loadBathy():
  fname = 'testGridder_xyz.dat';
  fdir = os.path.dirname(os.path.abspath(__file__))
  fpath = os.path.join(fdir, fname)

  rslt = []
  fl = open(fpath)
  for ln in fl:
    ln = ln.strip(' \n')
    vls = ln.split()
    if (not ln) or (len(vls) < 3):
      continue
    lon = float(vls[0])
    lat = float(vls[1])
    dpt = float(vls[2])
    rslt.append([lon, lat, dpt])
  return np.array(rslt)

def loadCoastline():
  fname = 'rand.dat'
  fdir = os.path.dirname(os.path.abspath(__file__))
  fpath = os.path.join(fdir, fname)
  
  rslt = []
  fl = open(fpath)
  for ln in fl:
    ln = ln.strip(' \n')
    vls = ln.split()
    if (not ln) or (len(vls) < 4):
      continue
    lon = float(vls[1])
    lat = float(vls[2])
    rslt.append([lon, lat])
  return np.array(rslt)

def loadIslands():
  fname = 'insel.dat'
  fdir = os.path.dirname(os.path.abspath(__file__))
  fpath = os.path.join(fdir, fname)
  
  islands = []
  fl = open(fpath)
  
  def loadIsland():
    islandStr = fl.readline()
    if not islandStr:
      return None
    points = []
    endOfIsland = False
    while True:
      ln = fl.readline().strip(' \n\r\t')
      if ln == '-1':
        break
      vls = ln.split()
      lon = float(vls[1])
      lat = float(vls[2])
      points.append([lon, lat])
    return np.array(points)
      
  while True:
    islPoints = loadIsland()
    if islPoints != None:
      islands.append(islPoints)
    else:
      break
  return islands
