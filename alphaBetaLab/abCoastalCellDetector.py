import numpy as np
from shapely import geometry as g
from . import abFixBasemap
from mpl_toolkits import basemap
from .abOptionManager import getOption


class abCoastalCellDetector:

  def __init__(self, options):
    """
    A coastal cell is a cell that lays partly on the coasts of large land bodies.
    In these cells the parameterization of the unresolved obstacles conflicts with
    the shallow water source terms. Therefore it is useful to detect these cells
    and turn off the parameterization of the unresolved obstacles.
    By default a cell is considered coastal if it has more that 20% of its surface on large land bodies
    (the threshold can be parameterized).
    TODO: make the comparisons between sizes and surfaces in m, not in degrees
    """
    self.coveredSurfaceThresholdRatio = getOption(options, 'coveredSurfaceThresholdRatio', .1)
    self.coveredSurfaceThresholdRatioSmallBodies = getOption(options, 'coveredSurfaceThresholdRatioSmallBodies', .5)
    self.coarseCoastlineResolution = getOption(options, 'coarseCoastlineResolution', 'c')
    self.smallBodiesSizeRatio = getOption(options, 'smallBodiesSizeRatio', 10)
    self._loadDataStructure()

  def _loadDataStructure(self):
    mp = basemap.Basemap(resolution = self.coarseCoastlineResolution)
    cstPls = mp.coastpolygons
    self.cstPls = cstPls
    cstGPls = []
    cstPlBnds = []
    cstPlSfc = []
    for pl in cstPls:
      xs = pl[0]
      ys = pl[1]
      pts = [c for c in zip(xs, ys)]
      gpl = g.Polygon(pts)
      cstGPls.append(gpl)
      cstPlBnds.append(gpl.boundary)
      cstPlSfc.append(gpl.area)
    self.cstGPls = cstGPls
    self.cstPlBnds = cstPlBnds
    self.cstPlSfc = cstPlSfc
    
  def isCoastalCell(self, cellPolygon, cellPolygonBoundary=None, cellSurface=-1, cellCentroid=None):
    cstPlBnds = self.cstPlBnds
    cstGPls = self.cstGPls    
    cstPlSfc = self.cstPlSfc
    coveredSurfaceThresholdRatio = self.coveredSurfaceThresholdRatio
    coveredSurfaceThresholdRatioSmallBodies = self.coveredSurfaceThresholdRatioSmallBodies
    smallBodiesSizeRatio = self.smallBodiesSizeRatio

    cellPolygonBoundary = cellPolygon.boundary if cellPolygonBoundary is None else g.LineString(cellPolygonBoundary)
    cellSurface = cellPolygon.area if cellSurface == -1 else cellSurface
    cellCentroid = cellPolygon.centroid if cellCentroid is None else cellCentroid
    cellRadius = np.sqrt(cellSurface/np.pi) # approximating as a circle
    surfThreshold = cellSurface*coveredSurfaceThresholdRatio
    surfThresholdSmallBodies = cellSurface*coveredSurfaceThresholdRatioSmallBodies

    result = False
    distFromClosestLargeLand = np.inf
    intsSurf = 0
    npl = len(cstPlBnds)
    for ipl in range(npl):
      plbnd = cstPlBnds[ipl]
      plsfc = cstPlSfc[ipl]
      pl = cstGPls[ipl]
      if plsfc >= cellSurface*smallBodiesSizeRatio:
        actDist = pl.distance(cellCentroid)
        distFromClosestLargeLand = np.min([distFromClosestLargeLand, actDist])
      if cellPolygonBoundary.intersects(plbnd):
        ints = cellPolygon.intersection(pl)
        intsSurf += ints.area
        if cellSurface >= plsfc/2.:
          # if the body is very small, treating it as an unresolved obstacle
          continue
        elif (cellSurface >= plsfc/smallBodiesSizeRatio):
          # high max land fraction of the cell, if it intersects a small body
          if intsSurf >= surfThresholdSmallBodies:
            return True
        elif (cellSurface < plsfc) and (intsSurf >= surfThreshold):
          # low max land fraction of the cell, if it intersects a large body
          return True
    return distFromClosestLargeLand <= cellRadius

      
    
  
    

