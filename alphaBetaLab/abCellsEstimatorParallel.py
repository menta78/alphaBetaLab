import multiprocessing as mp

from . import abCellsEstimator
from .abOptionManager import getOption

"""
parallelFuncLocal: needs to be a global function
to let multiprocessing pickle it automatically to the other processes
"""
def parallelFuncLocal(tpl):
  global cellEst
  crd, geoCrd, cell = tpl
  return cellEst.computeLocalOneCell(crd, geoCrd, cell)

"""
parallelFuncShadow: needs to be a global function
to let multiprocessing pickle it automatically to the other processes
"""
def parallelFuncShadow(tpl):
  #from test.mpPdb import mpPdb; mpPdb().set_trace()
  global cellEst
  crd, geoCrd, cell = tpl
  return cellEst.computeShadowOneCell(crd, geoCrd, cell)

class abCellsEstimatorParallel:

  def __init__(self, cellEst, nParWorker, options):
    self.cellEst = cellEst
    cellEst.grid.nParWorker = nParWorker
    self.nParWorker = nParWorker
    self._progressSkippedSteps = 10
    self.longBreakWaterAdjust = cellEst.longBreakWaterAdjust

  def _initParEnv(self):
    # cellEst needs to be global in order to be automatically
    # pickled to the other processes.
    # this variable needs to be initialized before
    # creating the parallel pool, otherwise the system won't pickle it.
    global cellEst
    cellEst = self.cellEst
    cellEst._print('initializing parallel pool')
    p = mp.Pool(self.nParWorker)
    cellEst._print('... done')
    self.procPool = p
    return p

  def _finalizeParEnv(self):
    cellEst = self.cellEst
    cellEst._print('finalizing parallel pool')
    self.procPool.close()
    del self.procPool
    self.procPool = None
    cellEst._print('... done')

  def computeLocalAlphaBeta(self):
    cellEst = self.cellEst
    cellEst._print('computing local alpha-beta ...')
    allGeoCoords = cellEst.grid.getGeoCoords()
    ncells = float(len(cellEst.grid.cells))

    cellEst._print('  running parallel jobs and')
    cellEst._print('  collecting output to the standard structure')
    alphaBetaOutput = cellEst.initLocAlphaBetaOutput()

    p = self._initParEnv()

    i = 0
    for singleCellLocAlphaBetaOutput in p.imap(parallelFuncLocal, zip(cellEst.grid.cellCoordinates, allGeoCoords, cellEst.grid.cells)):
      cellEst.updateLocAlphaBetaOutput(alphaBetaOutput, singleCellLocAlphaBetaOutput)
      i += 1
      if i % self._progressSkippedSteps == 0:
        prg = i/ncells*100.
        cellEst._progress(prg)

    self._finalizeParEnv()

    cellEst._print('  ... done')
    coords, geoCoords, alphas, betas, sizes, totallyBlockedCells, obstrcells = alphaBetaOutput

    cellEst.totallyBlockedCells = totallyBlockedCells
    cellEst._print('... all done')
    cellEst._print('')

    if self.longBreakWaterAdjust:
      alphas, betas = cellEst._longBreakWaterLocAdjust(obstrcells, cellEst.grid, cellEst.highResCoastalPolygons, alphas, betas, parallel = True, nParallelWorker = self.nParWorker)    

    cellEst.localAlphasReady = True
    return coords, geoCoords, alphas, betas, sizes
    
  def computeShadowAlphaBeta(self):
    cellEst = self.cellEst
    cellEst._print('computing shadow alpha-beta ...')
    allGeoCoords = cellEst.grid.getGeoCoords()
    ncells = float(len(cellEst.grid.cells))

    cellEst._print('  running parallel jobs and')
    cellEst._print('  collecting output to the standard structure')
    alphaBetaOutput = cellEst.initShdAlphaBetaOutput()
    
    cellEst.grid.buildNeighCache();
    """
    parallel environment *needs* to be reinitialized
    because because cellEnv changed because of computeLocalAlphaBeta call,
    and needs to be re-pickled to the processes of the pool
    """
    p = self._initParEnv()
    i = 0
    for singleCellShdAlphaBetaOutput in p.imap(parallelFuncShadow, zip(cellEst.grid.cellCoordinates, allGeoCoords, cellEst.grid.cells)):
      cellEst.updateShdAlphaBetaOutput(alphaBetaOutput, singleCellShdAlphaBetaOutput)
      i += 1
      if i % self._progressSkippedSteps == 0:
        prg = i/ncells*100.
        cellEst._progress(prg)

    self._finalizeParEnv()

    coords, geoCoords, alphas, betas, sizes = alphaBetaOutput
    cellEst._print('  ... done')

    cellEst._print('... all done')
    cellEst._print('')
    return coords, geoCoords, alphas, betas, sizes


