import unittest
import os
import numpy as np
from shapely import geometry as g

from alphaBetaLab import abTriangularMesh

plotPolygons = False


class testAbTriangularMesh(unittest.TestCase):

   
  def testLoadFromGr3File1(self):
    mdldir = os.path.dirname( os.path.abspath(__file__) )
    mshFilePath = os.path.join(mdldir, 'triangularMeshTest/hgridGiamaica.gr3')
    feMeshSpec = abTriangularMesh.loadFromGr3File(mshFilePath)
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
    bnd = np.unique(list(feMeshSpec.openBoundaryNodes.values()))
    self.assertEqual([1], bnd)
    self.assertEqual(1, feMeshSpec.openBoundaryNodes[22])
    self.assertEqual(48, len(feMeshSpec.landBoundaryNodes.keys()))
    self.assertFalse(3 in feMeshSpec.landBoundaryNodes)
    self.assertTrue(25 in feMeshSpec.landBoundaryNodes)
    bnd = np.unique(list(feMeshSpec.landBoundaryNodes.values()))
    self.assertEqual([1], bnd)

   
  def testLoadFromGr3File2(self):
    mdldir = os.path.dirname( os.path.abspath(__file__) )
    mshFilePath = os.path.join(mdldir, 'triangularMeshTest/hgridSmallIsland.gr3')
    feMeshSpec = abTriangularMesh.loadFromGr3File(mshFilePath)
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

   
  def testLoadFromGr3File3(self):
    mdldir = os.path.dirname( os.path.abspath(__file__) )
    mshFilePath = os.path.join(mdldir, 'triangularMeshTest/hgridWestMed.gr3')
    feMeshSpec = abTriangularMesh.loadFromGr3File(mshFilePath)
    # some random checks
    self.assertEqual(1587, len(feMeshSpec.nodes.keys()))
    self.assertEqual(2819, len(feMeshSpec.connectionPolygons.keys()))
    self.assertEqual([500, 537, 525], feMeshSpec.connectionPolygons[100])
    self.assertEqual(2, len(feMeshSpec.openBoundaries.keys()))
    bndnds = feMeshSpec.openBoundaries[2]
    self.assertEqual(6, len(bndnds))
    self.assertEqual(1556, bndnds[3])
    self.assertEqual(11, len(feMeshSpec.openBoundaryNodes.keys()))
    self.assertEqual(352, len(feMeshSpec.landBoundaryNodes.keys()))
    self.assertEqual(352, len(feMeshSpec.landBoundaryOrdered))
    self.assertEqual(5, len(feMeshSpec.landBoundaries.keys()))
    self.assertEqual(5, len(feMeshSpec.landBoundaryType.keys()))
    self.assertEqual(abTriangularMesh.landBoundaryExteriorType, feMeshSpec.landBoundaryType[1])
    self.assertEqual(abTriangularMesh.landBoundaryIslandType, feMeshSpec.landBoundaryType[5])
    bndnds = feMeshSpec.landBoundaries[3]
    self.assertEqual(8, len(bndnds))
    self.assertEqual(453, bndnds[-1])

   
  def testSaveGr3File(self):
    mdldir = os.path.dirname( os.path.abspath(__file__) )
    mshFilePath = os.path.join(mdldir, 'triangularMeshTest/hgridWestMed.gr3')
    feMeshSpec0 = abTriangularMesh.loadFromGr3File(mshFilePath)
    tmpfnm = './_tmp.gr3'
    feMeshSpec0.saveAsGr3(tmpfnm)
    try:
      feMeshSpec = abTriangularMesh.loadFromGr3File(tmpfnm)
      # some random checks
      self.assertEqual(1587, len(feMeshSpec.nodes.keys()))
      self.assertEqual(2819, len(feMeshSpec.connectionPolygons.keys()))
      self.assertEqual([500, 537, 525], feMeshSpec.connectionPolygons[100])
      self.assertEqual(2, len(feMeshSpec.openBoundaries.keys()))
      bndnds = feMeshSpec.openBoundaries[2]
      self.assertEqual(6, len(bndnds))
      self.assertEqual(1556, bndnds[3])
      self.assertEqual(11, len(feMeshSpec.openBoundaryNodes.keys()))
      self.assertEqual(352, len(feMeshSpec.landBoundaryNodes.keys()))
      self.assertEqual(352, len(feMeshSpec.landBoundaryOrdered))
      self.assertEqual(5, len(feMeshSpec.landBoundaries.keys()))
      self.assertEqual(5, len(feMeshSpec.landBoundaryType.keys()))
      self.assertEqual(abTriangularMesh.landBoundaryExteriorType, feMeshSpec.landBoundaryType[1])
      self.assertEqual(abTriangularMesh.landBoundaryIslandType, feMeshSpec.landBoundaryType[5])
      bndnds = feMeshSpec.landBoundaries[3]
      self.assertEqual(8, len(bndnds))
      self.assertEqual(453, bndnds[-1])
    finally:
      os.remove(tmpfnm)



  def testCreateSchismWWMBndFile(self):
    mdldir = os.path.dirname( os.path.abspath(__file__) )
    mshFilePath = os.path.join(mdldir, 'triangularMeshTest/hgridWestMed.gr3')
    feMeshSpec = abTriangularMesh.loadFromGr3File(mshFilePath)
    schismWWMBndFilePath = os.path.join(mdldir, 'triangularMeshTest/schismWWMbnd.gr3')
    feMeshSpec.createSchismWWMBndFile(schismWWMBndFilePath)
    try:
      self.assertTrue(os.path.isfile(schismWWMBndFilePath))
      dt = np.loadtxt(schismWWMBndFilePath, skiprows=2)
      # some random check
      self.assertEqual(1587, dt.shape[0])
      self.assertEqual(4, dt.shape[1])
      self.assertEqual(100, dt[99, 0])
      self.assertEqual(0, dt[99, 1])
      self.assertEqual(2, dt[1, 0])
      self.assertEqual(1, dt[2, 1])
      self.assertEqual(992, dt[991, 0])
      self.assertEqual(-1, dt[991, 1])
    finally:
      os.remove(schismWWMBndFilePath)
    
    
    
  def testGetCellPolygons_all(self):
    mdldir = os.path.dirname( os.path.abspath(__file__) )
    mshFilePath = os.path.join(mdldir, 'triangularMeshTest/hgridGiamaica.gr3')
    feMeshSpec = abTriangularMesh.loadFromGr3File(mshFilePath)
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
    mshFilePath = os.path.join(mdldir, 'triangularMeshTest/hgridGiamaica.gr3')
    feMeshSpec = abTriangularMesh.loadFromGr3File(mshFilePath)
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
    mshFilePath = os.path.join(mdldir, 'triangularMeshTest/hgridGiamaica.gr3')
    feMeshSpec = abTriangularMesh.loadFromGr3File(mshFilePath)
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
    mshFilePath = os.path.join(mdldir, 'triangularMeshTest/hgridSmallIsland.gr3')
    feMeshSpec = abTriangularMesh.loadFromGr3File(mshFilePath)
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
    mshFilePath = os.path.join(mdldir, 'triangularMeshTest/med.msh')
    feMeshSpec = abTriangularMesh.loadFromMshFile(mshFilePath)
    # some random checks
    self.assertEqual(24996, len(feMeshSpec.connectionPolygons.keys()))
    self.assertEqual([4293, 4292, 11180], feMeshSpec.connectionPolygons[7])
    self.assertEqual(16514, len(feMeshSpec.nodes.keys()))
    self.assertAlmostEqual((4.98622, 43.39583), feMeshSpec.nodes[350])
    self.assertEqual(16514, len(feMeshSpec.nodeBathy.keys()))
    self.assertAlmostEqual(0, feMeshSpec.nodeBathy[150])
    self.assertAlmostEqual(-1793.89160670, feMeshSpec.nodeBathy[11234])
    self.assertEqual(0, len(feMeshSpec.openBoundaryNodes.keys()))
    self.assertEqual(5993, len(feMeshSpec.landBoundaryNodes.keys()))
    self.assertEqual(5993, len(feMeshSpec.landBoundaryOrdered))
    self.assertTrue(1 in feMeshSpec.landBoundaryNodes)
    self.assertTrue(100 in feMeshSpec.landBoundaryNodes)
    self.assertFalse(6000 in feMeshSpec.landBoundaryNodes)
    self.assertTrue(1 in feMeshSpec.landBoundaryOrdered)
    self.assertTrue(100 in feMeshSpec.landBoundaryOrdered)
    self.assertFalse(6000 in feMeshSpec.landBoundaryOrdered)


  def testSaveMshFile1(self):
    mdldir = os.path.dirname( os.path.abspath(__file__) )
    mshFilePath = os.path.join(mdldir, 'triangularMeshTest/med.msh')
    feMeshSpec = abTriangularMesh.loadFromMshFile(mshFilePath)
    mshTestFilePath = os.path.join(mdldir, 'triangularMeshTest/test_med_copy.msh')
    feMeshSpec.saveAsMsh(mshTestFilePath)
    try:
      self.assertTrue(os.path.isfile(mshTestFilePath))
      feMeshSpec = abTriangularMesh.loadFromMshFile(mshTestFilePath)
      self.assertEqual(24996, len(feMeshSpec.connectionPolygons.keys()))
      self.assertEqual([4293, 4292, 11180], feMeshSpec.connectionPolygons[7])
      self.assertEqual(16514, len(feMeshSpec.nodes.keys()))
      self.assertAlmostEqual((4.98622, 43.39583), feMeshSpec.nodes[350])
      self.assertEqual(16514, len(feMeshSpec.nodeBathy.keys()))
      self.assertAlmostEqual(0, feMeshSpec.nodeBathy[150])
      self.assertAlmostEqual(1793.8916, feMeshSpec.nodeBathy[11234], 4)
      self.assertEqual(0, len(feMeshSpec.openBoundaryNodes.keys()))
      self.assertEqual(5993, len(feMeshSpec.landBoundaryNodes.keys()))
      self.assertTrue(1 in feMeshSpec.landBoundaryNodes)
      self.assertTrue(100 in feMeshSpec.landBoundaryNodes)
      self.assertFalse(6000 in feMeshSpec.landBoundaryNodes)
    finally:
      os.remove(mshTestFilePath)


  def testSaveMshFile2(self):
    mdldir = os.path.dirname( os.path.abspath(__file__) )
    mshFilePath = os.path.join(mdldir, 'triangularMeshTest/hgridSmallIsland.gr3')
    feMeshSpec = abTriangularMesh.loadFromGr3File(mshFilePath)
    mshTestFilePath = os.path.join(mdldir, 'triangularMeshTest/test_smallIsland_copy.msh')
    feMeshSpec.saveAsMsh(mshTestFilePath, bathyFactor=-1)
    try:
      self.assertTrue(os.path.isfile(mshTestFilePath))
      feMeshSpec = abTriangularMesh.loadFromMshFile(mshTestFilePath)
      # some random checks
      self.assertEqual(507, len(feMeshSpec.connectionPolygons.keys()))
      self.assertEqual([262, 280, 263], feMeshSpec.connectionPolygons[200])
      self.assertEqual(287, len(feMeshSpec.nodes.keys()))
      self.assertAlmostEqual((155.9556547, -57.57893481), feMeshSpec.nodes[150])
      self.assertEqual(287, len(feMeshSpec.nodeBathy.keys()))
      self.assertAlmostEqual(3368, feMeshSpec.nodeBathy[150])
      self.assertEqual(0, len(feMeshSpec.openBoundaryNodes.keys()))
      self.assertEqual(35, len(feMeshSpec.landBoundaryNodes.keys()))
      self.assertFalse(100 in feMeshSpec.landBoundaryNodes)
      self.assertTrue(27 in feMeshSpec.landBoundaryNodes)
      self.assertTrue(1 in feMeshSpec.landBoundaryNodes)
      self.assertTrue(2 in feMeshSpec.landBoundaryNodes)
    finally:
      os.remove(mshTestFilePath)


  def testSaveMshFileBathyFactor(self):
    mdldir = os.path.dirname( os.path.abspath(__file__) )
    mshFilePath = os.path.join(mdldir, 'triangularMeshTest/hgridSmallIsland.gr3')
    feMeshSpec = abTriangularMesh.loadFromGr3File(mshFilePath)
    mshTestFilePath = os.path.join(mdldir, 'triangularMeshTest/test_smallIsland_copy.msh')
    feMeshSpec.saveAsMsh(mshTestFilePath, bathyFactor=1)
    try:
      self.assertTrue(os.path.isfile(mshTestFilePath))
      feMeshSpec = abTriangularMesh.loadFromMshFile(mshTestFilePath)
      self.assertAlmostEqual(-3368, feMeshSpec.nodeBathy[150])
    finally:
      os.remove(mshTestFilePath)


  def testAdjustCrossDatelineVertices(self):
    x = [0, 1, .5]
    y = [10, 10, 11]
    vertices = [vrtx for vrtx in zip(x, y)]
    vertices = abTriangularMesh.adjustCrossDatelineVertices(vertices)
    for xexp, yexp, xyfnd in zip(x, y, vertices):
      self.assertEqual(xexp, xyfnd[0])
      self.assertEqual(yexp, xyfnd[1])

    x = [-179, 179, 180]
    y = [10, 10, 11]
    xexps = [181, 179, 180]
    vertices = [vrtx for vrtx in zip(x, y)]
    vertices = abTriangularMesh.adjustCrossDatelineVertices(vertices)
    for xexp, yexp, xyfnd in zip(xexps, y, vertices):
      self.assertEqual(xexp, xyfnd[0])
      self.assertEqual(yexp, xyfnd[1])

    x = [179, -179, 180]
    y = [10, 10, 11]
    xexps = [179, 181, 180]
    vertices = [vrtx for vrtx in zip(x, y)]
    vertices = abTriangularMesh.adjustCrossDatelineVertices(vertices)
    for xexp, yexp, xyfnd in zip(xexps, y, vertices):
      self.assertEqual(xexp, xyfnd[0])
      self.assertEqual(yexp, xyfnd[1])

    x = [179, 180, -179]
    y = [10, 11, 10]
    xexps = [179, 180, 181]
    vertices = [vrtx for vrtx in zip(x, y)]
    vertices = abTriangularMesh.adjustCrossDatelineVertices(vertices)
    for xexp, yexp, xyfnd in zip(xexps, y, vertices):
      self.assertEqual(xexp, xyfnd[0])
      self.assertEqual(yexp, xyfnd[1])

    x = [179, -179, -180]
    y = [10, 10, 11]
    xexps = [-181, -179, -180]
    vertices = [vrtx for vrtx in zip(x, y)]
    vertices = abTriangularMesh.adjustCrossDatelineVertices(vertices)
    for xexp, yexp, xyfnd in zip(xexps, y, vertices):
      self.assertEqual(xexp, xyfnd[0])
      self.assertEqual(yexp, xyfnd[1])

    x = [-179, 179, -180]
    y = [10, 10, 11]
    xexps = [-179, -181, -180]
    vertices = [vrtx for vrtx in zip(x, y)]
    vertices = abTriangularMesh.adjustCrossDatelineVertices(vertices)
    for xexp, yexp, xyfnd in zip(xexps, y, vertices):
      self.assertEqual(xexp, xyfnd[0])
      self.assertEqual(yexp, xyfnd[1])

    x = [-179, -180, 179]
    y = [10, 11, 10]
    xexps = [-179, -180, -181]
    vertices = [vrtx for vrtx in zip(x, y)]
    vertices = abTriangularMesh.adjustCrossDatelineVertices(vertices)
    for xexp, yexp, xyfnd in zip(xexps, y, vertices):
      self.assertEqual(xexp, xyfnd[0])
      self.assertEqual(yexp, xyfnd[1])


  def testGetNodesDataFrame(self):
    mdldir = os.path.dirname( os.path.abspath(__file__) )
    mshFilePath = os.path.join(mdldir, 'triangularMeshTest/hgridGiamaica.gr3')
    feMeshSpec = abTriangularMesh.loadFromGr3File(mshFilePath)
    df = feMeshSpec.getNodesDataframe()
    # some random checks
    self.assertEqual(410, len(df))
    self.assertEqual(3, len(df.columns))
    self.assertAlmostEqual(df[df.index==350].x.values[0], -77.3890650728)
    self.assertAlmostEqual(df[df.index==350].y.values[0], 17.6616614616)
    self.assertAlmostEqual(410, len(feMeshSpec.nodeBathy.keys()))
    self.assertAlmostEqual(119.0, df[df.index==350].bathy.values[0])
    

      
    


if __name__ == '__main__':
  unittest.main()
