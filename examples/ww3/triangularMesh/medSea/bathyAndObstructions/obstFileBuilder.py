import numpy as np

# importing from alphaBetaLab the needed components
from alphaBetaLab.abOptionManager import abOptions
from alphaBetaLab.abEstimateAndSave import triMeshSpecFromMshFile, abEstimateAndSaveTriangularEtopo1

# definition of the spectral grid
dirs = np.linspace(0, 2*np.pi, 25)
nfreq = 25
minfrq = .04118
frqfactor = 1.1
freqs = [minfrq*(frqfactor**i) for i in range(1,nfreq + 1)]

# definition of the spatial mesh
gridname = 'ww3'
mshfile = 'med.msh'
triMeshSpec = triMeshSpecFromMshFile(mshfile)

# path of the etopo1 bathymetry
etopoFilePath = '/home/lmentaschi/usr/WaveWatchIII/gridgen1.1/reference_data/etopo1.nc'

# output directory
outputDestDir = './output/'

# number of cores for parallel computing
nParWorker = 12
nParWorker = 4

# this option indicates that the computation should be skipped for cells smaller than 3 km
minSizeKm = 3
opt = abOptions(minSizeKm=minSizeKm)

# instruction to do the computation and save the output
abEstimateAndSaveTriangularEtopo1(dirs, freqs, gridname, triMeshSpec, etopoFilePath, outputDestDir, nParWorker)




