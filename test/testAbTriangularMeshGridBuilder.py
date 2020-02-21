import unittest
import os
import numpy as np
from shapely import geometry as g

from alphaBetaLab import abTriangularMesh
from alphaBetaLab.abTriangularMeshGridBuilder import abTriangularMeshGridBuilder


class testAbFiniteElementsGridBuilder(unittest.TestCase):

   
  def testBuildGrid(self):
    mdldir = os.path.dirname( os.path.abspath(__file__) )
    mshFilePath = os.path.join(mdldir, 'triangularMeshTest/hgridGiamaica.gr3')
    etopoFilePath = os.path.join(mdldir, 'etopo1_testGiamaica.nc')
    feMeshSpec = abTriangularMesh.loadFromGr3File(mshFilePath)
    nodeIds, cellPly = feMeshSpec.getCellPolygons(excludeLandBoundary=True,
                                                  excludeOpenBoundary=False)
    grdBuilder = abTriangularMeshGridBuilder(feMeshSpec)
    grd = grdBuilder.buildGrid()
    self.assertFalse(grd.isRegular)
    self.assertFalse(grd.wrapAroundDateline)
    self.assertEqual(362, len(grd.cellCoordinates))
    self.assertEqual(362, len(grd.cells))
    self.assertEqual(362, len(grd.centroids))
    for crd, cp, cntr in zip(grd.cellCoordinates, grd.cells, grd.centroids):
      nid = crd[0] + 1
      self.assertEqual(0, crd[1])
      ndptcrds = feMeshSpec.nodes[nid]
      self.assertEqual(ndptcrds, cntr)
      ndpt = g.Point(ndptcrds)
      self.assertTrue(cp.contains(ndpt) or cp.boundary.contains(ndpt))

   
  def testBuildGridWrappingAroundDateline(self):
    mdldir = os.path.dirname( os.path.abspath(__file__) )
    mshFilePath = os.path.join(mdldir, 'triangularMeshTest/hgridGlob.gr3')
    etopoFilePath = os.path.join(mdldir, 'etopo1_testGiamaica.nc')
    feMeshSpec = abTriangularMesh.loadFromGr3File(mshFilePath)
    grdBuilder = abTriangularMeshGridBuilder(feMeshSpec)
    grd = grdBuilder.buildGrid()
    self.assertFalse(grd.isRegular)
    self.assertTrue(grd.wrapAroundDateline)
    self.assertEqual(112500, len(grd.cellCoordinates))
    self.assertEqual(112500, len(grd.cells))
    self.assertEqual(112500, len(grd.centroids))
    wrappedCellFound = False
    for crd, cp, cntr in zip(grd.cellCoordinates, grd.cells, grd.centroids):
      bndr = cp.boundary.coords[:]
      xs = np.array([v[0] for v in bndr])
      if np.min(xs) < -180 or np.max(xs) > 180:
        wrappedCellFound = True
        for ix1 in range(len(xs)):
          for ix2 in range(ix1+1, len(xs)):
            try:
              self.assertTrue(np.abs(xs[ix2]-xs[ix1]) <= 180)
            except:
              print('test failed for cell ' + str(crd))
              print('xs: ' + str(xs))
              print('ys: ' + str([v[1] for v in bndr]))
              raise
    self.assertTrue(wrappedCellFound)
      


if __name__ == '__main__':
  unittest.main()
