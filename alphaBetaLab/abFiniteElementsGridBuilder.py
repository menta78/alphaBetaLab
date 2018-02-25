import abGrid


class abFiniteElementsGridBuilder:

  def __init__(self, feMeshSpec, nParWorker=4):
    self.feMeshSpec = feMeshSpec
    self.nParWorker = nParWorker

  def buildGrid(self):
    nodeIds, cells = self.feMeshSpec.getCellPolygons(excludeLandBoundary=True,
                                                     excludeOpenBoundary=False)
    cellcrds = [(nid, 1) for nid in nodeIds]
    grd = abGrid.getLandSeaGrid(cells, cellcrds, nParWorker=self.nParWorker)
    grd.isRegular = False

    return grd


