from mpl_toolkits import basemap
from shapely import geometry as g
from itertools import izip
from abOptionManager import getOption


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
      pts = [c for c in izip(xs, ys)]
      gpl = g.Polygon(pts)
      cstGPls.append(gpl)
      cstPlBnds.append(gpl.boundary)
      cstPlSfc.append(gpl.area)
    self.cstGPls = cstGPls
    self.cstPlBnds = cstPlBnds
    self.cstPlSfc = cstPlSfc
    
  def isCoastalCell(self, cellPolygon, cellPolygonBoundary = None, cellSurface = -1):
    cstPlBnds = self.cstPlBnds
    cstGPls = self.cstGPls    
    cstPlSfc = self.cstPlSfc
    coveredSurfaceThresholdRatio = self.coveredSurfaceThresholdRatio
    coveredSurfaceThresholdRatioSmallBodies = self.coveredSurfaceThresholdRatioSmallBodies
    smallBodiesSizeRatio = self.smallBodiesSizeRatio

    cellPolygonBoundary = cellPolygon.boundary if cellPolygonBoundary is None else g.LineString(cellPolygonBoundary)
    cellSurface = cellPolygon.area if cellSurface == -1 else cellSurface
    surfThreshold = cellSurface*coveredSurfaceThresholdRatio
    surfThresholdSmallBodies = cellSurface*coveredSurfaceThresholdRatioSmallBodies

    result = False
    intsSurf = 0
    npl = len(cstPlBnds)
    for ipl in range(npl):
      plbnd = cstPlBnds[ipl]
      plsfc = cstPlSfc[ipl]
      if cellPolygonBoundary.intersects(plbnd):
        pl = cstGPls[ipl]
        ints = cellPolygon.intersection(pl)
        intsSurf += ints.area
        if cellSurface >= plsfc/2.:
          # if the body is very small, treating it as an unresolved obstacle
          continue
        elif (cellSurface >= plsfc/smallBodiesSizeRatio):
          # high max land fraction of the cell, if it intersects a small body
          return intsSurf >= surfThresholdSmallBodies
        elif (cellSurface < plsfc) and (intsSurf >= surfThreshold):
          # low max land fraction of the cell, if it intersects a large body
          return True
    return result

      
    
  
    

