import unittest
import numpy as np

from alphaBetaLab.abRectangularGridBuilder import abRectangularGridBuilder as grdBld
from alphaBetaLab import abUpstreamPolyEstimator as upe

class testAbUpstreamPolyEstimator(unittest.TestCase):

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
  
  def _findClosePoint(self, expPoint, pointList):
    for pt in pointList:
      if np.isclose(expPoint[0], pt[0]) and np.isclose(expPoint[1], pt[1]):
        return True
    return False 

  def test0radE(self):
    rectGridBld = grdBld(minX=1, minY=10, dx=1, dy=1, nx=3, ny=3, minXYIsCentroid=False)
    hrmtx = self.getMockHiResAlphaMtxAndCstCellDet()
    coastalCellDetector = self.getMockHiResAlphaMtxAndCstCellDet()
    grd = rectGridBld.buildGrid(hrmtx, coastalCellDetector)
    cell = grd.cells[4] # the central cell

    neighTotPoly = grd.cells[0]
    for p in grd.cells[1:]:
      if p != cell:
        neighTotPoly = neighTotPoly.union(p)
    theta = 0
    
    upl = upe.getUpstreamPoly(cell, neighTotPoly, theta)
    uplcrds = upl.boundary.coords[:]
    expuplcrds = [(2.0, 11.0), (1.0, 11.0), (1.0, 12.0), (2.0, 12.0), (2.0, 11.0)]
    self.assertEqual(len(expuplcrds), len(uplcrds))
    for ecrd in expuplcrds:
      self._findClosePoint(ecrd, uplcrds)
  
  def test30degE(self):
    rectGridBld = grdBld(minX=1, minY=10, dx=1, dy=1, nx=3, ny=3, minXYIsCentroid=False)
    hrmtx = self.getMockHiResAlphaMtxAndCstCellDet()
    coastalCellDetector = self.getMockHiResAlphaMtxAndCstCellDet()
    grd = rectGridBld.buildGrid(hrmtx, coastalCellDetector)
    cell = grd.cells[4] # the central cell

    neighTotPoly = grd.cells[0]
    for p in grd.cells[1:]:
      if p != cell:
        neighTotPoly = neighTotPoly.union(p)
    theta = np.pi/6
    
    upl = upe.getUpstreamPoly(cell, neighTotPoly, theta)
    uplcrds = upl.boundary.coords[:]
    expuplcrds = [(1.0, 11.422649730810376), (2.0, 12.0), (2.0, 11.0),\
                  (3.0, 11.0), (1.2679491924311213, 10.0), (1.0, 10.0), (1.0, 11.0),\
                  (1.0, 11.422649730810376)]
    self.assertEqual(len(expuplcrds), len(uplcrds))
    for ecrd in expuplcrds:
      self._findClosePoint(ecrd, uplcrds)
  
  def test120degE(self):
    rectGridBld = grdBld(minX=1, minY=10, dx=1, dy=1, nx=3, ny=3, minXYIsCentroid=False)
    hrmtx = self.getMockHiResAlphaMtxAndCstCellDet()
    coastalCellDetector = self.getMockHiResAlphaMtxAndCstCellDet()
    grd = rectGridBld.buildGrid(hrmtx, coastalCellDetector)
    cell = grd.cells[4] # the central cell

    neighTotPoly = grd.cells[0]
    for p in grd.cells[1:]:
      if p != cell:
        neighTotPoly = neighTotPoly.union(p)
    theta = np.pi*4./6.
    
    upl = upe.getUpstreamPoly(cell, neighTotPoly, theta)
    uplcrds = upl.boundary.coords[:]
    expuplcrds = [(2.577350269189625, 10.0), (2.0, 11.0), (3.0, 11.0),\
                  (3.0, 12.0), (4.0, 10.26794919243112), (4.0, 10.0), (3.0, 10.0),\
                  (2.577350269189625, 10.0)]
    self.assertEqual(len(expuplcrds), len(uplcrds))
    for ecrd in expuplcrds:
      self._findClosePoint(ecrd, uplcrds)
  
  def test_45degE(self):
    rectGridBld = grdBld(minX=1, minY=10, dx=1, dy=1, nx=3, ny=3, minXYIsCentroid=False)
    hrmtx = self.getMockHiResAlphaMtxAndCstCellDet()
    coastalCellDetector = self.getMockHiResAlphaMtxAndCstCellDet()
    grd = rectGridBld.buildGrid(hrmtx, coastalCellDetector)
    cell = grd.cells[4] # the central cell

    neighTotPoly = grd.cells[0]
    for p in grd.cells[1:]:
      if p != cell:
        neighTotPoly = neighTotPoly.union(p)
    theta = -np.pi*1./4.
    
    upl = upe.getUpstreamPoly(cell, neighTotPoly, theta)
    uplcrds = upl.boundary.coords[:]
    expuplcrds = [(2.0, 11.0), (1.0, 12.0), (1.0, 13.0), (2.0, 13.0),\
                  (3.0, 12.0), (2.0, 12.0), (2.0, 11.0)]
    self.assertEqual(len(expuplcrds), len(uplcrds))
    for ecrd in expuplcrds:
      self._findClosePoint(ecrd, uplcrds)
    
    
    

if __name__ == '__main__':
  unittest.main()

