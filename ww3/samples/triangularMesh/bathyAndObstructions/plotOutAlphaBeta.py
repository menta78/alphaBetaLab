# -*- coding: utf-8 -*-
import os
from matplotlib import pyplot as plt
import numpy as np

from alphaBetaLab.plot import abAlphaBetaPlotter
import obstFileBuilder
from alphaBetaLab import abEtopo1BathyLoader, abHighResAlphaMatrix, abFiniteElementsMesh, abFiniteElementsGridBuilder




def getHighResAlphas():
  llcrnr = [22.7, 36]
  urcrnr = [27.6, 38.9]

  zlim = -.1
  x, y, z = abEtopo1BathyLoader.loadBathy(obstFileBuilder.etopoFilePath, llcrnr, urcrnr)
  alphamtx = np.ones(z.shape)
  alphamtx[z > zlim] = 0
  return abHighResAlphaMatrix.abHighResAlphaMatrix(x, y, alphamtx)




def getLowResGrid(hiResAlphaMtx):
  mspec = abFiniteElementsMesh.loadFromMshFile('med.msh')
  gridBld = abFiniteElementsGridBuilder.abFiniteElementsGridBuilder(mspec, nParWorker = 4)
  grid = gridBld.buildGrid()
  return grid
  


def plotOutAlphaBeta2Figs(plotFigureLocal = True, plotFigureShadow = True):
  moddir = os.path.dirname(os.path.abspath(__file__))
  outPlotLocalAlphaBetaFile = os.path.join(moddir, 'fig/locAlphaBeta.png')
  outPlotShadowAlphaBetaFile = os.path.join(moddir, 'fig/shadAlphaBeta.png')

  pltlonlims = (22.7, 27.6)
  pltlatlims = (36, 38.9)

  hResAlphaMtx = getHighResAlphas()
  mesh = getLowResGrid(hResAlphaMtx)
  dirs = np.linspace(0, 2*np.pi, 25)
  nfreq = 25
 
  abFileDir = os.path.abspath(os.path.dirname(__file__))

  def drawMeridianAndParallels():
    meridians = np.arange(22, 28, 1)
    parallels = np.arange(36, 39, 1)
    mp.drawmeridians(meridians, ax = ax)
    mrdLblLat = 35.8
    for lon in meridians[1:]:
      x, y = mp(lon, mrdLblLat)
      ax.text(x, y, str(lon), fontsize = 25, ha = 'center')
    prlLblLon = 22.5
    mp.drawparallels(parallels, ax = ax)
    for lat in parallels[1:]:
      x, y = mp(prlLblLon, lat)
      ax.text(x, y, str(lat), fontsize = 25, va = 'center')

  if plotFigureLocal:
    abLocFileName = os.path.join(abFileDir, 'output', 'obstructions_local.mediterr.in')
    plotter = abAlphaBetaPlotter.createMeshPlotterFromFile(abLocFileName, mesh, dirs, nfreq, lonlims=pltlonlims, latlims=pltlatlims)
    plotter.nPlottedCells = None
    plotter.margin = 0
    plotter.cstLineRes = 'f'
    #plotter.nPlottedCells = 10
    fg, ax, axs = plotter.plot()
    mp = plotter.mp
    drawMeridianAndParallels()
   #plotter.plotLegend(ax, -63, 27, fontsize = 25)
    ax.text(-63, 23, 'a', fontsize = 60, horizontalalignment = 'center', verticalalignment = 'center')
    plt.draw()
    import pdb; pdb.set_trace()
    fg.savefig(outPlotLocalAlphaBetaFile, dpi = 400, bbox_inches='tight')
    fg.show()

  if plotFigureShadow:
    abShdFileName = os.path.join(abFileDir, 'output', 'obstructions_shadow.mediterr.in')
    plotter = abAlphaBetaPlotter.createMeshPlotterFromFile(abShdFileName, mesh, dirs, nfreq, lonlims=pltlonlims, latlims=pltlatlims)
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
  plotOutAlphaBeta2Figs(plotFigureShadow=False)
  input('Wait for the plots to be ready. When you\'re done press enter')

