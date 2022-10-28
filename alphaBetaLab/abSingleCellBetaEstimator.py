import numpy as np
from shapely import geometry as g

from . import abUtils as abutls
from .abFirstOctantTransformation import abFirstOctantTransformation
from .abSingleCellAlphaEstimator import abSingleCellAlphaEstimator
from . import abAlphaBetaRecalibrator

debugPlots = False
thetaTolerance = .0001
defaultKShape = 1.

class abSingleCellBetaEstimator:

  def __init__(self, polygon, alphaMtx, kshape = -1, recalibFactor = 1., maxSubSections = 10):
    """
    abSingleCellBetaEstimator: estimates the local average beta for the given polygon,
    on the basis of the high resolution alpha matrix given by alphaMtx.
    """
    self.polygon = polygon
    if alphaMtx.polygon == polygon:
      self.alphaMtx = alphaMtx
    else:
      self.alphaMtx = alphaMtx.getAlphaSubMatrix(polygon)
    self.kshape = kshape if (kshape != -1) else defaultKShape; 
    self.obstrAlleviationEnabled = False
    self.maxSubSections = maxSubSections
    self.recalib = abAlphaBetaRecalibrator.abAlphaBetaRecalibrator(obstFactor = recalibFactor)
  
  def computeBeta(self, direction, frequency):
    if not self.alphaMtx.empty():
      firstOctTransf = abFirstOctantTransformation(self.alphaMtx, self.polygon)
      theta, alphaMtx, lowResCell = firstOctTransf.transform(direction)

      if debugPlots:
        import abHighResAlphaMatrixPlot as pp
        pp.plotHiResAlphaMtx('orig. mtx/poly/theta', self.alphaMtx, direction)
        pp.plotHiResAlphaMtxAndShow('rot. mtx/poly/theta', alphaMtx, theta)
  
      b = self._getBetaFirstOctant(theta, frequency, alphaMtx, lowResCell)
      b = self.recalib.recalibrate(b)
      return b
    else:
      return 1

  def _getBetaFirstOctant(self, theta, frequency, alphaMtx, lowResCell):
    """
    theta must be <= pi/4
    alphaMtx must be referred to the first octant.
    """

    def catValueToArrayIfOutside(array, val):
      minarr, maxarr = np.min(array), np.max(array)
      valGtArray = (val > array).all() and not abutls.isClose(val, maxarr)
      valLtArray = (val < array).all() and not abutls.isClose(val, minarr)
      
      if not (valGtArray or valLtArray):
        return array

      ornt = np.sign(array[-1] - array[0])
      compr = 1 if valGtArray else -1
      pos = ornt*compr

      if pos == 1.:
        return np.concatenate((array, np.array([val])))
      else:
        return np.concatenate((np.array([val]), array))
        

    if len(alphaMtx.alphas.shape) < 2:
      return 1
    normTheta = theta + np.pi/2.
    normSlope = np.tan(normTheta) if not abutls.isClose(theta, 0, thetaTolerance) else np.nan

    cell = alphaMtx.polygon 
    try:
      crds = list(cell.boundary.coords)
    except:
      # skipping the computation for strange geometries without coordinate sequence
      return 1
    cellxs = np.array([p[0] for p in crds])
    cellys = np.array([p[1] for p in crds])

    #getting y coords and extending them to cover the whole cell
    ys = alphaMtx.ys[:]
    ys = catValueToArrayIfOutside(ys, max(cellys))
    ys = catValueToArrayIfOutside(ys, min(cellys))
    miny = min(ys)
    maxy = max(ys)

    #getting x coords and extending them 
    #so that trasverse polygons can cover the whole cell
    xs = alphaMtx.xs[:]
    xs = catValueToArrayIfOutside(xs, min(cellxs))
    dx = abs(xs[-1] - xs[-2] if len(xs) else max(cellxs) - min(cellxs))
    if not np.isnan(normSlope):
      #normslope should be never 0
      polyxproj = cellxs + (miny - cellys)/normSlope
      subpolymaxx = max(polyxproj)
      mxxxs = max(xs)
      while mxxxs < subpolymaxx:
        mxxxs = min(mxxxs + dx, subpolymaxx)
        xs = catValueToArrayIfOutside(xs, mxxxs)
    elif max(xs) < max(cellxs):
      xs = np.concatenate((xs, np.array([max(cellxs)])))

    minx = min(xs)
    maxx = max(xs)
    alphas = []
    dys = []
    
    def getPolygonDY(pl):
      crds = list(pl.boundary.coords)
      plxs = np.array([c[0] for c in crds])
      plys = np.array([c[1] for c in crds])
      plprojy = plys + (maxx - plxs)*np.tan(theta) 
      dy = max(plprojy) - min(plprojy)
      return dy

    #looping on the trasverse polygons
    lminx = min(xs)
    lmaxx = max(xs)
    lenx = min(len(xs), self.maxSubSections)
    #guaranteeing that xs are equally spaced
    prevsubcell = None
    loopxs = np.linspace(lminx, lmaxx, lenx)
    loopxs = loopxs[loopxs > min(loopxs)]
    for x in loopxs:
      if not np.isnan(normSlope):
        #normSlope is negative
        y = miny - normSlope*(x - minx)
        pxs = [minx, x, minx, minx]
        pys = [miny, miny, y, miny]
      else:
        pxs = [minx, x, x, minx, minx]
        pys = [miny, miny, maxy, maxy, miny]
      pxy = [p for p in zip(pxs, pys)]
      poly = g.Polygon(pxy)
      subcell = cell.intersection(poly)
      if abutls.isClose(subcell.area, 0.) or (prevsubcell and abutls.isClose(prevsubcell.area, subcell.area)):
        #the trasverse polygon does not cross the cell yet
        continue
      if subcell.__class__ == g.Polygon:
        #the intersection between the trasverse polygon and the cell
        #is a polygon. Computing the alpha
        alphaEst = abSingleCellAlphaEstimator(subcell, alphaMtx, kshape = self.kshape, recalibFactor = 1)
        alphaEst.obstrAlleviationEnabled = self.obstrAlleviationEnabled
        alpha = alphaEst.computeAlpha(theta, frequency)
        totDy = getPolygonDY(subcell)
      elif subcell.__class__ in [g.GeometryCollection, g.MultiPolygon]:
        #the intersection between the trasverse polygon and the cell
        #is a collection of polygons (possible for concave cells). 
        #Computing the alpha for each subpolygon, and 
        #weight-averaging to compute the overall alpha
        totDy = 0
        if isinstance(subcell, g.MultiPolygon):
          cellitr = subcell.geoms
        else:
          cellitr = subcell
        plobstrs = []
        pldys = []
        for pl in cellitr:
          if pl.__class__ == g.Polygon:
            alphaEst = abSingleCellAlphaEstimator(pl, alphaMtx, kshape = self.kshape)
            alphaEst.obstrAlleviationEnabled = self.obstrAlleviationEnabled
            palpha = alphaEst.computeAlpha(theta, frequency) 
            dy = getPolygonDY(pl)
            plobstrs.append(1 - palpha)
            pldys.append(dy)
            totDy += dy
        plobstrs = np.array(plobstrs)
        pldys = np.array(pldys)
        totobstr = sum(plobstrs*pldys)/sum(pldys)
        alpha = 1 - totobstr
      else:
        raise TypeError('Unsupported geometry object: ' + str(subcell.__class__))
      alphas.append(alpha)
      dys.append(totDy)
      prevsubcell = subcell
    alphas = np.array(alphas)
    #weighting to the width or to dys is the same thing
    widths = np.array(dys)
    avgWidth = np.mean(widths)
    weights = widths[:]
    weights[weights > avgWidth] = avgWidth
    beta = np.sum(alphas*weights)/np.sum(weights)
    return beta


 
