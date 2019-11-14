import unittest
import os, shutil
import numpy as np
from shapely import geometry as g
from scipy.interpolate import interp2d

from alphaBetaLab.abOptionManager import abOptions
from alphaBetaLab.abEstimateAndSave import abEstimateAndSaveRegularGebco, abEstimateAndSaveTriangularGebco
from alphaBetaLab.abGebcoBathyLoader import loadBathy
from alphaBetaLab import abTriangularMesh


class testAbEstimateAndSaveGebco(unittest.TestCase):

   
  def _SLOW_testEstimateAndSaveTriangular(self):
    mdldir = os.path.dirname( os.path.abspath(__file__) )
    mshFilePath = os.path.join(mdldir, 'triangularMeshTest/redSea.msh')
    gbcFilePath = os.path.join(mdldir, 'gebco_test.nc')
    outputDestDir = os.path.join(mdldir, 'output')
    
    triMeshSpec = abTriangularMesh.loadFromMshFile(mshFilePath)

    dirs = np.linspace(0, 2*np.pi, 25)
    nfreq = 25
    minfrq = .04118
    frqfactor = 1.1
    freqs = [minfrq*(frqfactor**i) for i in range(1,nfreq + 1)]

    nParWorker = 4

    try:
      llcrnr = [40, 15]
      urcrnr = [41, 16]
      abEstimateAndSaveTriangularGebco(dirs, freqs, 'gebco_test_tr', triMeshSpec, gbcFilePath, outputDestDir, nParWorker, None)
    finally: 
      outFl1 = os.path.join(outputDestDir, 'obstructions_local.gebco_test_tr.in')
      self.assertTrue(os.path.isfile(outFl1))
      outFl2 = os.path.join(outputDestDir, 'obstructions_shadow.gebco_test_tr.in')
      self.assertTrue(os.path.isfile(outFl2))
      try:
        shutil.rmtree(outputDestDir)
      except:
        pass


  def _testEstimateAndSaveRegular(self):
    # importing from alphaBetaLab the needed components
    
    # definition of the spectral grid
    dirs = np.linspace(0, 2*np.pi, 25)
    nfreq = 25
    minfrq = .04118
    frqfactor = 1.1
    freqs = [minfrq*(frqfactor**i) for i in range(1,nfreq + 1)]
    
    # path of the etopo1 bathymetry
    mdldir = os.path.dirname( os.path.abspath(__file__) )
    gbcFilePath = os.path.join(mdldir, 'gebco_test.nc')

    def getMask(xmin, dx, nx, ymin, dy, ny):
      llcrnr = [xmin, ymin]
      urcrnr = [xmin + nx*dx, ymin + ny*dy]
      lon, lat, z = loadBathy(gbcFilePath, llcrnr, urcrnr)
      xs = np.arange(xmin, xmin + nx*dx, dx)
      ys = np.arange(ymin, ymin + ny*dy, dy)
      intp = interp2d(lon, lat, z)
      zintp = intp(xs, ys)
      mask = zintp < 0
      return mask
    
    # output directory
    outputDestDir = os.path.join(mdldir, 'output')
    
    # defining the spatial grid
    gridname = 'gebco_test'
    maskFilePath = gridname + '.mask'
    class _mk:
      pass
    regularGridSpec = _mk()
    regularGridSpec.xmin = 40
    regularGridSpec.ymin = 15
    regularGridSpec.dx = .1
    regularGridSpec.dy = .1
    regularGridSpec.nx = 7
    regularGridSpec.ny = 8
    regularGridSpec.mask = getMask(40, .1, 10, 15, .1, 12)
    
    # number of cores for parallel computing
    nParWorker = 4

    try:
      # instruction to do the computation and save the output
      abEstimateAndSaveRegularGebco(dirs, freqs, gridname, regularGridSpec, gbcFilePath, outputDestDir, nParWorker)
     #abEstimateAndSaveRegularEtopo1(dirs, freqs, gridname, regularGridSpec, gbcFilePath, outputDestDir, nParWorker)
    finally:
      outFl1 = os.path.join(outputDestDir, 'obstructions_local.gebco_test.in')
      self.assertTrue(os.path.isfile(outFl1))
      outFl2 = os.path.join(outputDestDir, 'obstructions_shadow.gebco_test.in')
      self.assertTrue(os.path.isfile(outFl2))
      try:
        shutil.rmtree(outputDestDir)
      except:
        pass



if __name__ == '__main__':
  unittest.main()
