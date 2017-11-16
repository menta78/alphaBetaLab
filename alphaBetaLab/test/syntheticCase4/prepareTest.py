import os
import shutil
mdlDirName = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.append(os.path.join(os.path.abspath(mdlDirName), '../../'))
sys.path.append(os.path.join(os.path.abspath(mdlDirName), '../wwiiiSyntheticGridManager'))
from wwiiiSyntheticGridManager import *

from abRectangularGridBuilder import abRectangularGridBuilder
from abHighResAlphaMatrix import *
from abEstimateAndSave import *

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

casename = 'case4swellonly'
casedisplname = 'case 4'
outputDir = os.path.join(mdlDirName, 'output')
outputGridDir = os.path.join(outputDir, 'grid')
advObstrOutputDir = os.path.join(outputDir, 'obstructions')
stdObstrOutputDir = os.path.join(outputDir, 'grid')

directions = np.linspace(0, 2*np.pi, 25)[:-1]
freqs = np.array([0.066667*1.1**i for i in range(25)])

highResGridName = 'test'
lowResGridName = 'tst_crs'

try:
  os.mkdir(outputDir)
except:
  pass
try:
  os.mkdir(outputGridDir)
except:
  pass
try:
  os.mkdir(advObstrOutputDir)
except:
  pass
try:
  os.mkdir(stdObstrOutputDir)
except:
  pass


# DEFINITION OF HIGH RES GRID
x0 = 4.9; nx = 102; dx = 0.1; y0 = 29.9; ny = 82; dy = 0.1; zbottom = -500

# generation of synthetic case data
grdSpc = gridSpec(name = highResGridName, x0 = x0, nx = nx, dx = dx, y0 = y0, ny = ny, dy = dy, zbottom = zbottom)
grdSpc.boundaryYs = [i for i in range(ny)]
grdSpc.boundaryXs = [0 for i in range(ny)]
grdSpc.customNameList = "&PRO3 WDTHCG = 0.5, WDTHTH = 0.5 /"
syntGridManager = syntheticGridManager(grdSpc)
od = pointsObstacleDrawer()
od.setXY(xs = obstrsxs, ys = obstrsys)
syntGridManager.obstacleDrawers.append(od)
syntGridManager.saveWWIIIGridFiles(outputGridDir)
_, hiresMask = syntGridManager.generateBathyData()
hiresAlpha = np.array(hiresMask)
hiresAlpha[hiresAlpha > 1] = 1

hiresxs = x0 + np.arange(nx)*dx
hiresys = y0 + np.arange(ny)*dy
hresSyntGrdMng = syntGridManager
##################################


# DEFINITION OF LOW RES GRID
x0 = 4.2; nx = 13; dx = 0.8; y0 = 29.2; ny = 12; dy = 0.8; zbottom = -500
# grid
rectGridBuilder = abRectangularGridBuilder(x0, y0, dx, dy, nx, ny)
grid = rectGridBuilder.buildGrid()

grdSpc = gridSpec(name = lowResGridName, x0 = x0, nx = nx, dx = dx, y0 = y0, ny = ny, dy = dy, zbottom = zbottom)
grdSpc.boundaryYs = [i for i in range(ny)]
grdSpc.boundaryXs = [0 for i in range(ny)]
grdSpc.customNameList = "&PRO3 WDTHCG = 0.5, WDTHTH = 0.5 /"
syntGridManager = syntheticGridManager(grdSpc)
syntGridManager.saveWWIIIGridFiles(outputGridDir)
loresxs = x0 + np.arange(nx)*dx
loresys = y0 + np.arange(ny)*dy



print('plotting grids')
from matplotlib import pyplot as plt
_, msk = hresSyntGrdMng.generateBathyData()
plt.pcolor(hiresxs, hiresys, msk)
minLresX, maxLresX = min(loresxs), max(loresxs)
xs = np.array([minLresX, maxLresX, maxLresX, minLresX, minLresX])
minLresY, maxLresY = min(loresys), max(loresys)
ys = np.array([minLresY, minLresY, maxLresY, maxLresY, minLresY])
plt.plot(xs, ys, 'r')
plt.xlim(minLresX - dx, maxLresX + dx)
plt.ylim(minLresY - dy, maxLresY + dy)
plt.gca().set_xticks(loresxs)
plt.gca().set_yticks(loresys)
plt.grid('on')
plt.show()

# saving alpha/beta/obstruction files
abEstimateAndSave(directions, freqs, grid, hiresxs, hiresys, hiresAlpha, advObstrOutputDir, stdObstrOutputDir, lowResGridName,\
                  savePropSchemeFile = True)
#################################




