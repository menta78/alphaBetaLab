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

import abSingleCellAlphaEstimator
abSingleCellAlphaEstimator.debugPlots = False


casename = 'case11swellonly'
casedisplname = 'case 11'
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
x0obs = hilowCellsFactor*lresObstrX + 4
xs = np.array([x0obs, x0obs + 1, x0obs + 2])
y0obs = hilowCellsFactor*5 + 4
ys = np.array([y0obs, y0obs + 1, y0obs + 2])

obstrsxs, obstrsys = np.meshgrid(xs, ys)
obstrsxs = obstrsxs.astype(int).flatten()
obstrsys = obstrsys.astype(int).flatten()

lresXBoundaryCondLimit = lresObstrX - 1

# generation of synthetic case data
grdSpc = gridSpec(name = highResGridName, x0 = x0, nx = nx, dx = dx, y0 = y0, ny = ny, dy = dy, zbottom = zbottom)
grdSpc.boundaryYs = [i for i in range(ny)]
grdSpc.boundaryYs.extend([0 for i in range(lresXBoundaryCondLimit*hilowCellsFactor)])
grdSpc.boundaryXs = [0 for i in range(ny)]
grdSpc.boundaryXs.extend([i for i in range(lresXBoundaryCondLimit*hilowCellsFactor)])
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
rectGridBuilder = abRectangularGridBuilder(x0, y0, dx, dy, nx, ny)
grid = rectGridBuilder.buildGrid()

grdSpc = gridSpec(name = lowResGridName, x0 = x0, nx = nx, dx = dx, y0 = y0, ny = ny, dy = dy, zbottom = zbottom)
grdSpc.boundaryYs = [i for i in range(ny)]
grdSpc.boundaryYs.extend([0 for i in range(lresXBoundaryCondLimit)])
grdSpc.boundaryXs = [0 for i in range(ny)]
grdSpc.boundaryXs.extend([i for i in range(lresXBoundaryCondLimit)])
grdSpc.customNameList = "&PRO3 WDTHCG = 0.5, WDTHTH = 0.5 /"
syntGridManager = syntheticGridManager(grdSpc)
syntGridManager.saveWWIIIGridFiles(outputGridDir)
# saving alpha/beta/obstruction files
abEstimateAndSave(directions, freqs, grid, hiresxs, hiresys, hiresAlpha, advObstrOutputDir, stdObstrOutputDir, lowResGridName,\
                  savePropSchemeFile = True)
#################################




