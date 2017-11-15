import numpy as np
from shapely import geometry as g
from abUtils import *

from abFirstOctantTransformation import abFirstOctantTransformation
import abAlphaBetaRecalibrator

debugPlots = False
debugPlotShow = False
debugPlotSave = True
thetaTolerance = .0001
defaultKShape = 1.

class _abSingleCellAlphaEstimatorLogInfo:
  pass

class abSingleCellAlphaEstimator:

  def __init__(self, polygon, alphaMtx, srcCellPolygon = None, kshape = -1,\
       obstrAlleviationParam = 1., obstrAlleviationThreshold = .9, recalibFactor = 1.):
    """
    abSingleCellAlphaEstimator: estimates the local average alpha for the given polygon,
    on the basis of the high resolution alpha matrix given by alphaMtx.
    """
    self.polygon = polygon
    if self.polygon == alphaMtx.polygon:
      self.alphaMtx = alphaMtx
    else:
      self.alphaMtx = alphaMtx.getAlphaSubMatrix(polygon)

    loginfo = _abSingleCellAlphaEstimatorLogInfo()
    loginfo.debugPlotSave = False
    loginfo.contextStrs = []
    loginfo.origPolygon = srcCellPolygon if srcCellPolygon else polygon
    self.loginfo = loginfo 
    """
    kshape = 1: in high resolution obstructed isolated cells obstacles are considered 
                as squares. 
    kshape = 0: obstacles are romboids.
    """
    self.kshape = kshape if (kshape != -1) else defaultKShape; 
    self.obstrAlleviationParam = obstrAlleviationParam
    if not isClose(obstrAlleviationParam, 1):
      self.obstrAlleviationExp = obstrAlleviationParam/(1 - obstrAlleviationParam)
    else:
      self.obstrAlleviationExp = 0.
    self.obstrAlleviationThreshold = obstrAlleviationThreshold
    self.obstrAlleviationEnabled = True
    self.recalib = abAlphaBetaRecalibrator.abAlphaBetaRecalibrator(obstFactor = recalibFactor)

  def computeAlpha(self, direction, frequency):
    if not self.alphaMtx.empty():
      firstOctTransf = abFirstOctantTransformation(self.alphaMtx, self.polygon)
      theta, alphaMtx, lowResCell = firstOctTransf.transform(direction)

      if debugPlots:
        import abHighResAlphaMatrixPlot as pt
        if debugPlotShow:
          pt.plotHiResAlphaMtx('orig. mtx/poly/theta', self.alphaMtx, direction)
          pt.plotHiResAlphaMtxAndShow('rot. mtx/poly/theta', alphaMtx, theta)
        elif debugPlotSave and self.loginfo.debugPlotSave:
          contextStrs = list(self.loginfo.contextStrs)
          contextStrs.append('orig')
          pt.plotHiResAlphaMtxAndSave('orig. mtx/poly/theta', self.alphaMtx, direction,\
              self.loginfo.origPolygon, contextStrs)
          contextStrs[-1] = 'rot'
          pt.plotHiResAlphaMtxAndSave('rot. mtx/poly/theta', alphaMtx, theta,\
              self.loginfo.origPolygon, contextStrs)
          
  
      a = self._getAlphaFirstOctant(theta, frequency, alphaMtx, lowResCell)
      a = self.recalib.recalibrate(a)
      return a
    else:
      return 1

  def _getAlphaFirstOctant(self, theta, frequency, alphaMtx, lowResCell):
    """
    theta must be <= pi/4
    alphaMtx must be referred to the first octant.
    """
    projsToX = []
    projsToY = []
    if len(alphaMtx.alphas.shape) < 2:
      return 1
    nx = alphaMtx.alphas.shape[1]
    ny = alphaMtx.alphas.shape[0]
    gd = alphaMtx.alphas
    xs = alphaMtx.xs
    ys = alphaMtx.ys
    cell = lowResCell
    crds = np.array(list(cell.boundary.coords))
    cellxs = np.array([c[0] for c in crds])
    cellys = np.array([c[1] for c in crds])
    cellminx, cellmaxx = min(cellxs), max(cellxs)
    cellminy, cellmaxy = min(cellys), max(cellys)
    if theta > thetaTolerance:
      #projecting all the vertexes to the line y = cellmaxy
      prxs = cellxs + (cellmaxy - cellys)/np.tan(theta)
      minprojx = min(prxs)
    else:
      minprojx = cellmaxx
    #projecting all the vertexes to the line x = cellmaxx
    prys = cellys + (cellmaxx - cellxs)*np.tan(theta)
    minprojy = min(prys)
    lowresDx = cellmaxx - minprojx
    lowresDy = cellmaxy - minprojy

    class projobj:
      pass

    def collectprojsToXY():
      #gd = highResCellGrid
      for ix in range(nx):
        for iy in range(ny):
          xi, yi = xs[ix], ys[iy]
          hresAlpha = alphaMtx.getAlpha(ix, iy, frequency)
          if isClose(hresAlpha, 1.):
            continue

          if len(xs) > 1:
            dx = xs[ix + 1] - xs[ix] if (ix < len(xs) - 1) else xs[-1] - xs[-2]
          else:
            dx = alphaMtx.dx

          if len(ys) > 1:
            dy = ys[iy + 1] - ys[iy] if (iy < len(ys) - 1) else ys[-1] - ys[-2]
          else:
            dy = alphaMtx.dy

          hrCellBorder = [[xi, yi], [xi + dx, yi], [xi + dx, yi + dy], [xi, yi + dy]]
          hrcell = g.Polygon(hrCellBorder)
          if cell.contains(hrcell):
            cellInts = g.Polygon(hrcell)
            hresCellIsInside = True
          elif cell.overlaps(hrcell):
            cellInts = cell.intersection(hrcell)
            if isClose(cellInts.area, hrcell.area):
              hresCellIsInside = True
            else:
              hresCellIsInside = False
          else:
            # intersection is an empty polygon
            cellInts = None
            hresCellIsInside = False
          
          if (cellInts == None) or isClose(cellInts.area, 0):
            # high res cell is outside coarse cell. Continuing
            continue
          hresAlpha = alphaMtx.getAlpha(ix, iy, frequency)
          if hresAlpha < 1.:

            def getIntersecPolygon():
              if cellInts.__class__ == g.Polygon:
                yield cellInts
              elif cellInts.__class__ in [g.GeometryCollection, g.MultiPolygon]:
                for p in cellInts:
                  if p.__class__ == g.Polygon:
                    yield p
              else:
                raise TypeError('Unsupported geometry object: ' + str(cellInts.__class__))

            for subcell in getIntersecPolygon():
              crds = np.array(list(subcell.boundary.coords))
              cellIntsXs = np.array([c[0] for c in crds])
              cellIntsYs = np.array([c[1] for c in crds])
              minx, maxx = min(cellIntsXs), max(cellIntsXs)
              miny, maxy = min(cellIntsYs), max(cellIntsYs)
  
              px = projobj()
              
              if theta > thetaTolerance:
                vrtxXs = cellIntsXs + (cellmaxy - cellIntsYs)/np.tan(theta)
                minxproj = min(vrtxXs)
                maxxproj = max(vrtxXs)
                pxobj = projobj()
                pxobj.start = minxproj
                pxobj.end = maxxproj
                pxobj.alpha = hresAlpha
                pxobj.canReshapeInf = hresCellIsInside
                pxobj.canReshapeSup = hresCellIsInside
                pxobj.dd = dy
                projsToX.append(pxobj)
     
              vrtxYs = cellIntsYs + (cellmaxx - cellIntsXs)*np.tan(theta)
              minyproj = min(vrtxYs)
              maxyproj = max(vrtxYs)
              pyobj = projobj()
              pyobj.start = minyproj
              pyobj.end = maxyproj
              pyobj.alpha = hresAlpha
              pyobj.canReshapeInf = hresCellIsInside
              pyobj.canReshapeSup = hresCellIsInside
              pyobj.dd = dx
              projsToY.append(pyobj)
      return


    def pruneAndSort():
      projsToX_ = [p for p in projsToX if p.start < cellmaxx]
      projsToX_.sort(lambda p1, p2: int(np.sign(p1.start - p2.start)))
      for p in projsToX_:
        p.canReshapeSup = p.canReshapeSup and not (lesser(p.start, cellmaxx) and greater(p.end, cellmaxx))
        p.end = min(p.end, cellmaxx)
      projsToY_ = [p for p in projsToY if p.start < cellmaxy]
      projsToY_.sort(lambda p1, p2: int(np.sign(p1.start - p2.start)))
      for p in projsToY_:
        p.canReshapeSup = p.canReshapeSup and not (lesser(p.start, cellmaxy) and greater(p.end, cellmaxy))
        p.end = min(p.end, cellmaxy)
      return projsToX_, projsToY_

    def pruneOverlaps(points):
      overlapExists = True
      while overlapExists:
        overlapExists = False
        oldPts = points
        points = []
        lowestPt = None
        for i in range(len(oldPts)):
          actualPt = oldPts[i]
          if (not lowestPt) or lesserClose(lowestPt.end, actualPt.start):
            lowestPt = actualPt
            points.append(lowestPt)
          elif greater(actualPt.end, lowestPt.end): 
            lowestPt.end = actualPt.end
            lowestPt.canReshapeSup = lowestPt.canReshapeSup and actualPt.canReshapeSup
            lowestPt.alpha = (lowestPt.alpha + actualPt.alpha)/2.
            lowestPt.dd = (lowestPt.dd + actualPt.dd)/2.
            overlapExists = True
      return points

    def adjustExtremeShapes(projsToX, projsToY):
      for pt in projsToX:
        start = pt.start
        end = pt.end
        dxRomboid = abs(pt.dd/2./np.tan(theta))
        startRomboid = start + dxRomboid
        endRomboid = end - dxRomboid
        if greater(endRomboid, startRomboid):
          if pt.canReshapeInf:
            pt.start = self.kshape*start + (1. - self.kshape)*startRomboid
          if pt.canReshapeSup:
            pt.end = self.kshape*end + (1. - self.kshape)*endRomboid

      for pt in projsToY:
        start = pt.start
        end = pt.end
        dyRomboid = abs(pt.dd/2.*np.tan(theta))
        startRomboid = start + dyRomboid
        endRomboid = end - dyRomboid
        if greater(endRomboid, startRomboid):
          if pt.canReshapeInf:
            pt.start = self.kshape*start + (1. - self.kshape)*startRomboid
          if pt.canReshapeSup:
            pt.end = self.kshape*end + (1. - self.kshape)*endRomboid

      return projsToX, projsToY

    collectprojsToXY()      
    if not (projsToX or projsToY):
      return 1
 
    projsToX, projsToY = pruneAndSort()
    projsToX = pruneOverlaps(projsToX)
    projsToY = pruneOverlaps(projsToY)
    projsToX, projsToY = adjustExtremeShapes(projsToX, projsToY)

    deltax = 0
    for ptx in projsToX:
      deltax += (ptx.end - ptx.start)*(1 - ptx.alpha)
    xobstr = deltax*np.sin(theta)
    deltay = 0
    for pty in projsToY:
      deltay += pty.end - pty.start
    yobstr = deltay*np.cos(theta)

    totObstr = (xobstr + yobstr)/(lowresDx*np.sin(theta) + lowresDy*np.cos(theta))
    if self.obstrAlleviationEnabled and (totObstr < self.obstrAlleviationThreshold):
      obstrAlleviationFactor =\
           1. - (1. - self.obstrAlleviationParam)*totObstr**self.obstrAlleviationExp
    else:
      obstrAlleviationFactor = 1.

    alpha = 1. - totObstr*obstrAlleviationFactor
    assert greaterClose(alpha, 0), 'alpha must result greater than 0'
    return max(0, alpha)


