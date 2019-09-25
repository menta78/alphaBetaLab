import unittest
import numpy as np

from alphaBetaLab.abRectangularGridBuilder import abRectangularGridBuilder as grdBld
from alphaBetaLab.abHighResAlphaMatrix import abHighResAlphaMatrix as hiResAMtx
from alphaBetaLab import abCellsEstimator as abClEstMod
from alphaBetaLab.abCellsEstimator import abCellsEstimator
from alphaBetaLab import abSingleCellAlphaEstimator, abSingleCellBetaEstimator
from alphaBetaLab.abOptionManager import abOptions

#abSingleCellAlphaEstimator.debugPlots = True
#abSingleCellAlphaEstimator.debugPlotSave = True

class testAbCellsEstimator(unittest.TestCase):

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
  
  def testLocal(self):
    abSingleCellAlphaEstimator.defaultKShape = 1
    abSingleCellBetaEstimator.defaultKShape = 1
    abClEstMod.defaultShadowAlphaAlleviationParam = 1

    rectGridBld = grdBld(minX = 1, minY = 10, dx = 1, dy = 1, nx = 3, ny = 2, nParWorker = 4, minXYIsCentroid=False)
    hiresxs = np.arange(0, 4, .1)
    hiresys = np.arange(9, 13, .1)
    alphas = np.ones([len(hiresys), len(hiresxs)])
    xobstr = np.array([25])
    yobstr = np.arange(0, len(hiresys), 2)
    xyobstr = np.meshgrid(xobstr, yobstr)
    alphas[xyobstr[1], xyobstr[0]] = 0
    hrmtx = hiResAMtx(hiresxs, hiresys, alphas)
    coastalCellDetector = self.getMockHiResAlphaMtxAndCstCellDet()
    grd = rectGridBld.buildGrid(hrmtx, coastalCellDetector)
    
    dirs = [0., np.pi/2., np.pi, 3.*np.pi/2.]
    freqs = [.1, .2, .3]
    cellEst = abCellsEstimator(grd, hrmtx, dirs, freqs, None)
    
    loccrd, locgeocrd, localpha, locbeta, sizes = cellEst.computeLocalAlphaBeta()
    self.assertEqual(2, len(loccrd))
    self.assertTrue((np.array([1, 0]) == loccrd[0]).all())
    self.assertTrue((np.array([1, 1]) == loccrd[1]).all())
    self.assertEqual(2, len(locgeocrd))
    self.assertEqual([(2.5, 10.5), (2.5, 11.5)], locgeocrd)

    self.assertEqual(2, len(localpha))
    a0 = localpha[0]
    a00 = a0[0]
    a01 = a0[-1]
    self.assertTrue((a00 == a01).all())
    self.assertTrue(np.allclose(a00, np.array([ .5,  .9 ,  .5 ,  .9])))
    self.assertTrue(np.allclose(localpha[0], localpha[1]))

    self.assertEqual(2, len(locbeta))
    b0 = locbeta[0]
    b00 = b0[0]
    b01 = b0[-1]
    self.assertTrue((b00 == b01).all())
    self.assertTrue(np.allclose(b00, np.array([ .75,  .9 ,  .7 ,  .91]), rtol = .05))
    self.assertTrue(np.allclose(locbeta[0], locbeta[1]))

  def testShadow(self):
    abSingleCellAlphaEstimator.defaultKShape = 1
    abSingleCellBetaEstimator.defaultKShape = 1
    abClEstMod.defaultShadowAlphaAlleviationParam = 1

    rectGridBld = grdBld(minX = 1, minY = 10, dx = 1, dy = 1, nx = 3, ny = 2, minXYIsCentroid = False)
    hiResAlphaMtx = self.getMockHiResAlphaMtxAndCstCellDet()
    coastalCellDetector = self.getMockHiResAlphaMtxAndCstCellDet()
    grd = rectGridBld.buildGrid(hiResAlphaMtx, coastalCellDetector)
    hiresxs = np.arange(0, 4, .1)
    hiresys = np.arange(9, 13, .1)
    alphas = np.ones([len(hiresys), len(hiresxs)])
    xobstr = np.array([25])
    yobstr = np.arange(0, len(hiresys), 2)
    xyobstr = np.meshgrid(xobstr, yobstr)
    alphas[xyobstr[1], xyobstr[0]] = 0
    hrmtx = hiResAMtx(hiresxs, hiresys, alphas)
  
    dirs = [0., np.pi/2., np.pi, 3.*np.pi/2.]
    freqs = [.1, .2, .3]
    cellEst = abCellsEstimator(grd, hrmtx, dirs, freqs, abOptions(shadRecalibFactor=1))
    
    cellEst.computeLocalAlphaBeta()
    shdcrd, shdgeocrd, shdalpha, shdbeta, sizes = cellEst.computeShadowAlphaBeta()
    self.assertEqual(6, len(shdcrd))
    self.assertTrue((np.array([0, 0]) == shdcrd[0]).all())
    self.assertTrue((np.array([0, 1]) == shdcrd[1]).all())
    self.assertTrue((np.array([1, 0]) == shdcrd[2]).all())
    self.assertTrue((np.array([1, 1]) == shdcrd[3]).all())
    self.assertTrue((np.array([2, 0]) == shdcrd[4]).all())
    self.assertTrue((np.array([2, 1]) == shdcrd[5]).all())
    self.assertEqual(6, len(shdgeocrd))
    self.assertEqual([(1.5, 10.5), (1.5, 11.5), (2.5, 10.5), (2.5, 11.5), (3.5, 10.5), (3.5, 11.5)], shdgeocrd)
    
    expshdalpha = np.array(\
    [np.array([[ 1. ,  1. ,  0.5,  1. ],\
               [ 1. ,  1. ,  0.5,  1. ],\
               [ 1. ,  1. ,  0.5,  1. ]]),\
     np.array([[ 1. ,  1. ,  0.5,  1. ],\
               [ 1. ,  1. ,  0.5,  1. ],\
               [ 1. ,  1. ,  0.5,  1. ]]),\
     np.array([[ 1. ,  1. ,  1. ,  0.9],\
               [ 1. ,  1. ,  1. ,  0.9],\
               [ 1. ,  1. ,  1. ,  0.9]]),\
     np.array([[ 1. ,  0.9,  1. ,  1. ],\
               [ 1. ,  0.9,  1. ,  1. ],\
               [ 1. ,  0.9,  1. ,  1. ]]),\
     np.array([[ 0.5,  1. ,  1. ,  1. ],\
               [ 0.5,  1. ,  1. ,  1. ],\
               [ 0.5,  1. ,  1. ,  1. ]]),\
     np.array([[ 0.5,  1. ,  1. ,  1. ],\
               [ 0.5,  1. ,  1. ,  1. ],\
               [ 0.5,  1. ,  1. ,  1. ]])])
    self.assertTrue(np.allclose(expshdalpha, np.array(shdalpha)))

    expshdbeta = np.array(\
    [np.array([[ 1. ,  1. ,  0.7,  1. ],
               [ 1. ,  1. ,  0.7,  1. ],\
               [ 1. ,  1. ,  0.7,  1. ]]),\
     np.array([[ 1. ,  1. ,  0.7,  1. ],\
               [ 1. ,  1. ,  0.7,  1. ],\
               [ 1. ,  1. ,  0.7,  1. ]]),\
     np.array([[ 1. ,  1. ,  1. ,  0.91],\
               [ 1. ,  1. ,  1. ,  0.91],\
               [ 1. ,  1. ,  1. ,  0.91]]),\
     np.array([[ 1. ,  0.9,  1. ,  1. ],
               [ 1. ,  0.9,  1. ,  1. ],\
               [ 1. ,  0.9,  1. ,  1. ]]),\
     np.array([[ 0.75,  1.  ,  1.  ,  1.  ],\
               [ 0.75,  1.  ,  1.  ,  1.  ],\
               [ 0.75,  1.  ,  1.  ,  1.  ]]),\
     np.array([[ 0.75,  1.  ,  1.  ,  1.  ],
               [ 0.75,  1.  ,  1.  ,  1.  ],\
               [ 0.75,  1.  ,  1.  ,  1.  ]])])
    self.assertTrue(np.allclose(expshdbeta, np.array(shdbeta), rtol = .05))



if __name__ == '__main__':
  unittest.main()

