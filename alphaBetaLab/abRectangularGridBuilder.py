import numpy as np
import shapely.geometry as gm
from . import abGrid

class abRectangularGridBuilder:
   
  def __init__(self, minX=0, minY=0, dx=0, dy=0, nx=0, ny=0, mask=None, minXYIsCentroid=True, nParWorker=4):
    """
    abRegularGridBuilder: object building a abGrid instance for 
    a regular grid.
    """
    self.minX = minX
    self.minY = minY
    self.dx = dx
    self.dy = dy
    self.nx = nx
    self.ny = ny
    self.mask = mask if (not mask is None) else np.ones((ny, nx))
    self.minXYIsCentroid = minXYIsCentroid
    self.nParWorker = nParWorker

  def buildGrid(self, hiResAlphaMtx, coastalCellDetector):
    crds = []
    cells = []
    dx = self.dx
    dy = self.dy
    if self.minXYIsCentroid:
      minX = self.minX - dx/2. #minX and minY refer to the centroid
      minY = self.minY - dy/2.
    else:
      minX, minY = self.minX, self.minY
    mask = self.mask
    for ix in range(self.nx):
      for iy in range(self.ny):
        if mask[iy, ix] != 1:
          continue
        ptx = minX + ix*dx
        pty = minY + iy*dy
        ext = [[ptx, pty], [ptx + dx, pty], [ptx + dx, pty + dy], [ptx, pty + dy]]
        cell = gm.Polygon(ext)
        cells.append(cell)
        crds.append([ix, iy])
    cells = gm.MultiPolygon(cells)
    crds = np.array(crds)

    if not coastalCellDetector is None: 
      grd = abGrid.getSeaGrid(cells, crds, hiResAlphaMtx, coastalCellDetector, 
               nParWorker=self.nParWorker)
    else:
      grd = abGrid.getLandSeaGrid(cells, crds, nParWorker=self.nParWorker)

    grd.isRegular = True
    grd.minX = minX
    grd.minY = minY
    grd.dx = self.dx
    grd.dy = self.dy
    grd.nx = self.nx
    grd.ny = self.ny
    return grd


