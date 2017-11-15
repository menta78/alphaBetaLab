import numpy as np
import math
import unittest
from shapely import geometry as g

import abSingleCellAlphaEstimator
import abSingleCellBetaEstimator
from abSingleCellBetaEstimator import abSingleCellBetaEstimator as be
from abHighResAlphaMatrix import abHighResAlphaMatrix as alphaMtx

debugPlots = False
abSingleCellAlphaEstimator.debugPlots = False
abSingleCellAlphaEstimator.defaultKShape = 1
abSingleCellBetaEstimator.debugPlots = debugPlots
abSingleCellBetaEstimator.defaultKShape = 1

rotatingTestBeta = .60568597491025722

class testSingleCellBetaEstimator(unittest.TestCase):

  def test1(self):
    xoff = 30.
    yoff = 40.

    highResCellGrid = np.ones((5, 4))
    highResCellGrid[0, 0] = 0
    highResCellGrid[1, 1] = 0
    highResCellGrid[2, 2] = 0
    highResCellGrid[4, 3] = 0
    xs = np.array(range(4)) + xoff
    ys = np.array(range(5)) + yoff
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid)

    lowresDx = 4
    lowresDy = 5
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    betaEst = be(cellPoly, hiResAlphaMtx)

    dr = 0
    beta = betaEst.computeBeta(dr, .1)
    
    alpha1 = .8
    alpha2 = .6
    alpha3 = .4
    alpha4 = .2
    expbeta = (alpha1 + alpha2 + alpha3 + alpha4)/4
    self.assertAlmostEqual(expbeta, beta, delta = .0001)

  def test2(self):
    xoff = 30.
    yoff = 40.

    highResCellGrid = np.ones((5, 4))
    highResCellGrid[0, 0] = 0
    highResCellGrid[1, 1] = 0
    highResCellGrid[2, 2] = 0
    highResCellGrid[4, 3] = 0
    xs = np.array(range(4)) + xoff
    ys = np.array(range(5)) + yoff
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid)

    lowresDx = 4
    lowresDy = 5
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    betaEst = be(cellPoly, hiResAlphaMtx)

    dr = np.pi/4.
    beta = betaEst.computeBeta(dr, .1)
    
    expbeta = 0.72105087014725577
    self.assertAlmostEqual(expbeta, beta, delta = .0001)

  def test3(self):
    xoff = 30.
    yoff = 40.

    highResCellGrid = np.ones((5, 4))
    highResCellGrid[0, 0] = 0
    highResCellGrid[1, 1] = 0
    highResCellGrid[2, 2] = 0
    highResCellGrid[4, 3] = 0
    xs = np.array(range(4)) + xoff
    ys = np.array(range(5)) + yoff
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid)

    lowresDx = 4
    lowresDy = 5
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    betaEst = be(cellPoly, hiResAlphaMtx, maxSubSections=100000)

    dr = np.arctan(.5)
    beta = betaEst.computeBeta(dr, .1)
    
    expbeta = rotatingTestBeta
    self.assertAlmostEqual(expbeta, beta, delta = .0001)

  def test_secondOctant(self):
    xoff = 30.
    yoff = 40.

    highResCellGrid = np.ones((5, 4))
    highResCellGrid[0, 0] = 0
    highResCellGrid[1, 1] = 0
    highResCellGrid[2, 2] = 0
    highResCellGrid[4, 3] = 0
    highResCellGrid = highResCellGrid.transpose()
    xs = np.array(range(5)) + xoff
    ys = np.array(range(4)) + yoff
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid)

    lowresDx = 5
    lowresDy = 4
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    betaEst = be(cellPoly, hiResAlphaMtx)

    dr = np.arctan(2.)
    beta = betaEst.computeBeta(dr, .1)
    
    expbeta = rotatingTestBeta
    self.assertAlmostEqual(expbeta, beta, delta = .0001)

  def test_secondQuarter(self):
    xoff = 30.
    yoff = 40.

    highResCellGrid = np.ones((5, 4))
    highResCellGrid[0, 0] = 0
    highResCellGrid[1, 1] = 0
    highResCellGrid[2, 2] = 0
    highResCellGrid[4, 3] = 0
    highResCellGrid = highResCellGrid.transpose()
    highResCellGrid = highResCellGrid[::-1]
    xs = np.array(range(5)) + xoff
    ys = np.array(range(4)) + yoff
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid)

    lowresDx = 5
    lowresDy = 4
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    betaEst = be(cellPoly, hiResAlphaMtx)
    betaEst.kshape = 1.
    betaEst.obstrAlleviationEnabled = False

    dr = np.arctan(-2.)
    beta = betaEst.computeBeta(dr, .1)
    
    expbeta = rotatingTestBeta
    self.assertAlmostEqual(expbeta, beta, delta = .0001)

  def test_thirdQuarter(self):
    xoff = 30.
    yoff = 40.

    highResCellGrid = np.ones((5, 4))
    highResCellGrid[0, 0] = 0
    highResCellGrid[1, 1] = 0
    highResCellGrid[2, 2] = 0
    highResCellGrid[4, 3] = 0
    highResCellGrid = highResCellGrid[::-1, ::-1]
    xs = np.array(range(4)) + xoff
    ys = np.array(range(5)) + yoff
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid)

    lowresDx = 4
    lowresDy = 5
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    betaEst = be(cellPoly, hiResAlphaMtx)

    dr = np.arctan(.5) + np.pi
    beta = betaEst.computeBeta(dr, .1)
    
    expbeta = rotatingTestBeta
    self.assertAlmostEqual(expbeta, beta, delta = .0001)

  def test_forthQuarter(self):
    xoff = 30.
    yoff = 40.

    highResCellGrid = np.ones((5, 4))
    highResCellGrid[0, 0] = 0
    highResCellGrid[1, 1] = 0
    highResCellGrid[2, 2] = 0
    highResCellGrid[4, 3] = 0
    highResCellGrid = highResCellGrid.transpose()
    highResCellGrid = highResCellGrid[:, ::-1]
    xs = np.array(range(5)) + xoff
    ys = np.array(range(4)) + yoff
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid)

    lowresDx = 5
    lowresDy = 4
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    betaEst = be(cellPoly, hiResAlphaMtx)

    dr = np.arctan(-2.) + np.pi
    beta = betaEst.computeBeta(dr, .1)
    
    expbeta = rotatingTestBeta
    self.assertAlmostEqual(expbeta, beta, delta = .0001)

  def test_concavePolygon(self):
    xoff = 30.
    yoff = 40.

    highResCellGrid = np.ones((5, 4))
    highResCellGrid[2, 1] = 0
    xs = np.array(range(4)) + xoff
    ys = np.array(range(5)) + yoff
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid)
    
    lowresDx = 4
    lowresDy = 5
    vrtxxs = np.array([1., 3., 3., 1., 1., 2., 2., 1., 1.]) + xoff
    vrtxys = np.array([1., 1., 4., 4., 2.75, 2.75, 2.25, 2.25, 1.]) + yoff
    cellPolyVrtxs = [[c[0], c[1]] for c in zip(vrtxxs, vrtxys)]
    
    cellPoly = g.Polygon(cellPolyVrtxs)
    hiResAlphaMtx.polygon = cellPoly

    betaEst = be(cellPoly, hiResAlphaMtx)

    dr = np.arctan(.5)
    beta = betaEst.computeBeta(dr, .1)
    
    expbeta = 0.67258992805755391
    self.assertAlmostEqual(expbeta, beta, delta = .0001)
    



if __name__ == '__main__':
  unittest.main()

