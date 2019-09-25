import sys
import traceback
import numpy as np
from shapely import geometry as g

from . import abSingleCellAlphaEstimator as aEst
from . import abSingleCellBetaEstimator as bEst
from . import abUpstreamPolyEstimator as upe
from . import abCellSize as csEst
from . import abUtils
from . import abLongBreakWaterLocAlphaAdjust as bwAdj
#import cProfile
from .abOptionManager import getOption

defaultVerbose = True
defaultShadowAlphaAlleviationParam = .83
defaultAlleviationMaxBlockedNeighborCount = 1

class abCellsEstimator:
 
  def __init__(self, grid, alphaMtx, dirs, freqs, options):
    """
    abCellsEstimator: evaluates local dissipation alpha and beta for the whole grid.
    Methods computeLocalAlphaBeta computeShadowAlphaBeta returns: 
     - coords: a list of the indexes of the obstructed cells
     - geoCoords: a list of the geographical coords of the obstructed cells
     - alphas/betas: lists of alpha/beta by freq/direction
     - sizes: list of cell size by direction
    """
    self.grid = grid
    self.alphaMtx = alphaMtx
    self.dirs = dirs
    self.freqs = freqs
    self.shadowAlphaAlleviationParam = defaultShadowAlphaAlleviationParam
    self.shadowAlleviationMaxBlockedNeighborCount = defaultAlleviationMaxBlockedNeighborCount
    self.shadowKShape = 1
    self.totallyBlockedCells = None
    self.localAlphasReady = False
    self.postMortemDebug = False
    self.minAvgAlpha, self.minAvgBeta = .1, .2
    self.verbose = getOption(options, 'verbose', True)
    self.computationDirs = getOption(options, 'computationDirs', 
                                  np.linspace(0, 2*np.pi, 9)[:-1])
    self.betaMaxSubSections = getOption(options, 'betaMaxSubSections', 10)
    self.locRecalibFactor = getOption(options, 'locRecalibFactor', 1.)
    self.shadRecalibFactor = getOption(options, 'shadRecalibFactor', 1.2)
    self.longBreakWaterAdjust = getOption(options, 'longBreakWaterAdjust', False)
    self.highResCoastalPolygons = getOption(options, 'highResCoastalPolygons', [])

    timeStep = float(getOption(options, 'timeStep', 0.))
    cgMax = 9.8/(4.*np.pi*min(freqs))
    self.minSizeKm = getOption(options, 'minSizeKm', cgMax*timeStep/1000.)
    if self.longBreakWaterAdjust and len(self.highResCoastalPolygons) == 0:
      raise abException("abCellsEstimator: if longBreakWaterAdjust is enabled, highResCoastalPolygons should not be empty")

  def _progress(self, percent):
    if self.verbose:
      sys.stdout.write('\r  progress: {:2.1f} %'.format(percent))
      sys.stdout.flush()

  def _print(self, msg = ''):
    if self.verbose:
      print(msg)




  ###############################################################
  ########## BLOCK OF COMPUTATION OF LOCAL ALPHA-BETA ###########
  ######################### START ###############################
  def computeLocalOneCell(self, crd, geoCrd, cell):
    try:
      cellAlphaMtx = self.alphaMtx.getAlphaSubMatrix(cell)
      cellMtxCoversCell = cellAlphaMtx.coversPoly()
      localAlphaBetaExist = not cellAlphaMtx.empty()
      onLand = cellAlphaMtx.onLand()
      if cellMtxCoversCell and localAlphaBetaExist and not onLand:
        alphaEst = aEst.abSingleCellAlphaEstimator(cell, cellAlphaMtx, recalibFactor = self.locRecalibFactor)
        alphaEst.loginfo.debugPlotSave = True
        alphaEst.loginfo.contextStrs = ['local']
        betaEst = bEst.abSingleCellBetaEstimator(cell, cellAlphaMtx, 
                          recalibFactor = self.locRecalibFactor,
                          maxSubSections = self.betaMaxSubSections)
        cellSizeEst = csEst.abCellSize(cell)
        cellSizes = cellSizeEst.computeSizesKm(self.dirs)
        if min(cellSizes) < self.minSizeKm:
          return False, None, None, None, False, None, None, cell
        lalpha = []
        lbeta = []
        totallyBlocked = False
        if self.alphaMtx.hasFreqs:
          raise abUtils.abException('alpha high resolution matrix with frequencies unsupported')
        else:
          fqalpha0 = []
          fqbeta0 = []
          f = self.freqs[0]
          #for d in self.dirs:
          for d in self.computationDirs:
            a = alphaEst.computeAlpha(d, f)
            fqalpha0.append(a)
            b = betaEst.computeBeta(d, f)
            fqbeta0.append(b)
            totallyBlocked = totallyBlocked or abUtils.isClose(a, 0)
          fqalpha = np.interp(self.dirs, self.computationDirs, fqalpha0, period = 2*np.pi)
          fqbeta = np.interp(self.dirs, self.computationDirs, fqbeta0, period = 2*np.pi)
          lalpha = [fqalpha for f in self.freqs]
          lbeta = [fqbeta for f in self.freqs]
        meanAlpha = np.mean(lalpha)
        meanBeta = np.mean(lbeta)
        if (meanAlpha < 1.) and (meanAlpha > self.minAvgAlpha and meanBeta > self.minAvgBeta):
          return True, lalpha, lbeta, cellSizes, totallyBlocked, crd, geoCrd, cell
        else:
          # This cell is on land. The resolved component of the model should take care of this
          return False, None, None, None, False, None, None, cell
      else:
        return False, None, None, None, False, None, None, cell
    except:
      raise abUtils.abException("".join(traceback.format_exception(*sys.exc_info())))

  def initLocAlphaBetaOutput(self):
    coords = []
    geoCoords = []
    alphas = []
    betas = []
    sizes = []
    obstructedCells = []
    totallyBlockedCells = {}
    return coords, geoCoords, alphas, betas, sizes, totallyBlockedCells, obstructedCells

  def updateLocAlphaBetaOutput(self, locAlphaBetaOutput, singleCellLocAlphaBetaOutput):
    locAlphaBetaExist, lalpha, lbeta, cellSizes, totallyBlocked, crd, geoCrd, cell = singleCellLocAlphaBetaOutput
    coords, geoCoords, alphas, betas, sizes, totallyBlockedCells, cells = locAlphaBetaOutput
    if locAlphaBetaExist:
      alphas.append(np.array(lalpha))
      betas.append(np.array(lbeta))
      coords.append(crd)
      geoCoords.append(geoCrd)
      sizes.append(cellSizes)
      cells.append(cell)
      if totallyBlocked:
        cell = self.grid.cellMap[crd]
        cltpl = tuple(cell.boundary.coords[:])
        totallyBlockedCells[cltpl] = cell

  def _longBreakWaterLocAdjust(self, obstrCells, grid, highResCoastalPolygons, alphas, betas, parallel = True, nParallelWorker = 4):
    self._print('reviewing estimated local alphas in presence of long breakwaters ...')
    lbwLocAlphaAdjust = bwAdj.abLongBreakWaterLocAlphaAdjustAllCells(obstrCells, grid, highResCoastalPolygons, self.dirs, alphas, betas, parallel, nParallelWorker)
    adjAlphas, adjBetas = lbwLocAlphaAdjust.reviewLocalAlpha()
    self._print('... done')
    self._print('')
    return adjAlphas, adjBetas

  def computeLocalAlphaBeta(self):
    alphaBetaOutput = self.initLocAlphaBetaOutput()

    self._print()
    self._print('computing local')
    allGeoCoords = self.grid.getGeoCoords()
    for i, crd, geoCrd, cell in zip(range(len(allGeoCoords)),\
                    self.grid.cellCoordinates, allGeoCoords, self.grid.cells):
      prog = float(i)/len(allGeoCoords)*100.
      self._progress(prog)
      singleCellLocAlphaBetaOutput = self.computeLocalOneCell(crd, geoCrd, cell)
      self.updateLocAlphaBetaOutput(alphaBetaOutput, singleCellLocAlphaBetaOutput)
    coords, geoCoords, alphas, betas, sizes, totallyBlockedCells, obstrcells = alphaBetaOutput
    
    self.totallyBlockedCells = totallyBlockedCells
    self._print()
    self._print('... done')
    self._print()

    if self.longBreakWaterAdjust:
      alphas, betas = self._longBreakWaterLocAdjust(obstrcells, self.grid, self.highResCoastalPolygons, alphas, betas, parallel = False)    

    self.localAlphasReady = True
    return coords, geoCoords, alphas, betas, sizes
  ######################### END #################################
  ########## BLOCK OF COMPUTATION OF LOCAL ALPHA-BETA ###########
  ###############################################################





  ###############################################################
  ########## BLOCK OF COMPUTATION OF SHADOW ALPHA-BETA ##########
  ######################### START ###############################
  def computeShadowOneCell(self, crd, geoCrd, cell):
    try:
      cellNeighbors = self.grid.getNeighbors(cell)
      if not len(cellNeighbors):
        self._print('cell ' + str(crd) + ' has no neighbors. Skipping')
        return False, None, None, None, None, None
        
      neighTotPoly = cell
      for p in cellNeighbors:
        neighTotPoly = neighTotPoly.union(p)
      if neighTotPoly.__class__ != g.Polygon:
        neighTotPoly = neighTotPoly.convex_hull - cell
      if neighTotPoly.__class__ != g.Polygon:
        self._print('cell ' + str(crd) + ': impossible to estimate neighboring polygon. Skipping')
        return False, None, None, None, None, None
      totPolyAlphaMtx = self.alphaMtx.getAlphaSubMatrix(neighTotPoly)
      shadAlphaBetaExist =  not totPolyAlphaMtx.isNull() and not totPolyAlphaMtx.empty()
      onLand = totPolyAlphaMtx.onLand() if shadAlphaBetaExist else False
      if shadAlphaBetaExist and not onLand:
        lalpha0 = []
        lbeta0 = []
        blockedCellCount = sum([1 for cl in cellNeighbors if tuple(cl.boundary.coords[:]) in self.totallyBlockedCells])
        obstrAlleviationEnabled = blockedCellCount <= self.shadowAlleviationMaxBlockedNeighborCount
        cellSizeEst = csEst.abCellSize(cell)
        cellSizes = cellSizeEst.computeSizesKm(self.dirs)
        if min(cellSizes) < self.minSizeKm:
          return False, None, None, None, None, None
        for dr in self.computationDirs:
          upstreamPoly = upe.getUpstreamPoly(cell, neighTotPoly, dr)
          upstreamPolyIsPolygon = upstreamPoly.__class__ == g.Polygon
          if upstreamPolyIsPolygon and (not abUtils.isClose(upstreamPoly.area, 0)):
            alphaEst = aEst.abSingleCellAlphaEstimator(upstreamPoly, self.alphaMtx, cell,\
                 kshape = self.shadowKShape, obstrAlleviationParam = self.shadowAlphaAlleviationParam, recalibFactor = self.shadRecalibFactor)
            alphaEst.obstrAlleviationEnabled = obstrAlleviationEnabled
            alphaEst.loginfo.debugPlotSave = False
            alphaEst.loginfo.contextStrs = ['shadow']
            betaEst = bEst.abSingleCellBetaEstimator(upstreamPoly, self.alphaMtx, kshape = self.shadowKShape, recalibFactor = self.shadRecalibFactor)
            betaEst.obstrAlleviationEnabled = obstrAlleviationEnabled
            diralpha = []
            lalpha0.append(diralpha)
            dirbeta = []
            lbeta0.append(dirbeta)
            if self.alphaMtx.hasFreqs:
              raise abUtils.abException('alpha high resolution matrix with frequencies unsupported')
             #for fq in self.freqs:
             #  alpha = alphaEst.computeAlpha(dr, fq)
             #  diralpha.append(alpha)
             #  beta = max(betaEst.computeBeta(dr, fq), alpha)
             #  dirbeta.append(beta)
            else:
              fq = self.freqs[0]
              alpha = alphaEst.computeAlpha(dr, fq) if not alphaEst.alphaMtx.nullOrEmpty() else 1
              diralpha.extend([alpha for f in self.freqs])
              beta = max(betaEst.computeBeta(dr, fq), alpha) if not betaEst.alphaMtx.nullOrEmpty() else 1
              dirbeta.extend([beta for f in self.freqs])
          else:
            alpha, beta = 1, 1
            diralpha = [alpha for f in self.freqs]
            dirbeta = [beta for f in self.freqs]
            lalpha0.append(diralpha)
            lbeta0.append(dirbeta)

        lalpmtx0 = np.array(lalpha0).transpose()
        lbetmtx0 = np.array(lbeta0).transpose()

        lalpha, lbeta = [], []
        for alparr, betarr in zip(lalpmtx0, lbetmtx0):
          alp = np.interp(self.dirs, self.computationDirs, alparr, period = 2*np.pi)
          lalpha.append(alp)
          bet = np.interp(self.dirs, self.computationDirs, betarr, period = 2*np.pi)
          lbeta.append(bet)

        lalpmtx = np.array(lalpha)
        lbetmtx = np.array(lbeta)

        meanAlpha = np.mean(lalpmtx)
        if meanAlpha < 1.:
          return True, lalpmtx, lbetmtx, cellSizes, crd, geoCrd
        else:
          return False, None, None, None, None, None
      else:
        return False, None, None, None, None, None
    except:
      raise abUtils.abException("".join(traceback.format_exception(*sys.exc_info())))

  def initShdAlphaBetaOutput(self):
    coords = []
    geoCoords = []
    alphas = []
    betas = []
    sizes = []
    return coords, geoCoords, alphas, betas, sizes

  def updateShdAlphaBetaOutput(self, shdAlphaBetaOutput, singleCellShdAlphaBetaOutput):
    shdAlphaBetaExist, lalpmtx, lbetmtx, cellSizes, crd, geoCrd = singleCellShdAlphaBetaOutput
    coords, geoCoords, alphas, betas, sizes = shdAlphaBetaOutput
    if shdAlphaBetaExist:
      alphas.append(lalpmtx)
      betas.append(lbetmtx)
      coords.append(crd)
      geoCoords.append(geoCrd)
      sizes.append(cellSizes)

  def computeShadowAlphaBeta(self):
    if not self.localAlphasReady:
      raise abUtils.abException('computeShadowAlphaBeta must be invoked after computeLocalAlphaBeta')

    try:
      alphaBetaOutput = self.initShdAlphaBetaOutput()
      self._print()
      self._print('computing shadow')
      allGeoCoords = self.grid.getGeoCoords()
      for i, crd, geoCrd, cell in zip(range(len(allGeoCoords)),\
                      self.grid.cellCoordinates, allGeoCoords, self.grid.cells):
        prog = float(i)/len(allGeoCoords)*100.
        self._progress(prog)
        
        singleCellShdAlphaBetaOutput = self.computeShadowOneCell(crd, geoCrd, cell)
        self.updateShdAlphaBetaOutput(alphaBetaOutput, singleCellShdAlphaBetaOutput)
      self._print()
      self._print('... done')
      self._print()
      return alphaBetaOutput
    except:
      raise
      
  ######################### END #################################
  ########## BLOCK OF COMPUTATION OF SHADOW ALPHA-BETA ##########
  ###############################################################
            
    
            
