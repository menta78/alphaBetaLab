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

# gridname, must be the same as in the ww3 grid file name
gridname = 'g_glb150'

# file path of the maskfile generated by gridgen
maskFilePath = os.path.join(mdlDir, gridname + '.mask')

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
#llcrnr = [-100, 5]
#urcrnr = [-55, 30]



# function that generates the files for uost, invoking abEstimateAndSaveRegularEtopo1
def doBuildObstacleFile():
  from alphaBetaLab.abOptionManager import abOptions
  from alphaBetaLab.abEstimateAndSave import abEstimateAndSaveRegularEtopo1, regularGridSpecWW3

 #opt = abOptions(llcrnr=llcrnr, urcrnr=urcrnr)
  opt = abOptions()
  regularGridSpec = regularGridSpecWW3(
        xmin= -180, ymin=-70,
        dx=1.5, dy=1.5,
        nx=240, ny=94,
        maskFilePath=maskFilePath)
  abEstimateAndSaveRegularEtopo1(dirs, freqs, gridname, regularGridSpec, etopoFilePath, outputDestDir, nParWorker, opt)



if __name__ == '__main__':
 #import pdb; pdb.set_trace()
  doBuildObstacleFile()



