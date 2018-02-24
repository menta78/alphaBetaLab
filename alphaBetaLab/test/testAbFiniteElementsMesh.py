import unittest
import os
import numpy as np

import abFiniteElementsMesh



class testAbFiniteElementsMesh(unittest.TestCase):
   
  def testLoadFromGr3File1(self):
    mdldir = os.path.dirname( os.path.abspath(__file__) )
    mshFilePath = os.path.join(mdldir, 'finiteElementsMeshTest/hgridGiamaica.gr3')
    feMeshSpec = abFiniteElementsMesh.loadFromGr3File(mshFilePath)
    # some random checks
    self.assertEqual(708, len(feMeshSpec.connectionPolygons.keys()))
    self.assertEqual([253, 302, 400], feMeshSpec.connectionPolygons[200])
    self.assertEqual(410, len(feMeshSpec.nodes.keys()))
    self.assertAlmostEqual((-77.3890650728, 17.6616614616), feMeshSpec.nodes[350])
    self.assertEqual(410, len(feMeshSpec.nodeBathy.keys()))
    self.assertAlmostEqual(1372, feMeshSpec.nodeBathy[150])
    self.assertEqual(64, len(feMeshSpec.openBoundaryNodes.keys()))
    self.assertFalse(5 in feMeshSpec.openBoundaryNodes)
    self.assertTrue(22 in feMeshSpec.openBoundaryNodes)
    bnd = np.unique(feMeshSpec.openBoundaryNodes.values())
    self.assertEqual([1], bnd)
    self.assertEqual(1, feMeshSpec.openBoundaryNodes[22])
    self.assertEqual(48, len(feMeshSpec.landBoundaryNodes.keys()))
    self.assertFalse(3 in feMeshSpec.landBoundaryNodes)
    self.assertTrue(25 in feMeshSpec.landBoundaryNodes)
    bnd = np.unique(feMeshSpec.landBoundaryNodes.values())
    self.assertEqual([1], bnd)
   
  def testLoadFromGr3File2(self):
    mdldir = os.path.dirname( os.path.abspath(__file__) )
    mshFilePath = os.path.join(mdldir, 'finiteElementsMeshTest/hgridSmallIsland.gr3')
    feMeshSpec = abFiniteElementsMesh.loadFromGr3File(mshFilePath)
    # some random checks
    self.assertEqual(507, len(feMeshSpec.connectionPolygons.keys()))
    self.assertEqual([262, 280, 263], feMeshSpec.connectionPolygons[200])
    self.assertEqual(287, len(feMeshSpec.nodes.keys()))
    self.assertAlmostEqual((155.9556546618, -57.5789348057), feMeshSpec.nodes[150])
    self.assertEqual(287, len(feMeshSpec.nodeBathy.keys()))
    self.assertAlmostEqual(-3368, feMeshSpec.nodeBathy[150])
    self.assertEqual(0, len(feMeshSpec.openBoundaryNodes.keys()))
    self.assertEqual(35, len(feMeshSpec.landBoundaryNodes.keys()))
    self.assertFalse(100 in feMeshSpec.landBoundaryNodes)
    self.assertTrue(27 in feMeshSpec.landBoundaryNodes)
    self.assertEqual(1, feMeshSpec.landBoundaryNodes[27])
    self.assertEqual(2, feMeshSpec.landBoundaryNodes[5])
    bnd = np.unique(feMeshSpec.landBoundaryNodes.values())
    bnd.sort()
    self.assertTrue(np.logical_and([1, 2], bnd).all())
    
    


if __name__ == '__main__':
  unittest.main()
