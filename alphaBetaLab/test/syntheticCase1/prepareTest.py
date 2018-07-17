import os
import shutil
mdlDirName = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.append(os.path.join(os.path.abspath(mdlDirName), '../../'))
sys.path.append(os.path.join(os.path.abspath(mdlDirName), '../wwiiiSyntheticGridManager'))
from wwiiiSyntheticGridManager import *

import abRectangularGridBuilder
import abHighResAlphaMatrix
import abEstimateAndSave


casename = 'case1swellonly'
casedisplname = 'case 1'
outputDir = os.path.join(mdlDirName, 'output')
outputGridDir = os.path.join(outputDir, 'grid')
advObstrOutputDir = os.path.join(outputDir, 'obstructions')
stdObstrOutputDir = os.path.join(outputDir, 'grid')

directions = np.linspace(0, 2*np.pi, 25)[:-1]
freqs = np.array([0.066667*1.1**i for i in range(25)])

hilowCellsFactor = 8
lresObstrX = 3

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

# obstructions
x = hilowCellsFactor*lresObstrX + 5
obstrsxs = (np.ones(40)*x).astype(int)
obstrsys = (np.arange(0, 40, 1)*2 + 1).astype(int)

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
##################################


# DEFINITION OF LOW RES GRID
x0 = 4.2; nx = 13; dx = 0.8; y0 = 29.2; ny = 12; dy = 0.8; zbottom = -500
# grid
rectGridBuilder = abRectangularGridBuilder.abRectangularGridBuilder(x0, y0, dx, dy, nx, ny)
grid = rectGridBuilder.buildGrid(None, None)

grdSpc = gridSpec(name = lowResGridName, x0 = x0, nx = nx, dx = dx, y0 = y0, ny = ny, dy = dy, zbottom = zbottom)
grdSpc.boundaryYs = [i for i in range(ny)]
grdSpc.boundaryXs = [0 for i in range(ny)]
grdSpc.customNameList = "&PRO3 WDTHCG = 0.5, WDTHTH = 0.5 /"
syntGridManager = syntheticGridManager(grdSpc)
syntGridManager.saveWWIIIGridFiles(outputGridDir)

highResolutionBathyMatrix = abHighResAlphaMatrix.abHighResAlphaMatrix(hiresxs, hiresys, hiresAlpha)
# saving alpha/beta/obstruction files
abEstimateAndSave._abEstimateAndSave(directions, freqs, lowResGridName, grid, highResolutionBathyMatrix, outputDir, 4, [])
#################################




