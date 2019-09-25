import unittest
import os, shutil
import numpy as np
from shapely import geometry as g

from alphaBetaLab.abEstimateAndSave import triMeshSpecFromGr3File, abEstimateAndSaveTriangularEtopo1


class testAbEstimateAndSaveTriangular(unittest.TestCase):

   
  def testEstimateAndSave0(self):
    mdldir = os.path.dirname( os.path.abspath(__file__) )
    mshFilePath = os.path.join(mdldir, 'triangularMeshTest/hgridGiamaica.gr3')
    etopoFilePath = os.path.join(mdldir, 'triangularMeshTest/etopo1_testGiamaica.nc')
    outdir = os.path.join(mdldir, 'triangularMeshTest/testOut/')
    
    triMeshSpec = triMeshSpecFromGr3File(mshFilePath)

    dirs = np.linspace(0, 2*np.pi, 25)
    nfreq = 25
    minfrq = .04118
    frqfactor = 1.1
    freqs = [minfrq*(frqfactor**i) for i in range(1,nfreq + 1)]

    nParWorker = 4

    abEstimateAndSaveTriangularEtopo1(dirs, freqs, 'testGiamaica', triMeshSpec, etopoFilePath, outdir, nParWorker, None)
 
    self.assertTrue(os.path.isfile(os.path.join(outdir, 'obstructions_local.testGiamaica.in')))
    self.assertTrue(os.path.isfile(os.path.join(outdir, 'obstructions_shadow.testGiamaica.in')))
    shutil.rmtree(outdir)


if __name__ == '__main__':
  unittest.main()
