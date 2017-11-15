import sys
import time
from itertools import izip
import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits import basemap as bm
import matplotlib.transforms

from .. import abWwiiiAlphaBetaLoader


class abAlphaBetaSingleCellPlotter:

  def __init__(self, directions, dirmeasure = 'rad', alphaColor = 'red', betaColor = 'blue'):
    self.directions = directions
    self.dirmeasure = dirmeasure # can be deg
    self.alphaColor = alphaColor
    self.betaColor = betaColor

  def plotCell(self, cellPoly, ax, color = 'darkgreen', linewidth = 2):
    bnd = cellPoly.boundary.coords[:]
    x = [p[0] for p in bnd]
    y = [p[1] for p in bnd]
    ax.plot(x, y, color = color, linewidth = linewidth)


  def plot(self, alphaByDir, betaByDir, ax = None, axesPosition = (0, 0, 1, 1)):
    assert len(alphaByDir.shape) == 1, 'abAlphaBetaPlotter: only direction-varying alpha and beta are supported'

    drs = self.directions
    a = alphaByDir
    b = betaByDir
    if ax is None:
      ax = plt.axes(axesPosition, polar = True)
    if drs[0] != drs[-1]:
      drs = np.concatenate([drs, [drs[0]]])
      a = np.concatenate([a, [a[0]]])
      b = np.concatenate([b, [b[0]]])
   
    drsRad = drs/180.*np.pi if self.dirmeasure == 'deg' else drs
    ddr = drsRad[1] - drsRad[0]
    drsRad = drsRad - ddr
    ax.bar(drsRad, b, color = self.betaColor, linewidth = 0)
    ax.bar(drsRad, a, color = self.alphaColor,linewidth = 0)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_ylim([0, 1])
    ax.axis('off')
    ax.plot(0, 0, color = 'k', marker = '.')
    ax.plot(drsRad, np.ones(drsRad.shape), linewidth = .5, color = 'k')




class abAlphaBetaMeshPlotter:


  def __init__(self, coords, geoCoords, alphaList, betaList, mesh, dirs, lonlims = None, latlims = None, 
               cstLineRes = 'i', verbose = True, mp = None):
    """
    abAlphaBetaMeshPlotter: class to plot a mesh, and on each cell a polar plot of alpha and beta.
    It works only for alpha/beta changing with the sole direction, not with frequency.
    geoCoords: list of tuples with the coordinates of the polar diagrams (the baricenter of each cell)
    alphaList, betaList: list of alpha and beta. Must be of the same length al geoCoords.
    mesh: object representing the mesh, as an abGrid instance.
    dirs: list of directions.
    lonlims/latlims: allow to plot a subset of the grid.
    cstLineRes: resolution of coastline.
    """
    self.coords = coords
    self.geoCoords = geoCoords
    self.alphaList = alphaList
    self.betaList = betaList
    self.mesh = mesh
    self.lonlims = lonlims
    self.latlims = latlims
    self.mp = mp
    self.figsize = [14, 8]
    self.figdpi = 80
    self.polarDiagLatSize = .05
    self.dirs = dirs
    self.cstLineRes = cstLineRes
    self.dirmeasure = 'rad'
    self.betaColor = 'blue'
    self.alphaColor = 'red'
    self.cellColor = 'darkgreen'
    self.mainAxesPosition = [0, 0, 1, 1]
    self.landColor = 'palegreen'
    self.seaColor = 'lightblue'
    self.margin = 1 #if a cell has the centroid closer that 1 deg from the plot boundary, it is not plot
    self.nPlottedCells = None #if != None, only the first cells are plotted. Useful for debug
    self.verbose = verbose


  def _print(self, msg):
    if self.verbose:
      print(msg)

  def _getLonLatLims(self):
    if self.lonlims is None:
      lons = [c[0] for c in self.geoCoords]
      lonlims = [min(lons), max(lons)]
    else:
      lonlims = self.lonlims
    if self.latlims is None:
      lats = [c[1] for c in self.geoCoords]
      latlims = [min(lats), max(lats)]
    else:
      latlims = self.latlims
    return lonlims, latlims

  def _getBaseMap(self, lonlims, latlims):
    if self.mp is None:
      self._print('generating basemap ...')
      mp = bm.Basemap(llcrnrlon = lonlims[0], llcrnrlat = latlims[0], urcrnrlon = lonlims[1], urcrnrlat = latlims[1], resolution = self.cstLineRes)
      self.mp = mp
    else:
      mp = self.mp
    return mp
    

  def plotMap(self, ax, lonlims = None, latlims = None):
    if lonlims is None:
      lonlims, latlims = self._getLonLatLims()

    mp = self._getBaseMap(lonlims, latlims)
    mp.drawcoastlines(linewidth = .5, ax = ax)
    mp.fillcontinents(color = self.landColor, ax = ax)
    mp.drawmapboundary(fill_color = self.seaColor, ax = ax)


  def plot(self, ax = None, plotMap = True, lonlims = None, latlims = None):
    if ax is None:
      fig = plt.figure(figsize = self.figsize, dpi = self.figdpi)
      mainAx = fig.gca()
      axCreated = True
    else:
      mainAx = ax
      fig = mainAx.figure
      axCreated = False
      
    dirs = self.dirs
    mesh = self.mesh
    mrgn = self.margin
    nPlottedCells = self.nPlottedCells

    abPlotter = abAlphaBetaSingleCellPlotter(directions = self.dirs, dirmeasure = self.dirmeasure, 
                                   alphaColor = self.alphaColor, betaColor = self.betaColor)
    if lonlims is None:
      lonlims, latlims = self._getLonLatLims()
    else:
      self.lonlims, self.latlims = lonlims, latlims

    if plotMap: self.plotMap(mainAx, lonlims, latlims)

    if axCreated: 
      mainAx.set_position(self.mainAxesPosition)
    else:
      pos = mainAx.get_position()
      mainAx.set_position([0, 0, .1, .1])
      fig.canvas.draw()
      mainAx.set_position(pos)
      fig.canvas.draw()

    mp = self._getBaseMap(lonlims, latlims)
    fig.canvas.draw()
    maPos = mainAx.get_position().get_points().flatten()
    xratio = (maPos[2] - maPos[0])/(lonlims[1] - lonlims[0])
    yratio = (maPos[3] - maPos[1])/(latlims[1] - latlims[0])

    icl = 0
    ncl = len(self.coords)
    axs = []
    self._print('plotting ' + str(ncl) + ' cells ...')
    for crd, geocrd, a, b in izip(self.coords, self.geoCoords, self.alphaList, self.betaList):
      if (not nPlottedCells is None) and (icl >= nPlottedCells):
        break
      ix, iy = crd[0], crd[1]
      lon, lat = geocrd[0], geocrd[1]
      if not ( (lonlims[0] + mrgn <= lon <= lonlims[1] - mrgn) and (latlims[0] + mrgn <= lat <= latlims[1] - mrgn) ):
        continue

      sys.stdout.write('\r{p:2.2f} % '.format(p = float(icl)/ncl*100.))
      sys.stdout.flush()

      mpx, mpy = mp(lon, lat)
      figX = maPos[0] + (mpx - lonlims[0])*xratio
      figY = maPos[1] + (mpy - latlims[0])*yratio
      axDiagLatSize = self.polarDiagLatSize
      axDiagLonSize = self.polarDiagLatSize*self.figsize[1]/self.figsize[0]
      ax = plt.axes([figX - axDiagLonSize/2., figY - axDiagLatSize/2., axDiagLonSize, axDiagLatSize], polar = True)  
      ax.plot(0, 0, marker = '.', color = 'k')
      crdii = (crd[0] - 1, crd[1] - 1)
      if mesh.cellMap.has_key(crdii):
        cellPoly = mesh.cellMap[(crd[0] - 1, crd[1] - 1)]
        abPlotter.plotCell(cellPoly, mainAx, color = self.cellColor)
        abPlotter.plot(a, b, ax = ax)
      icl += 1
      axs.append(ax)

    plt.axes(mainAx)
    return fig, mainAx, axs


  def plotLegend(self, ax, lon, lat, figLegendSize = .2, fontsize = 10):
    lonlims, latlims = self._getLonLatLims()
    mp = self._getBaseMap(lonlims, latlims)
    ax.figure.canvas.draw()
    maPos = ax.get_position().get_points().flatten()
    xratio = (maPos[2] - maPos[0])/(lonlims[1] - lonlims[0])
    yratio = (maPos[3] - maPos[1])/(latlims[1] - latlims[0])
    mpx, mpy = mp(lon, lat)
    figX = maPos[0] + (mpx - lonlims[0])*xratio
    figY = maPos[1] + (mpy - latlims[0])*yratio
    axDiagLatSize = figLegendSize
    axDiagLonSize = figLegendSize*self.figsize[1]/self.figsize[0]
    lgndax = plt.axes([figX - axDiagLonSize/2., figY - axDiagLatSize/2., axDiagLonSize, axDiagLatSize], polar = True)  
    
    abPlotter = abAlphaBetaSingleCellPlotter(directions = self.dirs, dirmeasure = self.dirmeasure, 
                                   alphaColor = self.alphaColor, betaColor = self.betaColor)
    lgndB = np.ones(self.dirs.shape)
    lgndA = lgndB/2.5
    abPlotter.plot(lgndA, lgndB, ax = lgndax)
    lgndax.text(0, 0, '$\\alpha$', horizontalalignment = 'center', verticalalignment = 'center', fontsize = fontsize)
    lgndax.text(1.5*np.pi, .70, '$\\beta$', horizontalalignment = 'center', verticalalignment = 'center', fontsize = fontsize)
    return lgndax



def plotLocalShadowFigure(abLocalFileName, abShadowFileName, mesh, dirs, nfreq, pltlonlims, pltlatlims, figsize = [7, 8], ifreq = 0, **kwargs):
  """
  DOES NOT WORK PROPERLY
  """
  ldr = abWwiiiAlphaBetaLoader.abWwiiiAlphaBetaLoader(nfreq)

  ab = ldr.load(abLocalFileName)
  alphaListLoc = [a[ifreq, :] for a in ab.alphaList] 
  betaListLoc = [b[ifreq, :] for b in ab.betaList] 

  plotter = abAlphaBetaMeshPlotter(ab.coords, ab.geoCoords, alphaListLoc, betaListLoc, mesh, dirs, lonlims = pltlonlims, latlims = pltlatlims, **kwargs)
  fig, axes = plt.subplots(nrows=2, ncols=1, figsize=figsize, tight_layout=True, sharex=True)

  plotter.plotMap(axes[0])
  plotter.plotMap(axes[1])
 
  fig.canvas.draw()
  plotter.plot(ax = axes[0], plotMap = False)

  ab = ldr.load(abShadowFileName)
  alphaListShd = [a[ifreq, :] for a in ab.alphaList] 
  betaListShd = [b[ifreq, :] for b in ab.betaList] 

  mp = plotter.mp
  plotter = abAlphaBetaMeshPlotter(ab.coords, ab.geoCoords, alphaListShd, betaListShd, mesh, dirs, lonlims = pltlonlims, latlims = pltlatlims, **kwargs)
  plotter.mp = mp
  plotter.plot(ax = axes[1], plotMap = False)
  
  


def createMeshPlotterFromFile(abFileName, mesh, dirs, nfreq, ifreq = 0, **kwargs):
  ldr = abWwiiiAlphaBetaLoader.abWwiiiAlphaBetaLoader(nfreq)
  ab = ldr.load(abFileName)

  alphaList = [a[ifreq, :] for a in ab.alphaList] 
  betaList = [b[ifreq, :] for b in ab.betaList] 

  plotter = abAlphaBetaMeshPlotter(ab.coords, ab.geoCoords, alphaList, betaList, mesh, dirs, **kwargs)
  return plotter


