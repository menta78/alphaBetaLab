import unittest
import shapely.geometry as gm

from alphaBetaLab.abRectangularGridBuilder import abRectangularGridBuilder

class testAbRectangularGridBuilder(unittest.TestCase):

  def getMockHiResAlphaMtxAndCstCellDet(self, posCellCentroids = None):
    class _mockClass:
      def __init__(self, posCellCentroids):
        self.posCellCentroids = posCellCentroids
        self.cell = None
      def getAlphaSubMatrix(self, cell):
        sm = _mockClass(self.posCellCentroids)
        sm.cell = cell
        return sm
      def _positive(self, cell):
        cntrs = self.posCellCentroids
        if cell is None or cntrs is None:
          return False
        else:
          for c in cntrs:
            if cell.contains(gm.Point([c[0], c[1]])):
              return True
          return False
      def onLand(self):
        cell = self.cell
        return self._positive(cell)
      def isCoastalCell(self, cell, boundary = None, surface = -1):
        return self._positive(cell)
    return _mockClass(posCellCentroids)


  def testGetSeaGridSerial(self):
    minx = 100.
    miny = 45.
    dx = .5
    dy = 1.
    nx = 30
    ny = 10
    maxx = minx + nx*dx
    maxy = miny + ny*dy
    landCntrs = [[100.25, 45.25], [105.25, 47.25]]
    coastCntrs = [[100.75, 45.25], [105.25, 47.25]]
    gb = abRectangularGridBuilder(minx, miny, dx, dy, nx, ny, 
              wrapAroundDateline=False, nParWorker=1, minXYIsCentroid=False)
    hiResMtx = self.getMockHiResAlphaMtxAndCstCellDet(landCntrs)
    cstClDet = self.getMockHiResAlphaMtxAndCstCellDet(coastCntrs)
    grd = gb.buildGrid(hiResMtx, cstClDet)
    self.assertEqual(1, grd.nParWorker)
    cells = grd.cells
    self.assertEqual(nx*ny - 3, len(cells))


  def testGetSeaGridParallel(self):
    minx = 100.
    miny = 45.
    dx = .5
    dy = 1.
    nx = 30
    ny = 10
    maxx = minx + nx*dx
    maxy = miny + ny*dy
    landCntrs = [[100.25, 45.25], [105.25, 47.25]]
    coastCntrs = [[100.75, 45.25], [105.25, 47.25]]
    gb = abRectangularGridBuilder(minx, miny, dx, dy, nx, ny, nParWorker=4, minXYIsCentroid=False)
    hiResMtx = self.getMockHiResAlphaMtxAndCstCellDet(landCntrs)
    cstClDet = self.getMockHiResAlphaMtxAndCstCellDet(coastCntrs)
    grd = gb.buildGrid(hiResMtx, cstClDet)
    self.assertEqual(4, grd.nParWorker)
    cells = grd.cells
    self.assertEqual(nx*ny - 3, len(cells))
    

  def testGetNeighborsSerial(self):
    minx = 100.
    miny = 45.
    dx = .5
    dy = 1.
    nx = 30
    ny = 10
    maxx = minx + nx*dx
    maxy = miny + ny*dy
    gb = abRectangularGridBuilder(minx, miny, dx, dy, nx, ny, nParWorker = 1)
    hiResMtx = self.getMockHiResAlphaMtxAndCstCellDet()
    cstClDet = self.getMockHiResAlphaMtxAndCstCellDet()
    grd = gb.buildGrid(hiResMtx, cstClDet)
    grd.nParWorker = 1
    cells = grd.cells

    cell = cells[0]
    ncls = grd.getNeighbors(cell)
    self.assertEqual(3, len(ncls))
    for nc in ncls:
      self.assertTrue( cell.distance(nc) < .000000001 )

    cell = cells[45]
    ncls = grd.getNeighbors(cell)
    self.assertEqual(8, len(ncls))
    for nc in ncls:
      self.assertTrue( cell.distance(nc) < .000000001 )

    cell = cells[100]
    ncls = grd.getNeighbors(cell)
    self.assertEqual(5, len(ncls))
    for nc in ncls:
      self.assertTrue( cell.distance(nc) < .000000001 )
    

  def testGetNeighborsWrapAround0Serial(self):
    """
    like previous test. the wrapAroundDataline param is true,
    but should do nothing
    """
    minx = 100.
    miny = 45.
    dx = .5
    dy = 1.
    nx = 30
    ny = 10
    maxx = minx + nx*dx
    maxy = miny + ny*dy
    gb = abRectangularGridBuilder(minx, miny, dx, dy, nx, ny, wrapAroundDateline=True, nParWorker = 1)
    hiResMtx = self.getMockHiResAlphaMtxAndCstCellDet()
    cstClDet = self.getMockHiResAlphaMtxAndCstCellDet()
    grd = gb.buildGrid(hiResMtx, cstClDet)
    grd.nParWorker = 1
    cells = grd.cells

    cell = cells[0]
    ncls = grd.getNeighbors(cell)
    self.assertEqual(3, len(ncls))
    for nc in ncls:
      self.assertTrue( cell.distance(nc) < .000000001 )

    cell = cells[45]
    ncls = grd.getNeighbors(cell)
    self.assertEqual(8, len(ncls))
    for nc in ncls:
      self.assertTrue( cell.distance(nc) < .000000001 )

    cell = cells[100]
    ncls = grd.getNeighbors(cell)
    self.assertEqual(5, len(ncls))
    for nc in ncls:
      self.assertTrue( cell.distance(nc) < .000000001 )
    

  def testGetNeighborsWrapAroundGlobalParallel(self):
    minx = -179.
    miny = -89.
    dx = 2
    dy = 2
    nx = 180
    ny = 90
    maxx = minx + nx*dx
    maxy = miny + ny*dy
    gb = abRectangularGridBuilder(minx, miny, dx, dy, nx, ny, wrapAroundDateline=True, nParWorker = 4)
    hiResMtx = self.getMockHiResAlphaMtxAndCstCellDet()
    cstClDet = self.getMockHiResAlphaMtxAndCstCellDet()
    grd = gb.buildGrid(hiResMtx, cstClDet)
    cells = grd.cells

    cell = cells[0]
    ncls = grd.getNeighbors(cell)
    self.assertEqual(5, len(ncls))
    for nc in ncls:
      self.assertTrue( cell.distance(nc) < .000000001 )
    self.assertEqual(-182, ncls[3].boundary.coords[0][0])
    self.assertEqual(-182, ncls[4].boundary.coords[0][0])

    cell = cells[45]
    ncls = grd.getNeighbors(cell)
    self.assertEqual(8, len(ncls))
    for nc in ncls:
      self.assertTrue( cell.distance(nc) < .000000001 )
    self.assertEqual(-182, ncls[5].boundary.coords[0][0])
    self.assertEqual(-182, ncls[6].boundary.coords[0][0])
    self.assertEqual(-182, ncls[6].boundary.coords[0][0])

    cell = cells[65]
    ncls = grd.getNeighbors(cell)
    self.assertEqual(8, len(ncls))
    for nc in ncls:
      self.assertTrue( cell.distance(nc) < .000000001 )
    self.assertEqual(-182, ncls[5].boundary.coords[0][0])
    self.assertEqual(-182, ncls[6].boundary.coords[0][0])
    self.assertEqual(-182, ncls[6].boundary.coords[0][0])

    cell = cells[89]
    ncls = grd.getNeighbors(cell)
    self.assertEqual(5, len(ncls))
    for nc in ncls:
      self.assertTrue( cell.distance(nc) < .000000001 )
    self.assertEqual(-182, ncls[3].boundary.coords[0][0])
    self.assertEqual(-182, ncls[4].boundary.coords[0][0])

    cell = cells[200]
    ncls = grd.getNeighbors(cell)
    self.assertEqual(8, len(ncls))
    for nc in ncls:
      self.assertTrue( cell.distance(nc) < .000000001 )

    cell = cells[nx*ny-22]
    ncls = grd.getNeighbors(cell)
    self.assertEqual(8, len(ncls))
    for nc in ncls:
      self.assertTrue( cell.distance(nc) < .000000001 )
    self.assertEqual(182, ncls[5].boundary.coords[1][0])
    self.assertEqual(182, ncls[6].boundary.coords[1][0])
    self.assertEqual(182, ncls[6].boundary.coords[1][0])

    cell = cells[nx*ny-1]
    ncls = grd.getNeighbors(cell)
    self.assertEqual(5, len(ncls))
    for nc in ncls:
      self.assertTrue( cell.distance(nc) < .000000001 )
    self.assertEqual(182, ncls[3].boundary.coords[1][0])
    self.assertEqual(182, ncls[4].boundary.coords[1][0])


  def testGetNeighborsParallel(self):
    minx = 100.
    miny = 45.
    dx = .5
    dy = 1.
    nx = 30
    ny = 10
    maxx = minx + nx*dx
    maxy = miny + ny*dy
    gb = abRectangularGridBuilder(minx, miny, dx, dy, nx, ny, nParWorker = 4)
    hiResMtx = self.getMockHiResAlphaMtxAndCstCellDet()
    cstClDet = self.getMockHiResAlphaMtxAndCstCellDet()
    grd = gb.buildGrid(hiResMtx, cstClDet)
    grd.nParWorker = 4
    cells = grd.cells

    cell = cells[0]
    ncls = grd.getNeighbors(cell)
    self.assertEqual(3, len(ncls))
    for nc in ncls:
      self.assertTrue( cell.distance(nc) < .000000001 )

    cell = cells[45]
    ncls = grd.getNeighbors(cell)
    self.assertEqual(8, len(ncls))
    for nc in ncls:
      self.assertTrue( cell.distance(nc) < .000000001 )

    cell = cells[100]
    ncls = grd.getNeighbors(cell)
    self.assertEqual(5, len(ncls))
    for nc in ncls:
      self.assertTrue( cell.distance(nc) < .000000001 )
    
    
    
if __name__ == '__main__':
  unittest.main()

