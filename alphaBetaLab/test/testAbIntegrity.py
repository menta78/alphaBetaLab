import unittest
import os
import shutil

from abHighResAlphaMatrix import *
from abEstimateAndSave import _abEstimateAndSave
import abCellsEstimator
from test.wwiiiSyntheticGridManager.wwiiiSyntheticGridManager import *
from abRectangularGridBuilder import abRectangularGridBuilder
from abHighResAlphaMatrix import abHighResAlphaMatrix as hiResAMtx
from abOptionManager import abOptions



class testIntegrity(unittest.TestCase):



  def setUp(self):
    abCellsEstimator.defaultShadowAlphaAlleviationParam = .83
    abCellsEstimator.defaultAlleviationMaxBlockedNeighborCount = 1 
    self.directions = np.linspace(0, 2*np.pi, 25)[:-1]
    self.freqs = np.array([0.066667*1.1**i for i in range(25)])
    self.tempOutDir = os.path.join(os.getcwd(), 'integrityTestTmpOutput')
    self.locpath = os.path.dirname(os.path.abspath(__file__))



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



  def _testIntegrity(self, locAlphaBetaExpFile, shdAlphaBetaExpFile,\
         grid, hiresAlpha, nParWorker):
     
     try:
       os.mkdir(self.tempOutDir)
     except:
       pass
     try:
       betaMaxSubSections = 1000000000
       computationDirs = np.arange(0, 2*np.pi, np.pi/12.)
       opt = abOptions(shadRecalibFactor=1, 
             betaMaxSubSections=betaMaxSubSections, computationDirs=computationDirs)
       _abEstimateAndSave(self.directions, self.freqs, 'test', grid, 
                          hiresAlpha, self.tempOutDir, nParWorker=nParWorker, abOptions=opt)

       def loadVals(fl):
         vals = []
         for ln in fl:
           if ln[0] != '$':
             vlsln = [float(v) for v in ln.strip('\n\r\t ').split() if v]
             vals.extend(vlsln)
         return np.array(vals)

       outLocFlPath = os.path.join(self.tempOutDir, 'obstructions_local.test.in')
       outLocFl = open(outLocFlPath)
       outvals = loadVals(outLocFl)
       expLocFl = open(locAlphaBetaExpFile)
       expvals = loadVals(expLocFl)
       self.assertTrue(np.all(abs(expvals-outvals) < .05))

       outShdFlPath = os.path.join(self.tempOutDir, 'obstructions_shadow.test.in')
      #outShdFl = open(outShdFlPath); outlines = ''.join(ln for ln in outShdFl)
       outShdFl = open(outShdFlPath)
       outvals = loadVals(outShdFl)
      #expShdFl = open(shdAlphaBetaExpFile); explines = ''.join(ln for ln in expShdFl)
       expShdFl = open(shdAlphaBetaExpFile)
       expvals = loadVals(expShdFl)
       self.assertTrue(np.all(abs(expvals-outvals) < .05 ))
     finally:
       shutil.rmtree(self.tempOutDir)

    

  def _testSyntheticCase01(self, nParWorker):
    hilowCellsFactor = 8
    lresObstrX = 3
    # DEFINITION OF HIGH RES GRID
    x0 = 4.9; nx = 102; dx = 0.1; y0 = 29.9; ny = 82; dy = 0.1; zbottom = -500
    
    # obstructions
    x = hilowCellsFactor*lresObstrX + 5
    obstrsxs = (np.ones(40)*x).astype(int)
    obstrsys = (np.arange(0, 40, 1)*2 + 1).astype(int)
    
    # generation of synthetic case data
    grdSpc = gridSpec(name = 'testHR', x0 = x0, nx = nx, dx = dx, y0 = y0, ny = ny, dy = dy, zbottom = zbottom)
    grdSpc.boundaryYs = [i for i in range(ny)]
    grdSpc.boundaryXs = [0 for i in range(ny)]
    grdSpc.customNameList = "&PRO3 WDTHCG = 0.5, WDTHTH = 0.5 /"
    syntGridManager = syntheticGridManager(grdSpc)
    od = pointsObstacleDrawer()
    od.setXY(xs = obstrsxs, ys = obstrsys)
    syntGridManager.obstacleDrawers.append(od)
    _, hiresMask = syntGridManager.generateBathyData()
    hiresAlpha = np.array(hiresMask)
    hiresAlpha[hiresAlpha > 1] = 1
    
    hiresxs = x0 + np.arange(nx)*dx
    hiresys = y0 + np.arange(ny)*dy
    hrmtx = hiResAMtx(hiresxs, hiresys, hiresAlpha)
    ##################################
    
    # DEFINITION OF LOW RES GRID
    x0 = 4.2; nx = 13; dx = 0.8; y0 = 29.2; ny = 12; dy = 0.8; zbottom = -500
    # grid
    rectGridBuilder = abRectangularGridBuilder(x0, y0, dx, dy, nx, ny, minXYIsCentroid=False)
    cstClDet = self.getMockHiResAlphaMtxAndCstCellDet()
    grid = rectGridBuilder.buildGrid(hrmtx, cstClDet)
    
    locAlphaBetaExpFile = os.path.join(self.locpath, 'integrityTest/obstructions_local.syntheticCase01.in')
    shdAlphaBetaExpFile = os.path.join(self.locpath, 'integrityTest/obstructions_shadow.syntheticCase01.in')
    self._testIntegrity(locAlphaBetaExpFile, shdAlphaBetaExpFile, grid, hrmtx, nParWorker)

  def testSyntheticCase01_serial(self):
    self._testSyntheticCase01(1)

  def testSyntheticCase01_parallel(self):
    self._testSyntheticCase01(4)




  def _testSyntheticCase04(self, nParWorker):
    #obstructions
    hilowCellsFactor = 8
    lresObstrX = 3
    
    singleCellXs = np.array([2, 3, 5, 6])
    singleCellYs = np.array([1, 4, 3, 6])
    obstrsxs = np.tile(singleCellXs, 10) + hilowCellsFactor*lresObstrX
    obstrsxs = np.concatenate((obstrsxs, obstrsxs + hilowCellsFactor))
    
    obstrsys = singleCellYs
    for i in range(1, 10):
      obstrsys = np.concatenate((obstrsys, singleCellYs + i*hilowCellsFactor))
    obstrsys += 1
    #obstrsys = np.tile(obstrsys, 2)
    obstrsys = np.concatenate((obstrsys, obstrsys + 1))
    ##############

    # DEFINITION OF HIGH RES GRID
    x0 = 4.9; nx = 102; dx = 0.1; y0 = 29.9; ny = 82; dy = 0.1; zbottom = -500
    
    # generation of synthetic case data
    grdSpc = gridSpec(name = 'testHR', x0 = x0, nx = nx, dx = dx, y0 = y0, ny = ny, dy = dy, zbottom = zbottom)
    grdSpc.boundaryYs = [i for i in range(ny)]
    grdSpc.boundaryXs = [0 for i in range(ny)]
    grdSpc.customNameList = "&PRO3 WDTHCG = 0.5, WDTHTH = 0.5 /"
    syntGridManager = syntheticGridManager(grdSpc)
    od = pointsObstacleDrawer()
    od.setXY(xs = obstrsxs, ys = obstrsys)
    syntGridManager.obstacleDrawers.append(od)
    _, hiresMask = syntGridManager.generateBathyData()
    hiresAlpha = np.array(hiresMask)
    hiresAlpha[hiresAlpha > 1] = 1
    
    hiresxs = x0 + np.arange(nx)*dx
    hiresys = y0 + np.arange(ny)*dy
    hresSyntGrdMng = syntGridManager
    hrmtx = hiResAMtx(hiresxs, hiresys, hiresAlpha)
    ##################################
    
    # DEFINITION OF LOW RES GRID
    x0 = 4.2; nx = 13; dx = 0.8; y0 = 29.2; ny = 12; dy = 0.8; zbottom = -500
    # grid
    rectGridBuilder = abRectangularGridBuilder(x0, y0, dx, dy, nx, ny, minXYIsCentroid=False)
    cstClDet = self.getMockHiResAlphaMtxAndCstCellDet()
    grid = rectGridBuilder.buildGrid(hrmtx, cstClDet)
    
    locAlphaBetaExpFile = os.path.join(self.locpath, 'integrityTest/obstructions_local.syntheticCase04.in')
    shdAlphaBetaExpFile = os.path.join(self.locpath, 'integrityTest/obstructions_shadow.syntheticCase04.in')
    self._testIntegrity(locAlphaBetaExpFile, shdAlphaBetaExpFile, grid, hrmtx, nParWorker)

  def testSyntheticCase04_serial(self):
    self._testSyntheticCase04(1)

  def testSyntheticCase04_parallel(self):
    self._testSyntheticCase04(4)




  def _testSyntheticCase07_totalBlock(self, nParWorker):
    hilowCellsFactor = 8
    lresObstrX = 3
    # DEFINITION OF HIGH RES GRID
    x0 = 4.9; nx = 102; dx = 0.1; y0 = 29.9; ny = 82; dy = 0.1; zbottom = -500
    
    # obstructions
    x = hilowCellsFactor*lresObstrX + 5
    obstrsxs = (np.ones(80)*x).astype(int)
    obstrsys = (np.arange(0, 80, 1) + 1).astype(int)
    
    # generation of synthetic case data
    grdSpc = gridSpec(name = 'testHR', x0 = x0, nx = nx, dx = dx, y0 = y0, ny = ny, dy = dy, zbottom = zbottom)
    grdSpc.boundaryYs = [i for i in range(ny)]
    grdSpc.boundaryXs = [0 for i in range(ny)]
    grdSpc.customNameList = "&PRO3 WDTHCG = 0.5, WDTHTH = 0.5 /"
    syntGridManager = syntheticGridManager(grdSpc)
    od = pointsObstacleDrawer()
    od.setXY(xs = obstrsxs, ys = obstrsys)
    syntGridManager.obstacleDrawers.append(od)
    _, hiresMask = syntGridManager.generateBathyData()
    hiresAlpha = np.array(hiresMask)
    hiresAlpha[hiresAlpha > 1] = 1
    
    hiresxs = x0 + np.arange(nx)*dx
    hiresys = y0 + np.arange(ny)*dy
    hrmtx = hiResAMtx(hiresxs, hiresys, hiresAlpha)
    ##################################
    
    # DEFINITION OF LOW RES GRID
    x0 = 4.2; nx = 13; dx = 0.8; y0 = 29.2; ny = 12; dy = 0.8; zbottom = -500
    # grid
    rectGridBuilder = abRectangularGridBuilder(x0, y0, dx, dy, nx, ny, minXYIsCentroid=False)
    cstClDet = self.getMockHiResAlphaMtxAndCstCellDet()
    grid = rectGridBuilder.buildGrid(hrmtx, cstClDet)
    
    locAlphaBetaExpFile = os.path.join(self.locpath, 'integrityTest/obstructions_local.syntheticCase07.in')
    shdAlphaBetaExpFile = os.path.join(self.locpath, 'integrityTest/obstructions_shadow.syntheticCase07.in')
    self._testIntegrity(locAlphaBetaExpFile, shdAlphaBetaExpFile, grid, hrmtx, nParWorker)

  def testSyntheticCase07_totalBlock_serial(self):
    self._testSyntheticCase07_totalBlock(1)

  def testSyntheticCase07_totalBlock_parallel(self):
    self._testSyntheticCase07_totalBlock(4)

if __name__ == '__main__':
  unittest.main()
