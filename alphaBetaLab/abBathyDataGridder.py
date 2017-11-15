from itertools import izip, imap
import numpy as np
import matplotlib
from matplotlib.mlab import griddata
import multiprocessing as mp
from warnings import warn
from shapely import geometry as g
import sys

from abUtils import *


class abBathyDataGridder:


  def __init__(self, xs, ys, zs, landPolygons = [], nParallelWorker = 4, verbose = True):
    """
    abBathyDataGridder: class to manage fast gridding of sparse bathymetry data.
    xs, ys, zs: 1d arrays of x, y and z
    landPolygons: list of polygons corresponding to land areas.
    NOTE these must be polygons, just coastline is not enough.
    If you load coastline from basemap.Basemap.coastsegs,
    it should be in the correct format.
    If matloblib version <= 1.3 is used it is recommended
    an installation of natgrid, which provides bindings
    to the ncar interpolating procedures.
    """
    self.doGrid = self.doGridParallel
    self.x = np.array(xs)
    self.y = np.array(ys)
    self.z = np.array(zs)
    # nxInterpSteps: x size of each patch
    self.nxInterpSteps = 100
    self.nxInterpExtraSteps = 20
    # nyInterpSteps: y size of each patch
    self.nyInterpSteps = 100
    self.nyInterpExtraSteps = 20
    self.setLandPolygons(landPolygons)
    self.nParallelWorker = nParallelWorker
    self.patchDataThresholdLength = 20
    self.verbose = verbose
    if (matplotlib.__version__ < '1.4'):
      try:
        from mpl_toolkits import natgrid
      except:  
        warn('WE RECOMMEND INSTALLING natgrid: matplotlib version is <= 1.3 and natgrid is not installed')


  def _print(self, msg):
    if self.verbose:
      print(msg)

  
  def setLandPolygons(self, landPolygons):
    self.landPolygons = [g.Polygon(p) for p in landPolygons]


  def _reduceXYZ(self, minx, maxx, dx, miny, maxy, dy):
    _x, _y, _z = self.x, self.y, self.z
    cond = np.bitwise_and(\
              np.bitwise_and(np.greater_equal(_x, minx - dx), np.less_equal(_x, maxx + dx)),\
              np.bitwise_and(np.greater_equal(_y, miny - dy), np.less_equal(_y, maxy + dy))\
           )
    x = _x[cond]
    y = _y[cond]
    z = _z[cond]

    self._print('reducing the number of points')
    self._print('  mapping bathy points by gridded cell')
    ptsmap = {}
    xymap = {}
    nx = int(np.floor((maxx - minx)/dx))
    ny = int(np.floor((maxy - miny)/dy))
    for xi, yi, zi in izip(x, y, z):
      xy = (xi, yi)
      if not (xy in xymap):
        ix = int(np.floor((xi - minx) / dx))
        iy = int(np.floor((yi - miny) / dy))
        if ix < -2  or ix > nx+2 or iy < -2 or iy > ny+2:
          continue
        ptslst = ptsmap.get((ix, iy), [])
        ptsmap[(ix, iy)] = ptslst
        ptslst.append([xi, yi, zi])
        xymap[(xi,yi)] = zi
    self._print('  creating reduced points list')
    
    self._print('  gathering reduced points')
    redx, redy, redz = [], [], []
    ptsiter = ptsmap.itervalues()
    for cellpts in ptsiter:
      cellpts = np.array(cellpts)
      clxs = cellpts[:,0]
      xr = np.mean(clxs)
      clys = cellpts[:,1]
      yr = np.mean(clys)
      clzs = cellpts[:,2]
      zr = np.mean(clzs)
      redx.append(xr)
      redy.append(yr)
      redz.append(zr)
    
    minredx, maxredx = min(redx), max(redx)
    while minx < minredx:
      minx += dx
    while maxx > maxredx:
      maxx -= dx
    if minx >= maxx:
      raise abException\
              ('x coords of interpolating points are outside of the grid')

    minredy, maxredy = min(redy), max(redy)
    while miny < minredy:
      miny += dy
    while maxy > maxredy:
      maxy -= dy
    if miny >= maxy:
      raise abException\
              ('y coords of interpolating points are outside of the grid')

    grdx = np.arange(minx, maxx, dx)
    grdy = np.arange(miny, maxy, dy)
 
    self.redx, self.redy, self.redz = np.array(redx), np.array(redy), np.array(redz)
    self.grdx, self.grdy = np.array(grdx), np.array(grdy)
    self.minx, self.maxx = minx, maxx
    self.miny, self.maxy = miny, maxy
    self.dx, self.dy = dx, dy




  def getNXNYInterpPatch(self):
    nx = np.floor(float( len(self.grdx) ) / float(self.nxInterpSteps))
    nx = max(nx, 1)
    ny = np.floor(float( len(self.grdy) ) / float(self.nyInterpSteps))
    ny = max(ny, 1)
    return nx, ny


  def getInterpPatch(self, ixstep, iystep):
    redx, redy, redz = self.redx, self.redy, self.redz
    grdx, grdy = self.grdx, self.grdy
    dx, dy = self.dy, self.dy
    nxExtra = self.nxInterpExtraSteps
    nyExtra = self.nyInterpExtraSteps
    igrdxStart = ixstep*self.nxInterpSteps
    igrdxEnd = min( len(grdx), (ixstep + 1)*self.nxInterpSteps )
    if len(grdx) - igrdxEnd < self.nxInterpSteps:
      igrdxEnd = len(grdx) + 1
    igrdyStart = iystep*self.nyInterpSteps
    igrdyEnd = min( len(grdy), (iystep + 1)*self.nyInterpSteps )
    if len(grdy) - igrdyEnd < self.nyInterpSteps:
      igrdyEnd = len(grdy) + 1
    pgrdx = grdx[igrdxStart:igrdxEnd]
    pgrdy = grdy[igrdyStart:igrdyEnd]
    minx, maxx = min(pgrdx) - dx*nxExtra, max(pgrdx) + dx*(nxExtra + 1)
    miny, maxy = min(pgrdy) - dy*nyExtra, max(pgrdy) + dy*(nyExtra + 1)
    condx = np.logical_and(redx >= minx, redx <= maxx)
    condy = np.logical_and(redy >= miny, redy <= maxy)
    cond = np.logical_and(condx, condy)
    predx = redx[cond]
    predy = redy[cond]
    predz = redz[cond]
    return predx, predy, predz, pgrdx, pgrdy
    

  def _progress(self, percent):
    if self.verbose:
      sys.stdout.write('\r  progress: {:2.1f} %'.format(percent))
      sys.stdout.flush()


  def doGridSerial(self, minx, maxx, dx, miny, maxy, dy):
    self._print('')
    self._print('')
    self._print('reducing input data')
    self._reduceXYZ(minx, maxx, dx, miny, maxy, dy)
    self._print(' ... done')
    self._print('')

    grdx, grdy = self.grdx, self.grdy    
    grdz = np.zeros((len(grdy), len(grdx)))

    npatchx, npatchy = self.getNXNYInterpPatch()
    npatchx, npatchy = int(npatchx), int(npatchy)
    ntot = npatchx*npatchy
    patchGenerator = ((ipx, ipy) for ipx in range(npatchx) for ipy in range(npatchy))

    self._print('interpolating and gethering the results ...')
    global btDtGridder
    btDtGridder = self
    intpPatches = imap(_intpOnePatch, patchGenerator)
    for pgrdx, pgrdy, pgrdz, iix, iiy in intpPatches:
      perc = float(iix*npatchy + iiy)/ntot*100
      self._progress(perc)

      indxx = np.where(np.in1d(grdx, pgrdx))[0]
      indxy = np.where(np.in1d(grdy, pgrdy))[0]
      ix, iy = np.meshgrid(indxx, indxy)
      grdz[iy, ix] = pgrdz
    
    self._print(' ... done')
    self.doNanLandCells(grdx, grdy, grdz)
    return grdx, grdy, grdz


  def doGridParallel(self, minx, maxx, dx, miny, maxy, dy):
    self._print('')
    self._print('')
    self._print('reducing input data')
    self._reduceXYZ(minx, maxx, dx, miny, maxy, dy)
    self._print(' ... done')
    self._print('')

    grdx, grdy = self.grdx, self.grdy    
    grdz = np.zeros((len(grdy), len(grdx)))

    npatchx, npatchy = self.getNXNYInterpPatch()
    npatchx, npatchy = int(npatchx), int(npatchy)
    ntot = npatchx*npatchy
    patchGenerator = ((ipx, ipy) for ipx in range(npatchx) for ipy in range(npatchy))

    self._print('interpolating and gethering results ...')
    global btDtGridder
    btDtGridder = self
    p = mp.Pool(self.nParallelWorker)
    if self.nParallelWorker > 1:
      intpPatches = p.imap(_intpOnePatch, patchGenerator)
    else:
      intpPatches = imap(_intpOnePatch, patchGenerator)
    for pgrdx, pgrdy, pgrdz, iix, iiy in intpPatches:
      perc = float(iix*npatchy + iiy)/ntot*100
      self._progress(perc)

      indxx = np.where(np.in1d(grdx, pgrdx))[0]
      indxy = np.where(np.in1d(grdy, pgrdy))[0]
      ix, iy = np.meshgrid(indxx, indxy)
      grdz[iy, ix] = pgrdz
    
    p.close()
    self._print(' ... done')
    self.doNanLandCells(grdx, grdy, grdz)
    return grdx, grdy, grdz


  def _getLandPointIndexes(self, grdx, grdy, grdz):
    global landPolygons, xcs, ycs, dx, dy
    xcs, ycs = grdx, grdy
    dx, dy = self.dx, self.dy
    ixcs, iycs = range(len(xcs)), range(len(ycs))
    ixcs, iycs = np.meshgrid(ixcs, iycs)
    ixcs, iycs = ixcs.flatten(), iycs.flatten()
    
    if len(self.landPolygons) == 0:
      return [], []

    landPolygons = self.landPolygons
    p = mp.Pool(self.nParallelWorker)
    grdzflatten = grdz.flatten()
    if self.nParallelWorker > 1:
      inLandIxIy = p.imap(_computePointInLand, izip(ixcs, iycs, grdzflatten))
    else:
      inLandIxIy = imap(_computePointInLand, izip(ixcs, iycs, grdzflatten))
    ntot = len(grdzflatten)
    nx = grdz.shape[1]
    landxindxs, landyindxs = [], []
    for inLand, ix, iy in inLandIxIy:
      ii = iy*nx + ix
      if ii % 50 == 0:
        perc = float(ii)/ntot*100.
        self._progress(perc)
      if inLand:
        landxindxs.append(ix)
        landyindxs.append(iy)
    p.close()
    return landxindxs, landyindxs


  def doNanLandCells(self, grdx, grdy, grdz):
    self._print('setting land points to nan')
    self._print('  getting land point indexes ...')    
    landxindxs, landyindxs = self._getLandPointIndexes(grdx, grdy, grdz)
    self._print(' ... done')
    if len(landxindxs) > 0:
      grdz[np.array(landyindxs), np.array(landxindxs)] = np.nan
    pass
   

def _composeIntpErrorMessage(ix, iy, pgrdx, pgrdy):
  minx, maxx = min(pgrdx), max(pgrdx)
  miny, maxy = min(pgrdy), max(pgrdy)
  msg = 'too few data to interpolate.' 
  msg += ' patch: ix, iy == ' + str(ix) + ', ' + str(iy) + '. '
  msg += ' location: '
  msg += ' minx, maxx == ' + str(minx) + ', ' + str(maxx) + '; '
  msg += ' miny, maxy == ' + str(miny) + ', ' + str(maxy) + '. '
  return msg
      
 
def _intpOnePatch(patch):
  ix, iy = patch
  predx, predy, predz, pgrdx, pgrdy = btDtGridder.getInterpPatch(*patch)
  if len(predx) < 3:
    msg = _composeIntpErrorMessage(ix, iy, pgrdx, pgrdy)
    msg += 'This patch looks on land. Setting the whole patch to nan'
    btDtGridder._print(msg)
    pgrdz = np.ones((len(pgrdy), len(pgrdx)))*np.nan
    return pgrdx, pgrdy, pgrdz, ix, iy
  elif len(predx) < btDtGridder.patchDataThresholdLength:
    msg = _composeIntpErrorMessage(ix, iy, pgrdx, pgrdy)
    msg += 'Try with a bigger value of gridder.nxInterpSteps, gridder.nyInterpSteps'
    raise abException(msg)
  pts = np.array([predx, predy]).T
  pgrdz = griddata(predx, predy, predz, pgrdx, pgrdy)
  return pgrdx, pgrdy, pgrdz, ix, iy
    


def _computePointInLand(pointCrds):
  ix, iy, z = pointCrds
  if np.isnan(z):
    inLand = True
  else:
    x0, y0 = xcs[ix], ycs[iy]
    x1, y1 = x0 + dx, y0 + dy
    cell = g.Polygon([[x0, y0], [x1, y0], [x1, y1], [x0, y1]])
    inLand = False
    for lp in landPolygons:
      #if lp.contains(cell) or lp.crosses(cell) or lp.equals(cell) or lp.within(cell):
      if lp.intersects(cell):
        inLand = True
        break
  return inLand, ix, iy
