from matplotlib import pyplot as plt
import numpy as np

def polyPlot(poly, doplot = False):
  xs = np.array([c[0] for c in poly.boundary.coords[:]])
  ys = np.array([c[1] for c in poly.boundary.coords[:]])
  minx, maxx, dx = min(xs), max(xs), (max(xs) - min(xs))/len(xs)
  miny, maxy, dy = min(ys), max(ys), (max(ys) - min(ys))/len(ys)
  plt.plot(xs, ys)
  plt.xlim([minx - dx, maxx + dx])
  plt.ylim([miny - dy, maxy + dy])
  
  if doplot:
    plt.show()

