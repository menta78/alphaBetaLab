import numpy as np

from . import abUtils

def getDefaultFactors(meshType):
  locRecFct = 1.
  shdRecFct = 1.2
  if meshType == abUtils.MESHTYPE_TRIANGULAR:
    fct = 2.0
    locRecFct = locRecFct*fct
    shdRecFct = shdRecFct*fct
  return locRecFct, shdRecFct
  

class abAlphaBetaRecalibrator:
  def __init__(self, obstFactor = 1.1):
    self.obstFactor = obstFactor

  def recalibrate(self, alpha):
    fctr = self.obstFactor
    recAlpha = 1 - (1 - alpha)*fctr
    if recAlpha < 0:
      recAlpha = 0
    elif recAlpha > 1:
      recAlpha = 1
    return recAlpha

