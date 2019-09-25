import os
import shutil
mdlDirName = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.append(os.path.join(os.path.abspath(mdlDirName), '../../'))
sys.path.append(os.path.join(os.path.abspath(mdlDirName), '../wwiiiSyntheticGridManager'))
from wwiiiSyntheticGridManager import *
from dummyWindGenerator import *

highResGridName = 'test'
lowResGridName = 'tst_crs'

winddir = 'wind'
try:
  os.mkdir(winddir)
except:
  pass

# HIGH RES GRID
x0 = 4.9; nx = 102; dx = 0.1; y0 = 29.9; ny = 82; dy = 0.1; zbottom = -500

grdSpc = gridSpec(name = highResGridName, x0 = x0, nx = nx, dx = dx, y0 = y0, ny = ny, dy = dy, zbottom = zbottom)

wg = dummyWindGenerator(grdSpc)
wg.saveWWIIIWindFiles(winddir)


# DEFINITION OF LOW RES GRID
x0 = 4.2; nx = 13; dx = 0.8; y0 = 29.2; ny = 12; dy = 0.8; zbottom = -500
# grid
grdSpc = gridSpec(name = lowResGridName, x0 = x0, nx = nx, dx = dx, y0 = y0, ny = ny, dy = dy, zbottom = zbottom)

wg = dummyWindGenerator(grdSpc)
#wg.firstXUW = wg.uw/4.
wg.firstxuw = 0
wg.secondxuw = 9.4
wg.saveWWIIIWindFiles(winddir)

