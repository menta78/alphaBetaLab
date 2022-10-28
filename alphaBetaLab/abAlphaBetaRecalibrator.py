import numpy as np

from . import abUtils

def getDefaultFactors(meshType):
  # The computation of the cell size tends to overestimate.
  # To compensate, increasing a bit the obstruction.
  # In the future, a better solution would be to compute 
  # the exact mean path length of the beams in the cell shape.
  locRecFct = 1.
  shdRecFct = 1.2
  if meshType == abUtils.MESHTYPE_TRIANGULAR:
    fct = 1.5
    locRecFct = locRecFct*fct
    shdRecFct = shdRecFct*fct
  return locRecFct, shdRecFct
  

class abAlphaBetaRecalibrator:
  def __init__(self, obstFactor = 1.1):
    self.obstFactor = obstFactor

  def recalibrate(self, alpha):
    fctr = self.obstFactor
    recAlpha = 1 - (1 - alpha)*fctr
    if isinstance(alpha, np.ndarray):
      recAlpha[recAlpha < 0] = 0
      recAlpha[recAlpha > 1] = 1
    else:
      if recAlpha < 0:
        recAlpha = 0
      elif recAlpha > 1:
        recAlpha = 1
    return recAlpha

