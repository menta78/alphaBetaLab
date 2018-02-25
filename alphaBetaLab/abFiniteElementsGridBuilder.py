import abGrid


class abFiniteElementsGridBuilder:

  def __init__(self, feMeshSpec, nParWorker=4):
    self.feMeshSpec = feMeshSpec
    self.nParWorker = nParWorker

  def buildGrid(self):
    fem = self.feMeshSpec
    nodeIds, cells = fem.getCellPolygons(excludeLandBoundary=True,
                                         excludeOpenBoundary=False)
    cellcrds = [(nid, 1) for nid in nodeIds]
    centroids = [fem.nodes[nid] for nid in nodeIds]
    grd = abGrid.getLandSeaGrid(cells, cellcrds, centroids=centroids, nParWorker=self.nParWorker)
    grd.isRegular = False

    return grd


