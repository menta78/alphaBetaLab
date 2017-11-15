import abc
import numpy as np
import os
import shutil

class sgmException(Exception):
  pass

class gridSpec:
  def __init__(self, name = '', x0 = 0, nx = 0, dx = 0, y0 = 0, ny = 0,\
               dy = 0, zbottom = 0, spgridstring = '1.1  0.066667  25  24  0.'):
    """
    gridSpec class contains the macro definition of the HIGH RESOLUTION bathymetry grid:
    nx, ny, dx, dy, x0, y0 and the depth zbottom.
    """
    if name == '':
      raise sgmException('name parameter is mandatory')
    if len(name) > 7:
      raise sgmException('name should be 7 characters max')
    self.name = name
    self.x0 = x0
    self.nx = nx
    self.dx = dx
    self.y0 = y0
    self.ny = ny
    self.dy = dy
    self.zbottom = zbottom
    self.zbottomConfFactor = 0.001
    self.spgridstring = spgridstring
    self.customNameList = ''
    self.boundaryXs = []
    self.boundaryYs = []



class abstractObstacleDrawer:

  def setGrid(self, gridSpec, bathymetryBase, maskBase):
    self.gridSpec = gridSpec
    self.bathymetryBase = bathymetryBase
    self.maskBase = maskBase

  @abc.abstractmethod
  def drawObstacle(self):
    pass



class pointsObstacleDrawer(abstractObstacleDrawer):
  
  def __init__(self):
    self.xs = None
    self.ys = None

  def setXY(self, xs = (), ys = ()):
    self.ys = ys
    self.xs = xs

  def drawObstacle(self):
    if not self.xs is None:
      self.bathymetryBase[self.ys, self.xs] = 0.
      self.maskBase[self.ys, self.xs] = 0.



class syntheticGridManager:
  def __init__(self, gridSpec):
    self.obstacleDrawers = []
    self.gridSpec = gridSpec

  def _getGridDataText(self, griddata, factor = 1):
    txt = ''
    for dtrow in griddata:
      strs = [str(int(round(dt * factor, 0))) for dt in dtrow]
      txt += '  '.join(strs) + '\n'
    return txt.strip('\n')
 
  def getGridFileName(self, gridname):
    return 'ww3_grid.inp.' + gridname

  def getBathyFileName(self, gridname):
    return gridname + '.depth_ascii'

  def getObstrFileName(self, gridname):
    return gridname + '.obstr_lev1'

  def getMaskFileName(self, gridname):
    return gridname + '.mask'

  def generateBaseBathyData(self):
    baseBathy = np.ones((self.gridSpec.ny, self.gridSpec.nx)) * self.gridSpec.zbottom
    baseMask = np.ones((self.gridSpec.ny, self.gridSpec.nx))
    return baseBathy, baseMask

  def generateBathyData(self):
    """
    Returns 2 arrays ny x nx (nx and ny are given by gridSpec):
        -> the bathymetry
        -> the mask (0 if sea point, 1 if earth point)
    """
    bathy, mask = self.generateBaseBathyData()
    for od in self.obstacleDrawers:
      od.setGrid(self.gridSpec, bathy, mask)
      od.drawObstacle()
    mask[bathy >= 0] = 0.
    for bndx, bndy in zip(self.gridSpec.boundaryXs, self.gridSpec.boundaryYs):
      mask[bndy, bndx] = 2
    return bathy, mask
      
  def buildGridFile(self, fl):
    """
    Builds wwiii grid file
    """
    lines = """\
$ -------------------------------------------------------------------- $
$ WAVEWATCH III Grid preprocessor input file                           $
$ -------------------------------------------------------------------- $
$
"""
    fl.write(lines)
    fl.write("'" + self.gridSpec.name + "'\n")
    lines = """\
   {spgridstring}
   F T T T F T
   3600. 100. 900. 10.
""".format(spgridstring = self.gridSpec.spgridstring)
    if self.gridSpec.customNameList:
      lines += "  " + self.gridSpec.customNameList + '\n'
    lines +="""\
  &MISC FLAGTR = 2 /
END OF NAMELISTS
'RECT' T 'NONE'
"""
    fl.write(lines)
    fl.write(str(self.gridSpec.nx) + '\t ' + str(self.gridSpec.ny) + '\n')    
    fl.write(str(self.gridSpec.dx) + '   ' + str(self.gridSpec.dy) + '   1.0\n')
    fl.write(str(self.gridSpec.x0) + '   ' + str(self.gridSpec.y0) + '   1.0\n')
    fl.write("-0.10   2.50  30  " + str(self.gridSpec.zbottomConfFactor)\
           + "  1  1 '(....)'  NAME  '" + self.getBathyFileName(self.gridSpec.name) + "'\n")
    fl.write("40  0.010000  1  1  '(....)'  NAME  '" + self.getObstrFileName(self.gridSpec.name) + "'\n")
    fl.write("50   1   1   '(....)'   NAME '" + self.getMaskFileName(self.gridSpec.name) + "'\n")
    fl.write("     0.    0.    0.    0.       0")

  def buildBathyFile(self, fl):
    """
    Builds wwiii bathy file
    """
    bathy, mask = self.generateBathyData()
    txt = self._getGridDataText(bathy, 1./self.gridSpec.zbottomConfFactor)
    fl.write(txt)

  def buildObstrFile(self, fl):
    """
    Builds wwiii obstruction file
    """
    obstrs = np.zeros((self.gridSpec.ny, self.gridSpec.nx))
    txt = self._getGridDataText(obstrs)
    txt += '\n' + self._getGridDataText(obstrs)
    fl.write(txt)

  def buildMaskFile(self, fl):
    """
    Builds wwiii mask file
    """
    bathy, mask = self.generateBathyData()
    txt = self._getGridDataText(mask)
    fl.write(txt)
  
  def saveWWIIIGridFiles(self, destdir):
    if not os.path.isdir(destdir):
      raise sgmException('directory ' + destdir + ' does not exist')
   
    grdnm = self.gridSpec.name

    fl = open(os.path.join(destdir, self.getGridFileName(grdnm)), 'w')
    self.buildGridFile(fl)
    fl.close()
    
    fl = open(os.path.join(destdir, self.getBathyFileName(grdnm)), 'w')
    self.buildBathyFile(fl)
    fl.close()

    fl = open(os.path.join(destdir, self.getObstrFileName(grdnm)), 'w')
    self.buildObstrFile(fl)
    fl.close()

    fl = open(os.path.join(destdir, self.getMaskFileName(grdnm)), 'w')
    self.buildMaskFile(fl)
    fl.close()
    



