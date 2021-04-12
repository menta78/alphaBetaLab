import numpy as np
from shapely import affinity as aff
from shapely import geometry as g

from .abUtils import *


def _computeAvgDir(cell):
  """
  _computeAvgDir: computes the average direction of the minimum rectangle enclosing the polygon
  modulo np.pi/2
  works well for rectangular cells, not ideal for other cells, but for now can do
  
  """
  rect = cell.minimum_rotated_rectangle
  crds = np.array(list(rect.boundary.coords[:]))
  xs = np.array([c[0] for c in crds[:2]])
  ys = np.array([c[1] for c in crds[:2]])

  avgDir = np.arctan2(ys[1]-ys[0], xs[1]-xs[0])
  return avgDir % (np.pi/2.)


class abCellSize:
  def __init__(self, cell):
    """
    abCellSize: compute the approximate size of a cell in whatever direction.
    Computes the sizes at directions of 
    0, a, pi/2, pi/2 + a, pi radiants with respect to the main axis of the cell,
    with respect to the average direction of the polygon.
    where a=arctan(dy/dx), dx, dy being the x-y sizes of the cell.
    Then interpolates them to the requested direction.
    Assumes a convex polygon and an euclidean geometry.
    """
    self.cell = cell
    self.angles = None
    self._sizes = None
    self.cellXs = None
    self.cellYs = None
    self.majorAxisDir = None
    self._computeSizeAtMainDirections()
    

  def _computeSizeAtMainDirections(self):
    """
    computes the sizes at directions of 
    0, arctan(dy/dx), pi/2, pi/2 + arctan(dy/dx), pi radiants
    """
    cell = self.cell
    avgDir = _computeAvgDir(cell)
    s = [0, 0, 0, 0, 0]
    a = [avgDir, -10, avgDir + np.pi/2, -10, avgDir + np.pi]
    cell = aff.rotate(cell, -avgDir, use_radians=True)
    self._avgdir = avgDir
    self._sizes = s
    self._angles = a
    crds = list(cell.boundary.coords)
    xs = np.array([c[0] for c in crds])
    ys = np.array([c[1] for c in crds])
    dx = max(xs) - min(xs)
    dy = max(ys) - min(ys)
    s[0] = dx
    s[2] = dy
    s[4] = dx

    angle = np.arctan2(dy, dx)
    a[1] = avgDir + angle
    a[3] = avgDir + np.pi - angle
    
    rcell = aff.rotate(cell, -angle, use_radians=True)
    crds = list(rcell.boundary.coords)
    xs = np.array([c[0] for c in crds])
    dx = max(xs) - min(xs)
    s[1] = dx
    
    rcell = aff.rotate(cell, +angle, use_radians=True)
    crds = list(rcell.boundary.coords)
    xs = np.array([c[0] for c in crds])
    dx = max(xs) - min(xs)
    s[3] = dx

    self.majorAxisDir = avgDir if (s[0] > s[2]) else avgDir + np.pi/2.


  def computeSize(self, direction):
    if self._sizes == None:
      self._computeSizeAtMainDirections()

    szs = self._sizes
    ang = self._angles - self._avgdir
    dr = (direction - self._avgdir) % np.pi

    for idr in range(len(ang)):
      if greaterClose(ang[idr], dr):
        break

    dr1 = ang[idr - 1] if idr > 0 else ang[0]
    dr2 = ang[idr]
    sz1 = szs[idr - 1] if idr > 0 else szs[0]
    sz2 = szs[idr]

    if isClose(dr1, dr2):
      intpsize = sz1
    else:
      if idr == 1:
        drw2 = dr
        drw1 = dr2
        sz1_ = sz1
        sz2_ = sz2
      if idr == 3:
        drw2 = dr - np.pi/2.
        drw1 = dr2 - np.pi/2.
        sz1_ = sz1
        sz2_ = sz2
      elif idr == 2:
        drw2 = np.pi/2. - dr
        drw1 = np.pi/2. - dr1
        sz1_ = sz2
        sz2_ = sz1
      elif idr == 4:
        drw2 = np.pi - dr
        drw1 = np.pi - dr1
        sz1_ = sz2
        sz2_ = sz1

      w2 = np.tan(drw2)
      wtot = np.tan(drw1)
      w1 = wtot - w2

      if not isClose(wtot, 0):
        intpsize = (w1*sz1_ + w2*sz2_)/(w1 + w2)
      else:
        intpsize = sz2
    
    return intpsize
    

  def computeSizes(self, directions):
    sizes = []
    for d in directions:
      sz = self.computeSize(d)
      sizes.append(sz)
    return np.array(sizes)

    
  def computeSizesKm(self, directions):
    sizes = self.computeSizes(directions)
    cellLonLat = self.cell
    if self.cellXs is None:
      crds = np.array(list(cellLonLat.boundary.coords))
      self.cellXs = np.array([c[0] for c in crds])
      self.cellYs = np.array([c[1] for c in crds])
    lons = self.cellXs
    lats = self.cellYs
    dera = np.pi/180.
    avglon = np.mean(lons)*dera
    avglat = np.mean(lats)*dera
    sizesXs = sizes*dera*np.cos(directions)*radiusEarth/1000.
    sizesYs = sizes*dera*np.sin(directions)*radiusEarth/1000.
    sizesKm =(sizesYs**2. + (sizesXs*np.cos(avglat))**2.)**.5
    return sizesKm

