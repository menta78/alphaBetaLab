import numpy as np
import math
import unittest
from shapely import geometry as g

import abSingleCellAlphaEstimator
import abSingleCellBetaEstimator
from abSingleCellAlphaEstimator import abSingleCellAlphaEstimator as ae
from abHighResAlphaMatrix import abHighResAlphaMatrix as alphaMtx

debugPlots = False
abSingleCellAlphaEstimator.debugPlots = debugPlots
abSingleCellAlphaEstimator.defaultKShape = 1
abSingleCellBetaEstimator.debugPlots = False

class testAbSingleCellAlphaEstimator(unittest.TestCase):
  
  def test1(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((4, 2))
    highResCellGrid[3, :] = 0
    highResCellGrid[1, 1] = 0
    xs = np.array(range(2)) + xoff
    ys = np.array(range(4)) + yoff
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid)

    lowresDx = 1.3
    lowresDy = 3.3
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    alphaEst = ae(cellPoly, hiResAlphaMtx)

    direction = 20./180.*np.pi
    alpha = alphaEst.computeAlpha(direction, .1)
    self.assertTrue(alpha > 0)
    obstrE = (1.3 + .3*np.tan(direction))*np.cos(direction)
    obstrN = 1.3*np.sin(direction)
    expalpha = 1 - (obstrE + obstrN)/(1.3*abs(np.sin(direction)) + 3.3*abs(np.cos(direction)))
    self.assertAlmostEqual(expalpha, alpha, delta = 0.001)
  
  def test11(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((2, 4))
    highResCellGrid[1, 1] = 0
    highResCellGrid[0, 3] = 0
    highResCellGrid[1, 3] = 0
    xs = np.array(range(4)) + xoff
    ys = np.array(range(2)) + yoff
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid)

    lowresDx = 3.3
    lowresDy = 1.3
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    alphaEst = ae(cellPoly, hiResAlphaMtx)

    direction = np.pi/2 - 20./180.*np.pi
    alpha = alphaEst.computeAlpha(direction, .1)
    self.assertTrue(alpha > 0)
    obstrE = (1.3 + .3*np.tan(np.pi/2 - direction))*np.cos(np.pi/2 - direction)
    obstrN = 1.3*np.sin(np.pi/2 - direction)
    expalpha = 1 - (obstrE + obstrN)/(1.3*abs(np.sin(np.pi/2 - direction)) + 3.3*abs(np.cos(np.pi/2 - direction)))
    self.assertAlmostEqual(expalpha, alpha, delta = 0.001)

  def test2(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((4, 2))
    highResCellGrid[0, :] = 0
    highResCellGrid[2, 1] = 0
    xs = np.array(range(2)) + xoff
    ys = np.array(range(4)) + yoff
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid)

    lowresDx = 1.3
    lowresDy = 3.3
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    alphaEst = ae(cellPoly, hiResAlphaMtx)
    
    direction = - 20./180.*np.pi
    alpha = alphaEst.computeAlpha(direction, .1)
    self.assertTrue(alpha > 0)
    obstrE = (2. + .3*abs(np.tan(direction)))*abs(np.cos(direction))
    obstrN = 1.3*abs(np.sin(direction))
    expalpha = 1 - (obstrE + obstrN)/(1.3*abs(np.sin(direction)) + 3.3*abs(np.cos(direction)))
    self.assertAlmostEqual(expalpha, alpha, delta = .001)

  def test21(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((4, 2))
    highResCellGrid[0, :] = 0
    highResCellGrid[2, 1] = 0
    highResCellGrid = highResCellGrid[::-1,:]
    xs = np.array(range(2)) + xoff
    ys = np.array(range(4)) + yoff
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid)

    lowresDx = 1.3
    lowresDy = 3.3
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    alphaEst = ae(cellPoly, hiResAlphaMtx)
    
    direction = - 20./180.*np.pi
    alpha = alphaEst.computeAlpha(direction, .1)
    self.assertTrue(alpha > 0)
    obstrE = (1.3 + 1.6*abs(np.tan(direction)))*abs(np.cos(direction))
    obstrN = 0.
    expalpha = 1 - (obstrE + obstrN)/(1.3*abs(np.sin(direction)) + 3.3*abs(np.cos(direction)))
    self.assertAlmostEqual(expalpha, alpha, delta = .001)

  def test3(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((4, 2))
    highResCellGrid[0, :] = 0
    highResCellGrid[2, 1] = 0
    xs = np.array(range(2)) + xoff
    ys = np.array(range(4)) + yoff
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid)

    lowresDx = 1.3
    lowresDy = 3.3
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    alphaEst = ae(cellPoly, hiResAlphaMtx)
    
    direction = 20./180.*np.pi + np.pi
    alpha = alphaEst.computeAlpha(direction, .1)
    self.assertTrue(alpha > 0)
    obstrE = (2. + .3*abs(np.tan(direction)))*abs(np.cos(direction))
    obstrN = 1.3*abs(np.sin(direction))
    expalpha = 1 - (obstrE + obstrN)/(1.3*abs(np.sin(direction)) + 3.3*abs(np.cos(direction)))
    self.assertAlmostEqual(expalpha, alpha, delta = .001)
    
  def test4(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((2, 4))
    highResCellGrid[:, 0] = 0
    highResCellGrid[0, 2] = 0
    xs = np.array(range(4)) + xoff
    ys = np.array(range(2)) + yoff
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid)

    lowresDx = 3.3
    lowresDy = 1.3
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    alphaEst = ae(cellPoly, hiResAlphaMtx)

    direction = np.pi - 20./180.*np.pi
    alpha = alphaEst.computeAlpha(direction, .1)
    self.assertTrue(alpha > 0)
    obstrE = 1.3*abs(np.cos(direction))
    obstrN = (3. - .3*abs(1./np.tan(direction)))*abs(np.sin(direction))
    expalpha = 1 - (obstrE + obstrN)/(lowresDx*abs(np.sin(direction)) + lowresDy*abs(np.cos(direction)))
    self.assertAlmostEqual(expalpha, alpha, delta = .001)
    
  def test5(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((5, 5))
    highResCellGrid[1, 3] = 0
    highResCellGrid[2, 1] = 0
    highResCellGrid[3, 2] = 0
    xs = np.array(range(5)) + xoff
    ys = np.array(range(5)) + yoff
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid)

    lowresDx = 5
    lowresDy = 5
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    alphaEst = ae(cellPoly, hiResAlphaMtx)

    direction = -np.pi/4.
    alpha = alphaEst.computeAlpha(direction, .1)
    self.assertTrue(alpha > 0)
    expalpha = 3./5.
    self.assertAlmostEqual(expalpha, alpha, delta = .001)

  def test6(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((5, 5))
    highResCellGrid[1, 3] = 0
    highResCellGrid[2, 1] = 0
    highResCellGrid[3, 2] = 0
    xs = np.array(range(5)) + xoff
    ys = np.array(range(5)) + yoff
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid)

    lowresDx = 5
    lowresDy = 5
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    alphaEst = ae(cellPoly, hiResAlphaMtx)

    direction = - math.atan(.5)
    alpha = alphaEst.computeAlpha(direction, .1)
    self.assertTrue(alpha > 0)
    obstrE = 3.*abs(np.cos(direction))
    obstrN = 0.
    expalpha = 1 - (obstrE + obstrN)/5./(abs(np.sin(direction)) + abs(np.cos(direction)))
    self.assertAlmostEqual(expalpha, alpha, delta = .001)
 
  def testMultipleOverlaps(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((5, 5))
    highResCellGrid[1, 1] = 0
    highResCellGrid[1, 3] = 0
    highResCellGrid[2, 1] = 0
    highResCellGrid[2, 2] = 0
    highResCellGrid[3, 2] = 0
    highResCellGrid[3, 3] = 0
    xs = np.array(range(5)) + xoff
    ys = np.array(range(5)) + yoff
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid)

    lowresDx = 5
    lowresDy = 5
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    alphaEst = ae(cellPoly, hiResAlphaMtx)

    direction = math.atan(.5)
    alpha = alphaEst.computeAlpha(direction, .1)
    self.assertTrue(alpha > 0)
    obstrE = 3.5*np.cos(direction)
    obstrN = 1.*np.sin(direction)
    expalpha = 1 - (obstrE + obstrN)/5/(abs(np.sin(direction)) + abs(np.cos(direction)))
    self.assertAlmostEqual(expalpha, alpha, delta = .001)
   
  def test0radiants(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((5, 5))
    highResCellGrid[1, 3] = 0.
    highResCellGrid[2, 1] = 0.
    highResCellGrid[3, 2] = 0.
    xs = np.array(range(5)) + xoff
    ys = np.array(range(5)) + yoff
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid)

    lowresDx = 5
    lowresDy = 5
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    alphaEst = ae(cellPoly, hiResAlphaMtx)

    direction = 0.
    alpha = alphaEst.computeAlpha(direction, .1)
    self.assertTrue(alpha > 0)
    expalpha = 2./5.
    self.assertEqual(expalpha, alpha, .001)
  
  def testDifferentHighResDxDy(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((4, 2))
    highResCellGrid[0, :] = 0
    highResCellGrid[2, 1] = 0
    xs = np.array(range(2)) + xoff
    ys = np.array(range(4))*.5 + yoff
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid)

    lowresDx = 1.3
    lowresDy = 3.3*.5
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    alphaEst = ae(cellPoly, hiResAlphaMtx)

    direction = 20./180.*np.pi
    alpha = alphaEst.computeAlpha(direction, .1)
    self.assertTrue(alpha > 0)
    obstrE = (1. + 1.6*np.tan(direction))*np.cos(direction)
    obstrN = 0
    expalpha = 1 - (obstrE + obstrN)/(1.3*abs(np.sin(direction)) + 3.3*.5*abs(np.cos(direction)))
    self.assertAlmostEqual(expalpha, alpha, delta = 0.001)
  
  def testDifferentHighResDxDy_ottant2(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((4, 2))
    highResCellGrid[0, :] = 0
    highResCellGrid[2, 1] = 0
    highResCellGrid = highResCellGrid.transpose()
    xs = np.array(range(4))*.5 + xoff
    ys = np.array(range(2)) + yoff
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid)

    lowresDy = 1.3
    lowresDx = 3.3*.5
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    alphaEst = ae(cellPoly, hiResAlphaMtx)

    direction = np.pi/2. - 20./180.*np.pi
    alpha = alphaEst.computeAlpha(direction, .1)
    self.assertTrue(alpha > 0)
    turneddir = 20./180.*np.pi
    obstrE = (1. + 1.6*np.tan(turneddir))*np.cos(turneddir)
    obstrN = 0
    expalpha = 1 - (obstrE + obstrN)/(1.3*abs(np.sin(turneddir)) + 3.3*.5*abs(np.cos(turneddir)))
    self.assertAlmostEqual(expalpha, alpha, delta = 0.001)
  
  def testDifferentHighResDxDy_quadrant2(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((4, 2))
    highResCellGrid[0, :] = 0
    highResCellGrid[2, 1] = 0
    highResCellGrid = highResCellGrid.transpose()
    xs = np.array(range(4))*.5 + xoff
    ys = np.array(range(2)) + yoff
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid)

    lowresDy = 1.3
    lowresDx = 3.3*.5
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    alphaEst = ae(cellPoly, hiResAlphaMtx)

    direction = 20./180.*np.pi + np.pi/2.
    alpha = alphaEst.computeAlpha(direction, .1)
    self.assertTrue(alpha > 0)

    turneddir = 20./180.*np.pi
    obstrE = (1. + .3*np.tan(turneddir))*np.cos(turneddir)
    obstrN = 1.3*np.sin(turneddir)
    expalpha = 1 - (obstrE + obstrN)/(1.3*abs(np.sin(turneddir)) + 3.3*.5*abs(np.cos(turneddir)))
    self.assertAlmostEqual(expalpha, alpha, delta = 0.001)
  
  def testDifferentHighResDxDy_quadrant3(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((4, 2))
    highResCellGrid[0, :] = 0
    highResCellGrid[2, 1] = 0
    highResCellGrid = highResCellGrid[::-1, ::-1]
    xs = np.array(range(2)) + xoff
    ys = np.array(range(4))*.5 + yoff
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid)

    lowresDx = 1.3
    lowresDy = 3.3*.5
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    alphaEst = ae(cellPoly, hiResAlphaMtx)

    direction = 20./180.*np.pi + np.pi
    alpha = alphaEst.computeAlpha(direction, .1)
    self.assertTrue(alpha > 0)

    turneddir = 20./180.*np.pi
    obstrE = (.65 + 2.3*np.tan(turneddir))*np.cos(turneddir)
    obstrN = 0.
    expalpha = 1 - (obstrE + obstrN)/(1.3*abs(np.sin(turneddir)) + 3.3*.5*abs(np.cos(turneddir)))
    self.assertAlmostEqual(expalpha, alpha, delta = 0.001)
  
  def testDifferentHighResDxDy_quadrant4(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((4, 2))
    highResCellGrid[0, :] = 0
    highResCellGrid[2, 1] = 0
    highResCellGrid = highResCellGrid.transpose()[::-1,::-1]
    xs = np.array(range(4))*.5 + xoff
    ys = np.array(range(2)) + yoff
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid)
    
    lowresDy = 1.3
    lowresDx = 3.3*.5
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    alphaEst = ae(cellPoly, hiResAlphaMtx)

    direction = 20./180.*np.pi + np.pi*3./2.
    alpha = alphaEst.computeAlpha(direction, .1)
    self.assertTrue(alpha > 0)

    turneddir = 20./180.*np.pi
    obstrE = (.65 + 2.3*np.tan(turneddir))*np.cos(turneddir)
    obstrN = 0.
    expalpha = 1 - (obstrE + obstrN)/(1.3*abs(np.sin(turneddir)) + 3.3*.5*abs(np.cos(turneddir)))
    self.assertAlmostEqual(expalpha, alpha, delta = 0.001)

  def testTriangularCell(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((5, 5))
    highResCellGrid[1, 3] = 0
    highResCellGrid[2, 1] = 0
    highResCellGrid[3, 2] = 0

    xs = np.array(range(5)) + xoff
    ys = np.array(range(5)) + yoff
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid)

    xvtxs = [23.5, 24., 22.]
    yvtxs = [11., 13., 14]
    xyvtxs = [xy for xy in zip(xvtxs, yvtxs)]
    cellPoly = g.Polygon(xyvtxs)
    hiResAlphaMtx.polygon = cellPoly

    alphaEst = ae(cellPoly, hiResAlphaMtx)

    direction = np.pi/4.
    alpha = alphaEst.computeAlpha(direction, .1)
    self.assertTrue(alpha > 0)

    obstrE = 1.5*np.cos(direction)
    obstrN = 2.*np.sin(direction)
    expalpha = 1 - (obstrE + obstrN)/(2.5*abs(np.sin(direction)) + 2.*abs(np.cos(direction)))
    self.assertAlmostEqual(expalpha, alpha, delta = 0.001)

  def testPentagonalCell(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((5, 5))
    highResCellGrid[1, 3] = 0
    highResCellGrid[2, 1] = 0
    highResCellGrid[3, 2] = 0

    xs = np.array(range(5)) + xoff
    ys = np.array(range(5)) + yoff
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid)

    xvtxs = [21.5, 22., 23.5, 23., 22.5]
    yvtxs = [12.5, 12., 11.5, 13., 13.5]
    xyvtxs = [xy for xy in zip(xvtxs, yvtxs)]
    cellPoly = g.Polygon(xyvtxs)
    hiResAlphaMtx.polygon = cellPoly

    alphaEst = ae(cellPoly, hiResAlphaMtx)

    direction = np.pi/4.
    alpha = alphaEst.computeAlpha(direction, .1)
    self.assertTrue(alpha > 0)

    expalpha = 1./3.
    self.assertAlmostEqual(expalpha, alpha, delta = 0.001)

  def testPentagonalCell1(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((5, 5))
    highResCellGrid[1, 3] = 0
    highResCellGrid[2, 1] = 0
    highResCellGrid[3, 2] = 0

    xs = np.array(range(5)) + xoff
    ys = np.array(range(5)) + yoff
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid)

    xvtxs = [21.5, 22., 23.5, 23., 22.5]
    yvtxs = [12.5, 12., 11.5, 13., 13.5]
    xyvtxs = [xy for xy in zip(xvtxs, yvtxs)]
    cellPoly = g.Polygon(xyvtxs)
    hiResAlphaMtx.polygon = cellPoly

    alphaEst = ae(cellPoly, hiResAlphaMtx)

    direction = np.arctan(.5)
    alpha = alphaEst.computeAlpha(direction, .1)
    self.assertTrue(alpha > 0)

    #total cross section of the cell with respect to direction:
    ltot = (5.)**.5
    #transparent section of the cell:
    ltrs = (1./5.)**.5
    expalpha = ltrs/ltot
    self.assertAlmostEqual(expalpha, alpha, delta = 0.001)

  def testConcavePolygon(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((5, 5))
    highResCellGrid[1, 1] = 0
    highResCellGrid[1, 3] = 0

    xs = np.array(range(5)) + xoff
    ys = np.array(range(5)) + yoff
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid)

    xvtxs = [21., 22., 22., 23., 23., 24., 24., 21., 21.]
    yvtxs = [11., 11., 12., 12., 11., 11., 13., 13., 11.]  
    xyvtxs = [xy for xy in zip(xvtxs, yvtxs)]
    cellPoly = g.Polygon(xyvtxs)
    hiResAlphaMtx.polygon = cellPoly

    alphaEst = ae(cellPoly, hiResAlphaMtx)

    direction = np.pi/2
    alpha = alphaEst.computeAlpha(direction, .1)
    self.assertTrue(alpha > 0)

    expalpha = 1./3.
    self.assertAlmostEqual(expalpha, alpha, delta = 0.001)

  def testConcavePolygon1(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((5, 5))
    highResCellGrid[1, 1] = 0
    highResCellGrid[1, 3] = 0

    xs = np.array(range(5)) + xoff
    ys = np.array(range(5)) + yoff
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid)

    xvtxs = [21., 22., 22., 23., 23., 24., 24., 21., 21.]
    yvtxs = [11., 11., 12., 12., 11., 11., 13., 13., 11.]  
    xyvtxs = [xy for xy in zip(xvtxs, yvtxs)]
    cellPoly = g.Polygon(xyvtxs)
    hiResAlphaMtx.polygon = cellPoly

    alphaEst = ae(cellPoly, hiResAlphaMtx)

    direction = np.arctan(2)
    alpha = alphaEst.computeAlpha(direction, .1)
    self.assertTrue(alpha > 0)

    trndir = np.arctan(.5)
    obstrE = 2.*np.cos(trndir)
    obstrN = 2.*np.sin(trndir)
    expalpha = 1 - (obstrE + obstrN)/(2.*abs(np.sin(trndir)) + 3.*abs(np.cos(trndir)))
    self.assertAlmostEqual(expalpha, alpha, delta = 0.001)

  def testConcavePolygonDoubleIntersectionHiResCell(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((5, 5))
    highResCellGrid[1, 2] = 0

    xs = np.array(range(5)) + xoff
    ys = np.array(range(5)) + yoff
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid)

    xvtxs = [21., 22.25, 22.25, 22.75, 22.75, 24., 24., 21., 21.]
    yvtxs = [11., 11., 12., 12., 11., 11., 13., 13., 11.]  
    xyvtxs = [xy for xy in zip(xvtxs, yvtxs)]
    cellPoly = g.Polygon(xyvtxs)
    hiResAlphaMtx.polygon = cellPoly

    alphaEst = ae(cellPoly, hiResAlphaMtx)

    direction = np.pi/2
    alpha = alphaEst.computeAlpha(direction, .1)
    self.assertTrue(alpha > 0)

    expalpha = 2.5/3.
    self.assertAlmostEqual(expalpha, alpha, delta = 0.001)
    
    
    

if __name__ == '__main__':
  unittest.main()

