import abGrid


class abRectangularGridBuilder:

  def __init__(self, feMeshSpec, nParWorker=4):
    self.feMeshSpec = feMeshSpec
    self.nParWorker = nParWorker

  def buildGrid(self):
    nodeIds, cells = self.feMeshSpec.getCellPolygons(excludeLandBoundary=True)
    cellcrds = [(nid - 1, 0) for nid in nodeIds]
    grd = abGrid.getLandSeaGrid(cells, cellcrds, nParWorker=self.nParWorker)
    grd.isRegular = False

    return grd


