import numpy as np
import os
import time
import platform


# spectra grid: directions and frequencies
dirs = np.linspace(0, 2*np.pi, 25)
nfreq = 25
minfrq = .04118
frqfactor = 1.1
freqs = [minfrq*(frqfactor**i) for i in range(1,nfreq + 1)]

# output directory (the directory of this script + output)
mdlDir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
outputDestDir = os.path.join(mdlDir, 'output')

# msh filename, must be the same as in the ww3 grid file name
mshfile = 'med.msh'
gridname = 'mediterr'

# number of cores for parallel computing
nParWorker = 12

# etopo file path (a different path if I launch from home or from the office)
if platform.node() == 'pcmenta':
  etopoFilePath = '/home/lmentaschi/usr/WaveWatchIII/gridgen1.1/reference_data/etopo1.nc'
elif platform.node() == 'user-VirtualBox':
  etopoFilePath = '/media/sf_DATA/etopo/ETOPO1_Bed_g_gmt4.grd'
else:
  etopoFilePath = '/DATA/etopo/ETOPO1_Bed_g_gmt4.grd'

# low-left and up-right corners of the sub-portion of the domain, where alphaBetaLab is applied
# if not sppecified, the system works on the whole domain



# function that generates the files for uost, invoking abEstimateAndSaveRegularEtopo1
def doBuildObstacleFiles():
  from alphaBetaLab.abOptionManager import abOptions
  from alphaBetaLab.abEstimateAndSave import triMeshSpecFromMshFile, abEstimateAndSaveTriangularEtopo1

  opt = abOptions(timeStep=180)
  triMeshSpec = triMeshSpecFromMshFile('med.msh')
  abEstimateAndSaveTriangularEtopo1(dirs, freqs, gridname, triMeshSpec, etopoFilePath, outputDestDir, nParWorker, opt)



if __name__ == '__main__':
 #import pdb; pdb.set_trace()
  doBuildObstacleFiles()



