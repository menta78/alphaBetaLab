import numpy as np
import shapely.geometry as gm
from itertools import izip, imap
import sys
import multiprocessing as mp

from abUtils import *
import abCoastalCellDetector


def getSeaGrid(cells, cellCoordinates, highResAlphaMtx, coastalCellDetector, nParWorker = 4):
  """
  getSeaGrid: builds an abGrid object without land/coastal cells.
  """
  grd = _abGrid(cells, cellCoordinates, nParWorker)
  seaGrid = grd.removeLandAndCoastalCells(highResAlphaMtx, coastalCellDetector)
  return seaGrid


def getLandSeaGrid(cells, cellCoordinates, nParWorker = 4):
  """
  getLandSeaGrid: builds an abGrid object with all the cells, on land and sea.
  """
  return _abGrid(cells, cellCoordinates, nParWorker)


class _abGrid:

  def __init__(self, cells, cellCoordinates, nParWorker = 4):
    """
    abGrid: object representing a grid as a collection of polygons, each representing a cell.
    The represented grid can be unstructured.
    Arguments:
    cells must be a shapely MultiPolygon
    cellCoordinates should be an array with n rows, with n the count of the cells, and 2 cols.
       It can also be a n-length list of 2-length tuples. cellCoordinates contains
       the x,y indexes of the cells. For unstructured grid the x index has a meaningful
       value, the y index is always 0.
    """
    self.cells = cells
    self.cellCoordinates = [tuple(l) for l in cellCoordinates]
    self.centroids = [c.centroid.coords[0] for c in cells]
    self.cellMap = dict(zip(self.cellCoordinates, cells))
    self.cellSfc = [c.area for c in cells]
    self.cellBnd = [tuple(c.boundary.coords[:]) for c in cells]
    self._neigCache = None
    self.nParWorker = nParWorker


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

    print('    building neighbor cells cache (can take some time) ...')
    global cls, clsCrd1s, clsCrdss, maxDiams
    cls = [c for c in self.cells]
    clsCrd1s = self.cellCoordinates
    clsCrdss = self.cellBnd
    maxDiams = [getMaxDiam(c) for c in clsCrdss]
    cch = {}
    lc = len(cls)
    ic = 0

    if self.nParWorker > 1:
      print('    initializing parallel environment ..')
      pl = mp.Pool(self.nParWorker)
      print('      ... done')
      neighCellsGen = pl.imap(_buildNeighCacheParallelJob, izip(cls, clsCrdss, maxDiams, range(lc)))
    else:
      neighCellsGen = imap(_buildNeighCacheParallelJob, izip(cls, clsCrdss, maxDiams, range(lc)))
          
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
      isLandOrCoastalCellGen = pl.imap(_cellIsOnLandOrCoastal, izip(cells, cellBnd, cellSfc, range(ncell)))
    else:
      isLandOrCoastalCellGen = imap(_cellIsOnLandOrCoastal, izip(cells, cellBnd, cellSfc, range(ncell)))

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
  

def _isNeigh(cl, clCrd, clMaxD, ncl, nclCrd, nclMaxD):
  # excluding from complex computation very far cells
  frstPtDist = np.sqrt((nclCrd[0] - clCrd[0])**2 + (nclCrd[1] - clCrd[1])**2)
  if frstPtDist < (clMaxD + nclMaxD):
    return lesserClose(cl.distance(ncl), 0.)
  else:
    return False


def _buildNeighCacheParallelJob(tpl):
  cl, clCrds, clMaxD, ic = tpl
  cneighs = []
  inc = ic + 1
  for ncl, nclCrd1, nclCrds, nclMaxD in izip(cls[inc:], clsCrd1s[inc:], clsCrdss[inc:], maxDiams[inc:]):
    if _isNeigh(cl, clCrds[0], clMaxD, ncl, nclCrds[0], nclMaxD):
      cneighs.append(nclCrds)
  return clCrds, cneighs
    






  

