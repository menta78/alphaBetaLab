# -*- coding: utf-8 -*-
import os
from matplotlib import pyplot as plt
import numpy as np

from alphaBetaLab.plot import abAlphaBetaPlotter
import obstFileBuilder


def plotOutAlphaBeta2Figs(plotFigureLocal = True, plotFigureShadow = True):
  moddir = os.path.dirname(os.path.abspath(__file__))
  outPlotLocalAlphaBetaFile = os.path.join(moddir, 'fig/locAlphaBeta.png')
  outPlotShadowAlphaBetaFile = os.path.join(moddir, 'fig/shadAlphaBeta.png')

  pltlonlims = (-99, -58)
  pltlatlims = (7, 32)

  hResAlphaMtx = obstFileBuilder.getHighResAlphas()
  mesh = obstFileBuilder.getLowResGrid(hResAlphaMtx)
  dirs = obstFileBuilder.dirs
  nfreq = obstFileBuilder.nfreq 
 
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
    plotter.plotLegend(ax, -63, 27, fontsize = 30)
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


def plotOutAlphaBeta1Fig():
  moddir = os.path.dirname(os.path.abspath(__file__))
  outPlotFile = os.path.join(moddir, 'fig/alphaBeta.png')

  pltlonlims = (-99, -58)
  pltlatlims = (7, 32)

  hResAlphaMtx = obstFileBuilder.getHighResAlphas()
  mesh = obstFileBuilder.getLowResGrid(hResAlphaMtx)
  dirs = obstFileBuilder.dirs
  nfreq = obstFileBuilder.nfreq 
 
  abFileDir = os.path.abspath(os.path.dirname(__file__))
  abLocFileName = os.path.join(abFileDir, 'output', 'obstructions_local.g_glb150.in')
  abShdFileName = os.path.join(abFileDir, 'output', 'obstructions_shadow.g_glb150.in')

  abAlphaBetaPlotter.plotLocalShadowFigure(abLocFileName, abShdFileName, mesh, dirs, nfreq, pltlonlims, pltlatlims)

  fg.savefig(outPlotFile, dpi = 400)
  fg.show()
  
  


if __name__ == '__main__':
  plotOutAlphaBeta()

