import numpy as np

# importing from alphaBetaLab the needed components
from alphaBetaLab.abOptionManager import abOptions
from alphaBetaLab.abEstimateAndSave import abEstimateAndSaveRegularEtopo1, regularGridSpecWW3

# definition of the spectral grid
dirs = np.linspace(0, 2*np.pi, 25)
nfreq = 25
minfrq = .04118
frqfactor = 1.1
freqs = [minfrq*(frqfactor**i) for i in range(1,nfreq + 1)]

# defining the spatial grid
gridname = 'g_glb150'
maskFilePath = gridname + '.mask'
regularGridSpec = regularGridSpecWW3(
        xmin= -180, ymin=-70,
        dx=1.5, dy=1.5,
        nx=240, ny=94,
        maskFilePath=maskFilePath)


# path of the etopo1 bathymetry
etopoFilePath = '/home/lmentaschi/usr/WaveWatchIII/gridgen1.1/reference_data/etopo1.nc'

# output directory
outputDestDir = './output/'

# number of cores for parallel computing
nParWorker = 12
nParWorker = 4

# instruction to do the computation and save the output
# No options are given. The algorithm is launched on the whole domain with the default parameters
abEstimateAndSaveRegularEtopo1(dirs, freqs, gridname, regularGridSpec, etopoFilePath, outputDestDir, nParWorker)

