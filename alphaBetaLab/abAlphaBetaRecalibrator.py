import numpy as np

from . import abUtils

def getDefaultFactors(meshType):
  locRecFct = 1.
  #this value compensates the limit of alphaBetaLab algo to represent
  #a diagonal shadow distributed in many cells
  shdRecFct = 1.2
  if meshType == abUtils.MESHTYPE_TRIANGULAR:
    #0.75 is the ratio between the surface of an exagon and the enclosing rectangle
    fct = 1/np.sqrt(.75)
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

