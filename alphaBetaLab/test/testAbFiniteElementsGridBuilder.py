import unittest
import os
import numpy as np
from shapely import geometry as g

import abFiniteElementsMesh
from abFiniteElementsGridBuilder import abFiniteElementsGridBuilder


class testAbFiniteElementsGridBuilder(unittest.TestCase):

   
  def testBuildGrid(self):
    mdldir = os.path.dirname( os.path.abspath(__file__) )
    mshFilePath = os.path.join(mdldir, 'finiteElementsMeshTest/hgridGiamaica.gr3')
    etopoFilePath = os.path.join(mdldir, 'etopo1_testGiamaica.nc')
    feMeshSpec = abFiniteElementsMesh.loadFromGr3File(mshFilePath)
    nodeIds, cellPly = feMeshSpec.getCellPolygons(excludeLandBoundary=True,
                                                  excludeOpenBoundary=False)
    grdBuilder = abFiniteElementsGridBuilder(feMeshSpec)
    grd = grdBuilder.buildGrid()
    self.assertFalse(grd.isRegular)
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
      


if __name__ == '__main__':
  unittest.main()
