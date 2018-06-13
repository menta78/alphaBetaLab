import unittest
import os
import numpy as np
from shapely import geometry as g

import abFiniteElementsMesh

plotPolygons = False


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
    
    
  def testGetCellPolygons_all(self):
    mdldir = os.path.dirname( os.path.abspath(__file__) )
    mshFilePath = os.path.join(mdldir, 'finiteElementsMeshTest/hgridGiamaica.gr3')
    feMeshSpec = abFiniteElementsMesh.loadFromGr3File(mshFilePath)
    nodeIds, cellPly = feMeshSpec.getCellPolygons(excludeLandBoundary=False, 
                                                  excludeOpenBoundary=False)
    self.assertEqual(410, len(nodeIds))
    self.assertEqual(410, len(cellPly))
    for nid, cp in zip(nodeIds, cellPly):
      ndpt = g.Point(feMeshSpec.nodes[nid])
      self.assertTrue(cp.contains(ndpt) or cp.boundary.contains(ndpt))
      
    if plotPolygons:
      import plot.abPolyPlot as pp
      pp.plotFeMesh(feMeshSpec.nodes, feMeshSpec.connectionPolygons)
      pp.plotPolyList(cellPly, doshow=True, title='all')
    

  def testGetCellPolygons_excludeLandBoundary(self):
    mdldir = os.path.dirname( os.path.abspath(__file__) )
    mshFilePath = os.path.join(mdldir, 'finiteElementsMeshTest/hgridGiamaica.gr3')
    feMeshSpec = abFiniteElementsMesh.loadFromGr3File(mshFilePath)
    nodeIds, cellPly = feMeshSpec.getCellPolygons(excludeLandBoundary=True,
                                                  excludeOpenBoundary=False)
    self.assertEqual(362, len(nodeIds))
    self.assertEqual(362, len(cellPly))
    for nid, cp in zip(nodeIds, cellPly):
      ndpt = g.Point(feMeshSpec.nodes[nid])
      self.assertTrue(cp.contains(ndpt) or cp.boundary.contains(ndpt))
      
    if plotPolygons:
      import plot.abPolyPlot as pp
      pp.plotFeMesh(feMeshSpec.nodes, feMeshSpec.connectionPolygons)
      pp.plotPolyList(cellPly, doshow=True, title='exclude land boundary')
    

  def testGetCellPolygons_excludeAllBoundary(self):
    mdldir = os.path.dirname( os.path.abspath(__file__) )
    mshFilePath = os.path.join(mdldir, 'finiteElementsMeshTest/hgridGiamaica.gr3')
    feMeshSpec = abFiniteElementsMesh.loadFromGr3File(mshFilePath)
    nodeIds, cellPly = feMeshSpec.getCellPolygons(excludeLandBoundary=True,
                                                  excludeOpenBoundary=True)
    self.assertEqual(298, len(nodeIds))
    self.assertEqual(298, len(cellPly))
    for nid, cp in zip(nodeIds, cellPly):
      ndpt = g.Point(feMeshSpec.nodes[nid])
      self.assertTrue(cp.contains(ndpt) or cp.boundary.contains(ndpt))
      
    if plotPolygons:
      import plot.abPolyPlot as pp
      pp.plotFeMesh(feMeshSpec.nodes, feMeshSpec.connectionPolygons)
      pp.plotPolyList(cellPly, doshow=True, title='exclude all boundary')
    

  def testGetCellPolygons_file2(self):
    mdldir = os.path.dirname( os.path.abspath(__file__) )
    mshFilePath = os.path.join(mdldir, 'finiteElementsMeshTest/hgridSmallIsland.gr3')
    feMeshSpec = abFiniteElementsMesh.loadFromGr3File(mshFilePath)
    nodeIds, cellPly = feMeshSpec.getCellPolygons()
    self.assertEqual(252, len(nodeIds))
    self.assertEqual(252, len(cellPly))
    for nid, cp in zip(nodeIds, cellPly):
      ndpt = g.Point(feMeshSpec.nodes[nid])
      self.assertTrue(cp.contains(ndpt) or cp.boundary.contains(ndpt))
      
    if plotPolygons:
      import plot.abPolyPlot as pp
      pp.plotFeMesh(feMeshSpec.nodes, feMeshSpec.connectionPolygons)
      pp.plotPolyList(cellPly, doshow=True, title='exclude land boundary')

   
  def testLoadFromMshFile1(self):
    mdldir = os.path.dirname( os.path.abspath(__file__) )
    mshFilePath = os.path.join(mdldir, 'finiteElementsMeshTest/med.msh')
    feMeshSpec = abFiniteElementsMesh.loadFromMshFile(mshFilePath)
    # some random checks
    self.assertEqual(24996, len(feMeshSpec.connectionPolygons.keys()))
    self.assertEqual([4293, 4292, 11180], feMeshSpec.connectionPolygons[6000])
    self.assertEqual(16514, len(feMeshSpec.nodes.keys()))
    self.assertAlmostEqual((4.98622, 43.39583), feMeshSpec.nodes[350])
    self.assertEqual(16514, len(feMeshSpec.nodeBathy.keys()))
    self.assertAlmostEqual(0, feMeshSpec.nodeBathy[150])
    self.assertAlmostEqual(1793.89160670, feMeshSpec.nodeBathy[11234])
    self.assertEqual(0, len(feMeshSpec.openBoundaryNodes.keys()))
    self.assertEqual(5993, len(feMeshSpec.landBoundaryNodes.keys()))
    self.assertTrue(1 in feMeshSpec.landBoundaryNodes)
    self.assertTrue(100 in feMeshSpec.landBoundaryNodes)
    self.assertFalse(6000 in feMeshSpec.landBoundaryNodes)
    


if __name__ == '__main__':
  unittest.main()
