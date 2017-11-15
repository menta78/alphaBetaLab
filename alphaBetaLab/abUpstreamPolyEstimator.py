import numpy as np
import shapely.geometry as gm

def getUpstreamPoly(cellPoly, neighborhoodPoly, direction):
  """
  getUpstreamPoly: computes the upstream polygon from:
  the current cell, the neighborhood polygon, i.e. the 
  polygon composed by the joined cells, current cell + neighbour cells.
  """
  direction = direction + np.pi
  # projecting cellPoly upstream along direction,
  # of a distance equal to the diagonal of the rectangular envelope 
  # of neighborhoodPoly. 
  cellVtxs = list(cellPoly.exterior.coords)
  neighPolyEnvlp = neighborhoodPoly.envelope
  diag1, diag2 = neighPolyEnvlp.boundary.coords[0], neighPolyEnvlp.boundary.coords[2]
  diag = ((diag2[0] - diag1[0])**2. + (diag2[1] - diag1[1])**2.)**.5
  ejectdx = 2*diag*np.cos(direction)
  ejectdy = 2*diag*np.sin(direction)
  ejectedCellVtxs = [gm.Point(c[0] + ejectdx, c[1] + ejectdy) for c in cellVtxs]
  extendedPolyPts = []
  extendedPolyPts.extend(cellVtxs)
  extendedPolyPts.extend(ejectedCellVtxs)
  extendedPolyLine = gm.LineString(extendedPolyPts)
  # extendedPoly covers, cellPoly and its projection upstream
  # covering the whole neighborhoodPoly and beyond.
  extendedPoly = extendedPolyLine.convex_hull
  # wholeUpstrPoly covers, cellPoly and its projection upstream
  # covering the whole neighborhoodPoly, not beyond.
  wholeUpstrPoly = extendedPoly.intersection(neighborhoodPoly)
  
  upstrPoly = wholeUpstrPoly - cellPoly
  
  return upstrPoly

