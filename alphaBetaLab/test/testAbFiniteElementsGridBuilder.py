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
    feMeshSpec = abFiniteElementsMesh.loadFromGr3File(mshFilePath)
    nodeIds, cellPly = feMeshSpec.getCellPolygons(excludeLandBoundary=True,
                                                  excludeOpenBoundary=False)
    grdBuilder = abFiniteElementsGridBuilder(feMeshSpec)
    grd = grdBuilder.buildGrid()
    self.assertFalse(grd.isRegular)
    self.assertEqual(362, len(grd.cellCoordinates))
    self.assertEqual(362, len(grd.cells))
    for crd, cp in zip(grd.cellCoordinates, grd.cells):
      nid = crd[0]
      self.assertEqual(1, crd[1])
      ndpt = g.Point(feMeshSpec.nodes[nid])
      self.assertTrue(cp.contains(ndpt) or cp.boundary.contains(ndpt))
      


if __name__ == '__main__':
  unittest.main()
