import numpy as np
import shapely.geometry as gm
import sys
import multiprocessing as mp

from .abUtils import *
from . import abCoastalCellDetector


def getSeaGrid(cells, cellCoordinates, highResAlphaMtx, coastalCellDetector, 
               centroids=None, nParWorker=4):
  """
  getSeaGrid: builds an abGrid object without land/coastal cells.
  """
  grd = _abGrid(cells, cellCoordinates, centroids=centroids, nParWorker=nParWorker)
  seaGrid = grd.removeLandAndCoastalCells(highResAlphaMtx, coastalCellDetector)
  return seaGrid


def getLandSeaGrid(cells, cellCoordinates, centroids=None, nParWorker=4):
  """
  getLandSeaGrid: builds an abGrid object with all the cells, on land and sea.
  """
  return _abGrid(cells, cellCoordinates, centroids=centroids, nParWorker=nParWorker)


class _abGrid:

  def __init__(self, cells, cellCoordinates, centroids=None, nParWorker = 4):
    """
    abGrid: object representing a grid as a collection of polygons, each representing a cell.
    The represented grid can be unstructured.
    Arguments:
    cells: must be a shapely MultiPolygon
    cellCoordinates: should be an array with n rows, with n the count of the cells, and 2 cols.
       It can also be a n-length list of 2-length tuples. cellCoordinates contains
       the x,y indexes of the cells. For unstructured grid the x index has a meaningful
       value, the y index is always 0.
    """
    self.cells = cells
    self.cellCoordinates = [tuple(l) for l in cellCoordinates]
    if centroids is None:
      self.centroids = [c.centroid.coords[0] for c in cells]
    else:
      self.centroids = centroids
    self.cellMap = dict(zip(self.cellCoordinates, cells))
    self.cellSfc = [c.area for c in cells]
    self.cellBnd = [tuple(c.boundary.coords[:]) for c in cells]
    self._neigCache = None
    self.nParWorker = nParWorker
    self.wrapAroundDateline = self._autoDetectNeedsWrapAroundDateline()

  def _autoDetectNeedsWrapAroundDateline(self, bufferDegThreshold=5):
    cntrX = np.array([c[0] for c in self.centroids])
    minCentroid, maxCentroid = np.min(cntrX), np.max(cntrX)
    if np.abs(np.abs(maxCentroid - minCentroid) - 360) <= bufferDegThreshold:
      return True
    else:
      return False

  def getGeoCoords(self):
    """
    returns a list with the geographical coordinates of cells.
    For each cell its centroid is returned as geographical coordinate
    """
    return self.centroids


  def getNeighbors(self, cell):
    #cls = []
    #for c in self.cells:
    #  if (c != cell) and lesserClose(cell.distance(c), 0.):
    #    cls.append(c)
    #return gm.MultiPolygon(cls)

    if self._neigCache is None:
      self.buildNeighCache()
    cellCrds = tuple(cell.boundary.coords[:])
    ngLst = self._neigCache[cellCrds]
    return gm.MultiPolygon([gm.Polygon(c) for c in ngLst])



  def buildNeighCache(self):
    if not self._neigCache is None:
      return

    def getMaxDiam(cl):
      clx = [c[0] for c in cl]
      minx, maxx = min(clx), max(clx)
      cly = [c[1] for c in cl]
      miny, maxy = min(cly), max(cly)
      mxdd = np.sqrt((maxx - minx)**2 + (maxy - miny)**2)
      return mxdd

    def wrapCellsAround(cls, clsCrd1s, clsCrdss):
      """
      builds a buffer of cells beyond the datelines, to let
      closing a global mesh (or a mesh passing the dateline)
        cls: list of cell polygons
        clsCrd1s: ordinate coordinates of the cell. 
                  E.g. the third cell of the first raw of cells has coords (0,2)
        clsCrdss: lonlat coordinates of the cell vertices.
      """
      lons = np.array([c[0][0] for c in clsCrdss])
      lats = np.array([c[0][1] for c in clsCrdss])

      # creating a longitudinal buffer where the cells will be wrapped.
      # this buffer increases with latitude
      latabs = np.abs(lats)
      buffDeg = np.ones(lats.shape)
      buffDeg[latabs <= 50] = 2
      buffDeg[np.logical_and(70 <= latabs, latabs <= 50)] = 3
      buffDeg[latabs > 70] = 5

      minlon, maxlon = np.min(lons), np.max(lons)

      ncell = len(cls)
      assert(ncell == len(self.centroids))
      for icell in range(ncell):
        cntr = self.centroids[icell]
        if (cntr[0] < minlon+buffDeg[icell]):
          # this cell is close to the east side of the dateline.
          # copying it to the west side
          clcrd = clsCrdss[icell]
          clcrdX = np.array([v[0] for v in clcrd])
          clcrdX = clcrdX + 360
          clcrdY = np.array([v[1] for v in clcrd])
          clcrdNew = tuple(v for v in zip(clcrdX, clcrdY))
          clsCrdss.append(clcrdNew)
          clsCrd1s.append(clsCrd1s[icell])
          cls.append(gm.Polygon(clcrdNew))
        elif (cntr[0] > maxlon-buffDeg[icell]):
          # this cell is close to the west side of the dateline.
          # copying it to the east side
          clcrd = clsCrdss[icell]
          clcrdX = np.array([v[0] for v in clcrd])
          clcrdX = clcrdX - 360
          clcrdY = np.array([v[1] for v in clcrd])
          clcrdNew = tuple(v for v in zip(clcrdX, clcrdY))
          clsCrdss.append(clcrdNew)
          clsCrd1s.append(clsCrd1s[icell])
          cls.append(gm.Polygon(clcrdNew))

    print('    building neighbor cells cache (can take some time) ...')
    global cls, clsCrd1s, clsCrdss, maxDiams, nclCrd0, nclCrd1
    cls = [c for c in self.cells]
    clsCrd1s = self.cellCoordinates
    clsCrdss = self.cellBnd
    lc = len(cls) # this ensures that the loop to build the neighborhood finishes with the real cells
    if self.wrapAroundDateline:
      wrapCellsAround(cls, clsCrd1s, clsCrdss)
    maxDiams = np.array([getMaxDiam(c) for c in clsCrdss])
    nclCrd0 = np.array([c[0][0] for c in clsCrdss])
    nclCrd1 = np.array([c[0][1] for c in clsCrdss])
    cch = {}
    ic = 0

    if self.nParWorker > 1:
      print('    initializing parallel environment ..')
      pl = mp.Pool(self.nParWorker)
      print('      ... done')
      neighCellsGen = pl.imap(_buildNeighCacheParallelJob, zip(cls, clsCrdss, maxDiams, range(lc)))
    else:
      neighCellsGen = map(_buildNeighCacheParallelJob, zip(cls, clsCrdss, maxDiams, range(lc)))
          
    for clCrds, cneighs_ in neighCellsGen:
      if ic % max(1, (lc // 1000)) == 0:
        sys.stdout.write('\r      ' + '{a:2.1f}'.format(a = float(ic)/lc*100) + '% done')
        sys.stdout.flush()
      ic += 1
      cneighs = cch.get(clCrds, [])
      cneighs.extend(cneighs_)
      cch[clCrds] = cneighs
      for nclCrds in cneighs_:
        ncneighs = cch.get(nclCrds, [])
        ncneighs.append(clCrds)
        cch[nclCrds] = ncneighs

    if self.nParWorker > 1:
      pl.close()
      del pl

    print('    ... neighborhood cells cache built')
    self._neigCache = cch


  def removeLandAndCoastalCells(self, hiResAlphaMtx, coastalCellDetector):
    """
    removeLandAndCoastalCells: produces a new grid object, removing land and coastal cells
    """
    cells = self.cells 
    cellCoordinates = self.cellCoordinates 
    centroids = self.centroids 
    cellBnd = self.cellBnd 
    cellSfc = self.cellSfc 
    cellMap = self.cellMap 
    nParWorker = self.nParWorker 

    global alphaMtx, cstClDet
    alphaMtx, cstClDet = hiResAlphaMtx, coastalCellDetector
    
    ncell = len(cells)
    if self.nParWorker > 1:
      print('    initializing parallel environment ..')
      pl = mp.Pool(self.nParWorker)
      print('      ... done')
      isLandOrCoastalCellGen = pl.imap(_cellIsOnLandOrCoastal, zip(cells, cellBnd, cellSfc, range(ncell)))
    else:
      isLandOrCoastalCellGen = map(_cellIsOnLandOrCoastal, zip(cells, cellBnd, cellSfc, range(ncell)))

    seaCells = []
    seaCellCrd = []
    for isLandOrCoastal, icell in isLandOrCoastalCellGen:
      if not isLandOrCoastal:
        seaCells.append(cells[icell])
        seaCellCrd.append(cellCoordinates[icell])

    if self.nParWorker > 1:
      pl.close()
      del pl

    newMesh = _abGrid(seaCells, seaCellCrd, nParWorker = self.nParWorker)
    return newMesh

    


    

def _cellIsOnLandOrCoastal(tpl):
  cell, boundary, surface, icell = tpl
  cellAlphaMtx = alphaMtx.getAlphaSubMatrix(cell)
  onLand = cellAlphaMtx.onLand()
  isCoastal = cstClDet.isCoastalCell(cell, boundary, surface) if not onLand else False
  return onLand or isCoastal, icell


def _buildNeighCacheParallelJob(tpl):
  cl, clCrds, clMaxD, ic = tpl
  cneighs = []

  inc = ic + 1

  maxDiams_ = maxDiams[inc:]
  nclCrd0_ = nclCrd0[inc:]
  nclCrd1_ = nclCrd1[inc:]
  frstPtDx_ = np.abs(nclCrd0_ - clCrds[0][0])
  gt180cnd = frstPtDx_ > 180
  frstPtDx_[gt180cnd] = np.abs(frstPtDx_[gt180cnd] - 360.)
  frstPtDy_ = nclCrd1_ - clCrds[0][1]
  frstPtDist_ = np.sqrt(frstPtDx_**2 + frstPtDy_**2)
  iiCloseCells = np.where(frstPtDist_ < clMaxD + maxDiams_)[0]

  for iiClsCell in iiCloseCells:
    ii_ = inc + iiClsCell
    ncl = cls[ii_]
    nclCrds = clsCrdss[ii_]
    if lesserClose(cl.distance(ncl), 0):
      cneighs.append(nclCrds)
    
  return clCrds, cneighs
    






  

