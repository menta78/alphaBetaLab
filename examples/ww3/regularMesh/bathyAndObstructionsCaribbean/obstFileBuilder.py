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

# low-left and up-right corners of the sub-portion of the domain, where alphaBetaLab is applied
# if not sppecified, the system works on the whole domain
llcrnr = [-100, 5]
urcrnr = [-55, 30]

# creating the options for the algorithm.
opt = abOptions(llcrnr=llcrnr, urcrnr=urcrnr)
# instruction to do the computation and save the output
abEstimateAndSaveRegularEtopo1(dirs, freqs, gridname, regularGridSpec, etopoFilePath, outputDestDir, nParWorker, opt)

