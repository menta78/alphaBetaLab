import numpy as np
import os

from .abUtils import *

try:
  from scipy.interpolate import RegularGridInterpolator
except:
  raise abException('abWwiiiGridFilesCompiler: scipy version should be >= 0.14')


class abWwiiiGridFilesCompiler:

  
  def __init__(self, xs, ys, zs, inverseZ = False, verbose = True):
    self.xs = np.array(xs)
    self.ys = np.array(ys)
    self.zs = np.array(zs) if not inverseZ else -np.array(zs)
    self.zsFactor = .001
    self.verbose = verbose

  def _print(self, msg):
    if self.verbose:
      print(msg)

  def interpolateGrid(self, minx, maxx, dx, miny, maxy, dy):
    xs, ys, zs = self.xs, self.ys, self.zs
    ipxs = np.arange(minx, maxx, dx)
    ipys = np.arange(miny, maxy, dy)
    ipxsm, ipysm = np.meshgrid(ipxs, ipys)
    pts = np.array([ipysm.flatten(), ipxsm.flatten()]).transpose()
    interpFunction = RegularGridInterpolator((ys, xs), zs)
    ipzs = interpFunction(pts)
    ipzs = ipzs.reshape((len(ipys), len(ipxs)))
    return ipys, ipxs, ipzs

    
  def generateMetaFileLines(self, gridname, grdx, grdy):
    lines = []
    firstLines = '$ Define grid ' + gridname + ' $\n'
    firstLines += """$ Four records containing :
$  1 NX, NY. As the outer grid lines are always defined as land
$    points, the minimum size is 3x3.
$  2 Grid increments SX, SY (degr.or m) and scaling (division) factor.
$    If NX*SX = 360., latitudinal closure is applied.
$  3 Coordinates of (1,1) (degr.) and scaling (division) factor.
$  4 Limiting bottom depth (m) to discriminate between land and sea
$    points, minimum water depth (m) as allowed in model, unit number
$    of file with bottom depths, scale factor for bottom depths (mult.),
$    IDLA, IDFM, format for formatted read, FROM and filename.
'RECT' T 'NONE'
"""
    lines.append(firstLines)
    lines.append(str(len(grdx)) + '\t  ' + str(len(grdy)) + '\n')
    dx = abs(grdx[1] - grdx[0])
    dy = abs(grdy[1] - grdy[0])
    lines.append(str(dx) + '\t  ' + str(dy) + '\t  1\n')
    lines.append(str(min(grdx)) + '\t  ' + str(min(grdy)) + '\t  1\n')
    lines.append('-0.10   2.50  20  ' + str(self.zsFactor) + '  1  1 \'(....)\'  NAME  \'' + gridname + '.depth_ascii\'\n')
    lines.append('$ Sub-grid information\n')
    lines.append('30  0.010000  1  1  \'(....)\'  NAME  \'' + gridname + '.obstr_lev1\'')
    return lines


  def generateBathyFileLines(self, grdx, grdy, grdz):
    grdz = grdz/self.zsFactor
    dx = abs(grdx[1] - grdx[0])
    dy = abs(grdy[1] - grdy[0])
    if dx < 0:
      grdz = grdz[:,::-1]
    if dy < 0:
      grdz = grdz[::-1,:]
    lines = []
    for vls in grdz:
      vls[np.isnan(vls)] = 0
      ln = '   '.join('{v:2.0f}'.format(v = v) for v in vls) + '\n'
      lines.append(ln)
    return lines


  def generateObstrLevFileLines(self, grdx, grdy, grdz):
    grdz = grdz*self.zsFactor
    dx = abs(grdx[1] - grdx[0])
    dy = abs(grdy[1] - grdy[0])
    if dx < 0:
      grdz = grdz[:,::-1]
    if dy < 0:
      grdz = grdz[::-1,:]
    lines = []
    for i in range(2):
      # doing this twice: for x and y components
      for vls in grdz:
        ln = '   '.join('0' for v in vls) + '\n'
        lines.append(ln)
    return lines


  def generateMaskOrigFileLines(self, grdx, grdy, grdz):
    msk = np.ones(grdz.shape)
    msk[grdz > 0] = 0
    msk[np.isnan(grdz)] = 0
    lines = []
    for vls in msk:
      ln = '   '.join(str(int(v)) for v in vls) + '\n'
      lines.append(ln)
    return lines
     

  def generateFiles(self, gridname, minx, maxx, dx, miny, maxy, dy, outputdir):
    if len(gridname) > 10:
      raise abException('grid name is too long! Should be 10 characters max')
    self._print('interpolating ...')
    grdy, grdx, grdz = self.interpolateGrid(minx, maxx, dx, miny, maxy, dy)

    self._print('... saving metadata file')
    lines = self.generateMetaFileLines(gridname, grdx, grdy)
    oflpath = os.path.join(outputdir, gridname + '.meta')
    ofl = open(oflpath, 'w')
    ofl.writelines(lines)
    ofl.close()

    self._print('... saving bathymetry file')
    lines = self.generateBathyFileLines(grdx, grdy, grdz)
    oflpath = os.path.join(outputdir, gridname + '.depth_ascii')
    ofl = open(oflpath, 'w')
    ofl.writelines(lines)
    ofl.close()

    self._print('... saving (empty) obstruction file')
    lines = self.generateObstrLevFileLines(grdx, grdy, grdz)
    oflpath = os.path.join(outputdir, gridname + '.obstr_lev1')
    ofl = open(oflpath, 'w')
    ofl.writelines(lines)
    ofl.close()

    self._print('... saving mask file')
    lines = self.generateMaskOrigFileLines(grdx, grdy, grdz)
    oflpath = os.path.join(outputdir, gridname + '.mask')
    ofl = open(oflpath, 'w')
    ofl.writelines(lines)
    ofl.close()
    
