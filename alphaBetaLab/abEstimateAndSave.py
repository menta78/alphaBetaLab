import os
import numpy as np
import time

import abHighResAlphaMatrix
import abCellsEstimator
import abCellsEstimatorParallel
import abWwiiiObstrFileSaver
import abWwiiiPropSchObstrFileSaver
from abOptionManager import getOption, printOpts
import abEtopo1BathyLoader
import abRectangularGridBuilder
import abCoastalCellDetector
import abFiniteElementsMesh
from abFiniteElementsGridBuilder import abFiniteElementsGridBuilder




################################################################
##### IMPLEMENTATION ON REGULAR GRIDS ##########################
################################################################

def regularGridSpecWW3(xmin=0, dx=0, nx=0, ymin=0, dy=0, ny=0, maskFilePath=''):
  """
  regularGridSpecWWIII:
  contains all the specifications necessary to the creation 
  of an abGrid object based on a regular grid.
  The mask is a matrix ny x nx with value 1 on sea cells, and 0 on land cells.
  Here it is loaded from the mask file produced by gridgen
  """
  class specClass:
    pass
  rs = specClass()
  rs.xmin, rs.ymin = xmin, ymin
  rs.dx, rs.dy = dx, dy
  rs.nx, rs.ny = nx, ny
  
  # loading the mask from the wwiii mask file produced by gridgen
  mask = np.zeros([ny, nx])
  fl = open(maskFilePath)
  ix = 0
  for ln in fl:
    if ix >= nx:
      raise Exception('regularGridSpecWWIII: wrong mask file: lon dimension does not match')
    vlStrs = ln.strip(' \n').split()
    vls = [int(s) for s in vlStrs]
    mask[ix, :] = vls
    ix += 1
  rs.mask = mask
  return rs

def abEstimateAndSaveRegularEtopo1(dirs, freqs, gridName, regularGridSpec, etopo1FilePath, outputDirectory, nParWorker, abOptions = None):
  """
  abEstimateAndSaveRegularEtopo1:
  This method does:

  - build an instance of _abGrid from the input regularGridSpec object (that represents 
    the logical structure of a latlon mesh, and can be generated with the regularGridSpecWW3 function)
  - build an instance of highResolutionBathyMatrix from etopo1
  - invoke _abEstimateAndSave like abEstimateAndSaveRegularEtopo1 does
  """
  
  # instatiating the builder of abGrid object for regular grids
  r = regularGridSpec
  xmin, ymin = r.xmin, r.ymin
  dx, dy = r.dx, r.dy
  nx, ny = r.nx, r.ny
  mask = r.mask
  regGridBld = abRectangularGridBuilder.abRectangularGridBuilder(xmin, ymin, dx, dy, nx, ny, mask, nParWorker = nParWorker)

  # building the high resolution matrix of alpha based on etopo1
  llcrnr = getOption(abOptions, 'llcrnr', None)
  urcrnr = getOption(abOptions, 'urcrnr', None)
  zlim = -.1
  print('loading etopo1 bathymetry ...')
  x, y, z = abEtopo1BathyLoader.loadBathy(etopo1FilePath, llcrnr, urcrnr)
  alphamtx = np.ones(z.shape)
  alphamtx[z > zlim] = 0
  highResolutionBathyMatrix = abHighResAlphaMatrix.abHighResAlphaMatrix(x, y, alphamtx)

  # creating the detector of the cells located along the coasts of big coastal bodies.
  # These bodies are resolved correctly by the model, and do not need subscale modelling
  coastalCellDetector = abCoastalCellDetector.abCoastalCellDetector(abOptions)

  # creating the grid object (where each cell is represented as a polygon)
  grid = regGridBld.buildGrid(highResolutionBathyMatrix, coastalCellDetector)

  _abEstimateAndSave(dirs, freqs, gridName, grid, highResolutionBathyMatrix, outputDirectory, nParWorker, abOptions)

################################################################
################################################################
################################################################




################################################################
##### IMPLEMENTATION ON FINITE ELEMET MESHES ##################
################################################################
feMeshSpecFromGr3File = abFiniteElementsMesh.loadFromGr3File

def abEstimateAndSaveFiniteElementsEtopo1(dirs, freqs, gridName, feMeshSpec, etopo1FilePath, outputDirectory, nParWorker, abOptions = None):
  """
  abEstimateAndSaveFiniteElementsEtopo1: 
  This method does:
  - build an instance of _abGrid from the input feMeshSpec object (that should represent 
    the logical structure of a triangular mesh, and should be loaded, for example, from a gmesh file)
  - build an instance of highResolutionBathyMatrix from etopo1
  - invoke _abEstimateAndSave like abEstimateAndSaveRegularEtopo1 does
  """
  
  gridBld = abFiniteElementsGridBuilder(feMeshSpec, nParWorker = nParWorker)
  grid = gridBld.buildGrid()

  llcrnr = getOption(abOptions, 'llcrnr', None)
  urcrnr = getOption(abOptions, 'urcrnr', None)
  zlim = -.1
  print('loading etopo1 bathymetry ...')
  x, y, z = abEtopo1BathyLoader.loadBathy(etopo1FilePath, llcrnr, urcrnr)
  alphamtx = np.ones(z.shape)
  alphamtx[z > zlim] = 0
  highResolutionBathyMatrix = abHighResAlphaMatrix.abHighResAlphaMatrix(x, y, alphamtx)


  _abEstimateAndSave(dirs, freqs, gridName, grid, highResolutionBathyMatrix, outputDirectory, nParWorker, abOptions)

################################################################
################################################################
################################################################





################################################################
##### IMPLEMENTATION ON SMC GRIDS ##############################
################################################################

def abEstimateAndSaveSMCEtopo1(dirs, freqs, gridName, smcGridSpec, etopo1FilePath, outputDirectory, nParWorker, abOptions = None):
  """
  abEstimateAndSaveSMCEtopo1:
  this is a stub for a to-be-implemented method.
  This method should:

  - build an instance of _abGrid from the input smcGridSpec object (that should represent 
    the logical structure of a smc mesh, and should be loaded from the smc configuration files)
  - build an instance of highResolutionBathyMatrix from etopo1
  - invoke _abEstimateAndSave like abEstimateAndSaveRegularEtopo1 does
  """
  
  # instatiating the builder of abGrid object for regular grids
  r = GridSpec
  xmin, ymin = r.xmin, r.ymin
  dx, dy = r.dx, r.dy
  nx, ny = r.nx, r.ny
  mask = r.mask
  #THE MODULE abSmcGridBuilder, that should convert a smc grid into a list of polygons, still needs to be implemented
  gridBld = abSmcGridBuilder.abSmcGridBuilder(smcGridSpec, nParWorker = nParWorker)

  # building the high resolution matrix of alpha based on etopo1
  llcrnr = getOption(abOptions, 'llcrnr', None)
  urcrnr = getOption(abOptions, 'urcrnr', None)
  zlim = -.1
  print('loading etopo1 bathymetry ...')
  x, y, z = abEtopo1BathyLoader.loadBathy(etopo1FilePath, llcrnr, urcrnr)
  alphamtx = np.ones(z.shape)
  alphamtx[z > zlim] = 0
  highResolutionBathyMatrix = abHighResAlphaMatrix.abHighResAlphaMatrix(x, y, alphamtx)

  # creating the detector of the cells located along the coasts of big coastal bodies.
  # These bodies are resolved correctly by the model, and do not need subscale modelling
  coastalCellDetector = abCoastalCellDetector.abCoastalCellDetector(abOptions)

  # creating the grid object (where each cell is represented as a polygon)
  grid = gridBld.buildGrid(highResolutionBathyMatrix, coastalCellDetector)

  _abEstimateAndSave(dirs, freqs, gridName, grid, highResolutionBathyMatrix, outputDirectory, nParWorker, abOptions)

################################################################
################################################################
################################################################









def _abEstimateAndSave(dirs, freqs, gridName, grid, highResolutionBathyMatrix, outputDirectory, nParWorker, abOptions=None):
  """
  _abEstimateAndSave:
  computes all that is needed by alphaBetaLab, given:
  - a spectral grid (dirs, freqs)
  - a spatial mesh (gridName, grid, that is an abGrid object containing a list of polygons)
  - a high resolution matrix of alpha, got from a high resolution bathymetry
  - outputDirectory, directory to save the output files.
  """

  saveLocalOnly = getOption(abOptions, 'saveLocalOnly', False)
  savePropSchemeFile = getOption(abOptions, 'savePropSchemeFile', False)

  parallel = nParWorker > 1
  advObstrLocFileName = 'obstructions_local.' + gridName + '.in'
  advObstrShdFileName = 'obstructions_shadow.' + gridName + '.in'

  advObstrLocFilePath = os.path.join(outputDirectory, advObstrLocFileName)
  advObstrShdFilePath = os.path.join(outputDirectory, advObstrShdFileName)

  t = time.time()

  try:
    cellEst = abCellsEstimator.abCellsEstimator(grid, highResolutionBathyMatrix, dirs, freqs, abOptions)
    if parallel:
      cellEstP = abCellsEstimatorParallel.abCellsEstimatorParallel(cellEst, nParWorker, abOptions)
      cellEst.grid.buildNeighCache()
      locParams = cellEstP.computeLocalAlphaBeta()
      if not saveLocalOnly:
        shdParams = cellEstP.computeShadowAlphaBeta()
      else:
        shdParams = None, None, None, None, None
    else:
      locParams = cellEst.computeLocalAlphaBeta()
      if not saveLocalOnly:
        shdParams = cellEst.computeShadowAlphaBeta()
      else:
        shdParams = None, None, None, None, None
    locCoords, locAlphas = locParams[0], locParams[2]

    try:
      os.makedirs(outputDirectory)
    except:
      pass

    wwiiiObstrFileSaver = abWwiiiObstrFileSaver.abWwiiiObstrFileSaver(*(locParams + shdParams))
    if saveLocalOnly:
      wwiiiObstrFileSaver.saveLocFile(advObstrLocFilePath)
    else:
      wwiiiObstrFileSaver.saveFiles(advObstrLocFilePath, advObstrShdFilePath)
  
    if savePropSchemeFile:
      stdObstrFileName = gridName + '.obstr_lev1'
      stdObstrFilePath = os.path.join(propSchemeObstrDestDir, stdObstrFileName)
      propSchObstrFileSaver = abWwiiiPropSchObstrFileSaver.\
               abWwiiiPropSchObstrFileSaver(grid, dirs, locCoords, locAlphas)
      propSchObstrFileSaver.saveFile(stdObstrFilePath)
  finally:
    timeElapsed = time.time() - t
    print('Complete. Time elapsed in seconds: ' + str(timeElapsed))
    print
    printOpts()


