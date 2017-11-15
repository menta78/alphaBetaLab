import unittest
import shapely.geometry as gm

from abRectangularGridBuilder import abRectangularGridBuilder

class testAbRectangularGridBuilder(unittest.TestCase):

  def getMockHiResAlphaMtxAndCstCellDet(self):
    class _mockClass:
      def onLand(self):
        return False
      def getAlphaSubMatrix(self, cell):
        sm = _mockClass()
        sm.cell = cell
        return sm
      def isCoastalCell(self, cell, boundary = None, surface = -1):
        return False
    return _mockClass()

  def test0(self):
    minx = 100.
    miny = 45.
    dx = .5
    dy = 1.
    nx = 30
    ny = 10
    maxx = minx + nx*dx
    maxy = miny + ny*dy
    gb = abRectangularGridBuilder(minx, miny, dx, dy, nx, ny, minXYIsCentroid=False)
    hiResAlphaMtx = self.getMockHiResAlphaMtxAndCstCellDet()
    coastalCellDetector = self.getMockHiResAlphaMtxAndCstCellDet()
    grd = gb.buildGrid(hiResAlphaMtx, coastalCellDetector)
    self.assertIsNotNone(grd)
    self.assertIsNotNone(grd.cells)
    self.assertIsNotNone(grd.cellCoordinates)
    cells = grd.cells
    grdbndr = gm.MultiPolygon(cells).convex_hull.envelope.boundary.coords
    self.assertTrue((minx, miny) in grdbndr)
    self.assertTrue((maxx, miny) in grdbndr)
    self.assertTrue((maxx, maxy) in grdbndr)
    self.assertTrue((minx, maxy) in grdbndr)
    self.assertEqual(nx*ny, len(cells))
    crds = [(a[0], a[1]) for a in grd.cellCoordinates]
    self.assertEqual(nx*ny, len(crds))
    for ix in range(nx):
      for iy in range(ny):
        pl = gm.Polygon([\
              [minx + ix*dx, miny + iy*dy], [minx + (ix + 1)*dx, miny + iy*dy],\
              [minx + (ix + 1)*dx, miny + (iy + 1)*dy], [minx + ix*dx, miny + (iy + 1)*dy]])
        self.assertTrue(pl in cells)
        self.assertTrue((ix, iy) in crds)

  def testMinXYIsCentroid(self):
    minx = 100.
    miny = 45.
    dx = .5
    dy = 1.
    nx = 30
    ny = 10
    maxx = minx + nx*dx
    maxy = miny + ny*dy
    gb = abRectangularGridBuilder(minx + dx/2., miny + dy/2., 
                          dx, dy, nx, ny, minXYIsCentroid=True)
    hiResAlphaMtx = self.getMockHiResAlphaMtxAndCstCellDet()
    coastalCellDetector = self.getMockHiResAlphaMtxAndCstCellDet()
    grd = gb.buildGrid(hiResAlphaMtx, coastalCellDetector)
    self.assertIsNotNone(grd)
    self.assertIsNotNone(grd.cells)
    self.assertIsNotNone(grd.cellCoordinates)
    cells = grd.cells
    grdbndr = gm.MultiPolygon(cells).convex_hull.envelope.boundary.coords
    self.assertTrue((minx, miny) in grdbndr)
    self.assertTrue((maxx, miny) in grdbndr)
    self.assertTrue((maxx, maxy) in grdbndr)
    self.assertTrue((minx, maxy) in grdbndr)
    self.assertEqual(nx*ny, len(cells))
    crds = [(a[0], a[1]) for a in grd.cellCoordinates]
    self.assertEqual(nx*ny, len(crds))
    for ix in range(nx):
      for iy in range(ny):
        pl = gm.Polygon([\
              [minx + ix*dx, miny + iy*dy], [minx + (ix + 1)*dx, miny + iy*dy],\
              [minx + (ix + 1)*dx, miny + (iy + 1)*dy], [minx + ix*dx, miny + (iy + 1)*dy]])
        self.assertTrue(pl in cells)
        self.assertTrue((ix, iy) in crds)
    
    
if __name__ == '__main__':
  unittest.main()

