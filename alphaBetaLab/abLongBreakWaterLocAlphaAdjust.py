import sys
import traceback
import numpy as np
from shapely import geometry as g
import multiprocessing as mp

import abCellSize
import abUtils




class abLongBreakWaterLocAlphaAdjust:
  

  def __init__(self, cell, neighbors, coastPolygons, directions, alphas, betas):
    self.cell = cell
    self.neighbors = [c for c in neighbors if c != cell]
    totPoly = cell
    for cl in self.neighbors:
      totPoly = totPoly.union(cl)
    if totPoly.__class__ != g.Polygon:
    # totPoly = totPoly.convex_hull
      totPoly = None
    self.totPoly = totPoly
    self.isBoundaryCell = totPoly.boundary.intersects(cell.boundary) if (totPoly != None) else True
    self.coastPolygons = [g.Polygon(p) for p in coastPolygons]
    self.directions = directions
    self.alphas = np.array(alphas)
    self.betas = np.array(betas)
    self.thresholdNInts = 3
    clSz = abCellSize.abCellSize(cell)
    self.minObstSizeKm = clSz.computeSizesKm([clSz.majorAxisDir])[0]*2.


  def _countIntersectNeighbors(self, coastPoly):
    cnt = 0
    for nc in self.neighbors:
      if coastPoly.intersects(nc):
        cnt += 1
    return cnt


  def reviewLocalAlpha(self):
    alphas = self.alphas
    betas = self.betas
    if (not self.isBoundaryCell) and (self.totPoly != None):
      dirs = self.directions
      newalphas = np.ones(alphas.shape)
      newbetas = np.ones(betas.shape)
      for cstPoly in self.coastPolygons:
        # breakwater must intersect the cell
        cints = cstPoly.intersection(self.cell)
        if abUtils.greater(cints.area, 0):
          # the breakwater must cross at least two sides of the cell
          boundaryIntersect = cints.boundary.intersection(self.cell.boundary)
          if boundaryIntersect.__class__ is g.MultiLineString:   
            # the number of intersected cells of the neighborhood must be >= 3
            nints = self._countIntersectNeighbors(cstPoly) + 1
            plSz = abCellSize.abCellSize(cstPoly)
            cstPolySizeKm = plSz.computeSizesKm([plSz.majorAxisDir])[0]
            if nints >= self.thresholdNInts and cstPolySizeKm > self.minObstSizeKm:
              cstSection = cstPoly.intersection(self.totPoly)
              if not cstSection.__class__ is g.Polygon:
                # skipping strange case
                return alphas, betas
 
              clSz = abCellSize.abCellSize(cstSection)
              avgCoastDir = clSz.majorAxisDir
             
              for idr in range(len(dirs)):
                dr, alpha, beta = dirs[idr], alphas[:, idr], betas[:, idr]
                drDelta = np.abs(abUtils.angleDiff(avgCoastDir, dr))
                if drDelta > np.pi/2.:
                  drDelta = np.pi - drDelta
                coeff = 1. - drDelta/(np.pi/2.)
                assert 0. <= coeff <= 1. 
                nalpha = alpha*coeff
                nbeta = beta*coeff
                newalphas[:, idr] = nalpha
                newbetas[:, idr] = nbeta
              # assuming a maximum one breakwater per cell
              return newalphas, newbetas
    return alphas, betas




class abLongBreakWaterLocAlphaAdjustAllCells:
  

  def __init__(self, obstrCells, grid, coastPolygons, directions, alphas, betas, parallel = True, nParallelWorker = 4, verbose = True):
    self.obstrCells = obstrCells
    self.grid = grid
    self.coastPolygons = coastPolygons
    self.directions = directions
    self.alphas = alphas
    self.betas = betas
    self.parallel = parallel
    self.nParallelWorker = nParallelWorker
    if parallel and (nParallelWorker > 1):
      self.reviewLocalAlpha = self._reviewLocalAlphaParallel
    else:
      self.reviewLocalAlpha = self._reviewLocalAlphaSerial
    self.verbose = verbose


  def _progress(self, progPercentage):
    if self.verbose:
      sys.stdout.write('\r progress: {p:2.0f} %'.format(p = progPercentage))
      sys.stdout.flush()


  def _reviewLocalAlphaSerial(self):
    #loop on all the cells, istantiate abLongBreakWaterAdjust and invoke reviewAlpha
    global grid, coastPolygons, directions
    grid = self.grid
    coastPolygons = self.coastPolygons
    directions = self.directions
    obstrCells = self.obstrCells
    newAlphas, newBetas = [], []
    ncell = len(obstrCells)

    adjAlphaGenerator = map(_elabOneCell, zip(obstrCells, self.alphas, self.betas, range(len(obstrCells))))
    for cell, adjAlpha, adjBeta, icell in adjAlphaGenerator:
      newAlphas.append(adjAlpha)
      newBetas.append(adjBeta)

      if icell % 10 == 0:
        progPerc = (float(icell)/ncell)*100
        self._progress(progPerc)
    return newAlphas, newBetas


  def _reviewLocalAlphaParallel(self):
    #loop on all the cells, istantiate abLongBreakWaterAdjust and invoke reviewAlpha
    global grid, coastPolygons, directions
    grid = self.grid
    coastPolygons = self.coastPolygons
    directions = self.directions
    obstrCells = self.obstrCells
    newAlphas, newBetas = [], []
    ncell = len(obstrCells)

    p = mp.Pool(self.nParallelWorker)
    adjAlphaGenerator = p.imap(_elabOneCell, zip(obstrCells, self.alphas, self.betas, range(len(obstrCells))))
    for cell, adjAlpha, adjBeta, icell in adjAlphaGenerator:
      newAlphas.append(adjAlpha)
      newBetas.append(adjBeta)

      if icell % 10 == 0:
        progPerc = (float(icell)/ncell)*100
        self._progress(progPerc)
    p.close()

    return newAlphas, newBetas


def _elabOneCell(cellAlphaObj):
  try:
    cell, alphas, betas, icell = cellAlphaObj
    neighbors = grid.getNeighbors(cell)
    bwadj = abLongBreakWaterLocAlphaAdjust(cell, neighbors, coastPolygons, directions, alphas, betas)
    adjAlphas, adjBetas = bwadj.reviewLocalAlpha()
    return cell, adjAlphas, adjBetas, icell
  except:
    raise abUtils.abException("".join(traceback.format_exception(*sys.exc_info())))
  
