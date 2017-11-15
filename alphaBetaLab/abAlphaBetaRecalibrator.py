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

