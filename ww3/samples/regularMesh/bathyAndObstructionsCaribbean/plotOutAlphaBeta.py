# -*- coding: utf-8 -*-
import os
from matplotlib import pyplot as plt
import numpy as np

from alphaBetaLab.plot import abAlphaBetaPlotter
import obstFileBuilder
from alphaBetaLab import abEtopo1BathyLoader, abHighResAlphaMatrix, abRectangularGridBuilder, abCoastalCellDetector




def getHighResAlphas():
  llcrnr = [-100, 5]
  urcrnr = [-55, 30]

  zlim = -.1
  x, y, z = abEtopo1BathyLoader.loadBathy(obstFileBuilder.etopoFilePath, llcrnr, urcrnr)
  alphamtx = np.ones(z.shape)
  alphamtx[z > zlim] = 0
  return abHighResAlphaMatrix.abHighResAlphaMatrix(x, y, alphamtx)




def getLowResGrid(hiResAlphaMtx):
  dx, dy = 1.5, 1.5
  minX, minY = -180, -70
  nx, ny = 240, 94

  def getMask():
    msk = np.zeros([ny, nx])
    fl = open(obstFileBuilder.maskFilePath)
    ix = 0
    for ln in fl:
      if ix >= nx:
        raise Exception('wrong mask file: lon dimension does not match')
      vlStrs = ln.strip(' \n').split()
      vls = [int(s) for s in vlStrs]
      msk[ix, :] = vls
      ix += 1
    return msk
    
  mask = getMask()
  regGridBld = abRectangularGridBuilder.abRectangularGridBuilder(minX, minY, dx, dy, nx, ny, mask, nParWorker = obstFileBuilder.nParWorker)
  coastalCellDetector = abCoastalCellDetector.abCoastalCellDetector(None)
  return regGridBld.buildGrid(hiResAlphaMtx, coastalCellDetector)

  


def plotOutAlphaBeta2Figs(plotFigureLocal = True, plotFigureShadow = True):
  moddir = os.path.dirname(os.path.abspath(__file__))
  outPlotLocalAlphaBetaFile = os.path.join(moddir, 'fig/locAlphaBeta.png')
  outPlotShadowAlphaBetaFile = os.path.join(moddir, 'fig/shadAlphaBeta.png')

  pltlonlims = (-99, -58)
  pltlatlims = (7, 32)

  hResAlphaMtx = getHighResAlphas()
  mesh = getLowResGrid(hResAlphaMtx)
  dirs = np.linspace(0, 2*np.pi, 25)
  nfreq = 25
 
  abFileDir = os.path.abspath(os.path.dirname(__file__))

  def drawMeridianAndParallels():
    meridians = np.arange(-99, -58, 6)
    parallels = np.arange(7, 32, 6)
    mp.drawmeridians(meridians, ax = ax)
    mrdLblLat = 31
    for lon in meridians[1:]:
      x, y = mp(lon, mrdLblLat)
      ax.text(x, y, str(lon), fontsize = 25, ha = 'center')
    prlLblLon = -99
    mp.drawparallels(parallels, ax = ax)
    for lat in parallels[1:]:
      x, y = mp(prlLblLon, lat)
      ax.text(x, y, str(lat), fontsize = 25, va = 'center')

  if plotFigureLocal:
    abLocFileName = os.path.join(abFileDir, 'output', 'obstructions_local.g_glb150.in')
    plotter = abAlphaBetaPlotter.createMeshPlotterFromFile(abLocFileName, mesh, dirs, nfreq, lonlims = pltlonlims, latlims = pltlatlims)
    plotter.nPlottedCells = None
    #plotter.nPlottedCells = 10
    fg, ax, axs = plotter.plot()
    mp = plotter.mp
    drawMeridianAndParallels()
    plotter.plotLegend(ax, -63, 27, fontsize = 25)
    ax.text(-63, 23, 'a', fontsize = 60, horizontalalignment = 'center', verticalalignment = 'center')
    plt.draw()
    fg.savefig(outPlotLocalAlphaBetaFile, dpi = 400, bbox_inches='tight')
    fg.show()

  if plotFigureShadow:
    abShdFileName = os.path.join(abFileDir, 'output', 'obstructions_shadow.g_glb150.in')
    plotter = abAlphaBetaPlotter.createMeshPlotterFromFile(abShdFileName, mesh, dirs, nfreq, lonlims = pltlonlims, latlims = pltlatlims)
    plotter.nPlottedCells = None
    #plotter.nPlottedCells = 10
    fg, ax, axs = plotter.plot()
    mp = plotter.mp
    drawMeridianAndParallels()
    ax.text(-63, 27, 'b', fontsize = 60, horizontalalignment = 'center', verticalalignment = 'center')
    plt.draw()
    fg.savefig(outPlotShadowAlphaBetaFile, dpi = 400, bbox_inches='tight')
    fg.show()


  


if __name__ == '__main__':
  plotOutAlphaBeta2Figs()
  input('Wait for the plots to be ready. When you\'re done press enter')

