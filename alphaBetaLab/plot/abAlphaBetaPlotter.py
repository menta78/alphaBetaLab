import sys
import time
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
import mpl_toolkits.axes_grid1.inset_locator as il
from matplotlib.projections import get_projection_class
from matplotlib import gridspec
import matplotlib.transforms
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from .. import abWwiiiAlphaBetaLoader


class abAlphaBetaSingleCellPlotter:

  def __init__(self, directions, dirmeasure = 'rad', alphaColor = 'red', betaColor = [.3, .3, 1]):
    self.directions = directions
    self.dirmeasure = dirmeasure # can be deg
    self.alphaColor = alphaColor
    self.betaColor = betaColor
    self.refLineWidth = 1

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
    ax.plot(drsRad, np.ones(drsRad.shape), linewidth = self.refLineWidth, color = 'k')




class abAlphaBetaMeshPlotter:

  def __init__(self, coords, geoCoords, alphaList, betaList, mesh, dirs, lonlims=None, latlims=None, 
               cstLineRes='i', polarDiagLatSize=.05, margin=1, verbose=True):
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
    self.figsize = [14, 8]
    self.figdpi = 80
    self.polarDiagLatSize = polarDiagLatSize
    self.dirs = dirs
    self.cstLineRes = cstLineRes
    self.dirmeasure = 'rad'
    self.betaColor = [.3, .3, 1]
    self.alphaColor = 'red'
    self.cellColor = 'darkgreen'
    self.mainAxesPosition = [0, 0, 1, 1]
   #self.landColor = 'palegreen'
    self.landColor = 'lightgray'
    self.seaColor = 'lightblue'
    self.margin = margin #if a cell has the centroid closer that 1 deg from the plot boundary, it is not plot
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
    

  def plotMap(self, ax, lonlims = None, latlims = None):
    if lonlims is None:
      lonlims, latlims = self._getLonLatLims()

    ax.coastlines(resolution='10m')
    lnd = cfeature.NaturalEarthFeature('physical', 'land', '10m', facecolor='lightgray')
    lndmsk = ax.add_feature(lnd)
    lndmsk.set_zorder(1)
    return lndmsk


  def plot(self, ax = None, plotMap = True, lonlims = None, latlims = None):
    if ax is None:
      fig = plt.figure(figsize = self.figsize, dpi = self.figdpi)
      ax = plt.axes(projection=ccrs.PlateCarree())

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

    if plotMap: 
      lndmsk = self.plotMap(mainAx, lonlims, latlims)
    else:
      lndmsk = None

    if axCreated: 
      mainAx.set_position(self.mainAxesPosition)
    else:
      pos = mainAx.get_position()
      mainAx.set_position([0, 0, .1, .1])
      fig.canvas.draw()
      mainAx.set_position(pos)
      fig.canvas.draw()

    mainAx.set_xlim(lonlims)
    mainAx.set_ylim(latlims)
    fig.canvas.draw()

    icl = 0
    ncl = len(self.coords)
    axs = []
    self._print('plotting ' + str(ncl) + ' cells ...')
    for crd, geocrd, a, b in zip(self.coords, self.geoCoords, self.alphaList, self.betaList):
      if (not nPlottedCells is None) and (icl >= nPlottedCells):
        break
      ix, iy = crd[0], crd[1]
      lon, lat = geocrd[0], geocrd[1]
      plotPie = ( (lonlims[0] + mrgn <= lon <= lonlims[1] - mrgn) and (latlims[0] + mrgn <= lat <= latlims[1] - mrgn) )
      plotPolygon = ( (lonlims[0] - 3 <= lon <= lonlims[1] + 3) and (latlims[0] - 3 <= lat <= latlims[1] + 3) )
      if (not plotPie) and (not plotPolygon):
        continue

      sys.stdout.write('\r{p:2.2f} % '.format(p = float(icl)/ncl*100.))
      sys.stdout.flush()

      crdii = (crd[0] - 1, crd[1] - 1)
      if crdii in mesh.cellMap:
        cellPoly = mesh.cellMap[(crd[0] - 1, crd[1] - 1)]
        if plotPolygon:
          abPlotter.plotCell(cellPoly, mainAx, color = self.cellColor)
        if plotPie:
          xy0 = mainAx.transData.transform((lon, lat))
          axDiagLatSize = self.polarDiagLatSize
          axDiagLonSize = self.polarDiagLatSize*self.figsize[1]/self.figsize[0]
          bbox = [lon-axDiagLonSize/2., lat-axDiagLatSize/2., axDiagLonSize, axDiagLatSize]
          ax = il.inset_axes(mainAx, '100%', '100%', bbox_to_anchor=bbox, bbox_transform=mainAx.transData, 
                borderpad=0, axes_class=get_projection_class("polar"))
          ax.plot(0, 0, marker = '.', color = 'k')
          abPlotter.plot(a, b, ax = ax)
      icl += 1
      axs.append(ax)

    plt.axes(mainAx)
    return fig, mainAx, axs, lndmsk


  def plotLegend(self, ax, lon, lat, figLegendSize=.2, fontsize=10):
    ax.figure.canvas.draw()

    xy0 = ax.transData.transform((lon, lat))
    axDiagLatSize = figLegendSize
    axDiagLonSize = figLegendSize*self.figsize[1]/self.figsize[0]
    bbox = [lon-axDiagLonSize/2., lat-axDiagLatSize/2., axDiagLonSize, axDiagLatSize]
    lgndax = il.inset_axes(ax, '100%', '100%', bbox_to_anchor=bbox, bbox_transform=ax.transData, 
            borderpad=0, axes_class=get_projection_class("polar"))
    
    abPlotter = abAlphaBetaSingleCellPlotter(directions = self.dirs, dirmeasure = self.dirmeasure, 
                                   alphaColor = self.alphaColor, betaColor = self.betaColor)
    lgndB = np.ones(self.dirs.shape)
    lgndA = lgndB/2.5
    abPlotter.plot(lgndA, lgndB, ax=lgndax)
   #lgndax.text(1.5*np.pi, .2, r'$\alpha (\leq \beta)$', horizontalalignment='center', verticalalignment='center', fontsize=fontsize)
    lgndax.text(1.5*np.pi, .2, r'$\alpha$', horizontalalignment='center', verticalalignment='center', fontsize=fontsize)
    lgndax.text(1.5*np.pi, .70, r'$\beta$', horizontalalignment='center', verticalalignment='center', fontsize=fontsize)
    lgndax.plot([.5*np.pi, .5*np.pi], [0, 1], linewidth=2, color='k')
    lgndax.text(0, .17, '0', fontsize=fontsize)
    lgndax.text(np.pi/2.*(7./8.), .9, '1', fontsize=fontsize)
    lgndax.plot(0, 0, marker='o', color='k')
    lgndax.plot(np.pi/2, .99, marker='o', color='k')
    
    return lgndax



def plotLocalShadowFigure(abLocalFileName, abShadowFileName, mesh, dirs, nfreq, pltlonlims, pltlatlims, figsize=[7, 8], ifreq=0, axes=None, **kwargs):
  """
  Plot both local and shadow alphas and betas, on 2 different axes
  """
  if axes is None:
    fig = plt.figure(figsize=figsize)
    gs = gridspec.GridSpec(2, 1)
    ax0 = plt.subplot(gs[0, 0], projection=ccrs.PlateCarree())
    ax1 = plt.subplot(gs[1, 0], projection=ccrs.PlateCarree())
    axes = [ax0, ax1]
    plt.tight_layout()
  else:
    fig = axes[0].gcf()

  ldr = abWwiiiAlphaBetaLoader.abWwiiiAlphaBetaLoader(nfreq)

  ab = ldr.load(abLocalFileName)
  alphaListLoc = [a[ifreq, :] for a in ab.alphaList] 
  betaListLoc = [b[ifreq, :] for b in ab.betaList] 

  plotter = abAlphaBetaMeshPlotter(ab.coords, ab.geoCoords, alphaListLoc, betaListLoc, mesh, dirs, lonlims = pltlonlims, latlims = pltlatlims, **kwargs)
 
  fig.canvas.draw()
  _, _, _, lndmskLocal = plotter.plot(ax = axes[0])

  ab = ldr.load(abShadowFileName)
  alphaListShd = [a[ifreq, :] for a in ab.alphaList] 
  betaListShd = [b[ifreq, :] for b in ab.betaList] 

  plotter = abAlphaBetaMeshPlotter(ab.coords, ab.geoCoords, alphaListShd, betaListShd, mesh, dirs, lonlims = pltlonlims, latlims = pltlatlims, **kwargs)
  _, _, _, lndmskShadow = plotter.plot(ax = axes[1])
  plt.tight_layout()
  return fig, axes, (lndmskLocal, lndmskShadow)
  
  


def createMeshPlotterFromFile(abFileName, mesh, dirs, nfreq, ifreq = 0, **kwargs):
  ldr = abWwiiiAlphaBetaLoader.abWwiiiAlphaBetaLoader(nfreq)
  ab = ldr.load(abFileName)

  alphaList = [a[ifreq, :] for a in ab.alphaList] 
  betaList = [b[ifreq, :] for b in ab.betaList] 

  plotter = abAlphaBetaMeshPlotter(ab.coords, ab.geoCoords, alphaList, betaList, mesh, dirs, **kwargs)
  return plotter


