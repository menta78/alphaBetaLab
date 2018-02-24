from matplotlib import pyplot as plt
import numpy as np
from shapely import geometry as g

def polyPlot(poly, color='b', doshow=False):
  xs = np.array([c[0] for c in poly.boundary.coords[:]])
  ys = np.array([c[1] for c in poly.boundary.coords[:]])
  minx, maxx, dx = min(xs), max(xs), (max(xs) - min(xs))/len(xs)
  miny, maxy, dy = min(ys), max(ys), (max(ys) - min(ys))/len(ys)
  plt.plot(xs, ys, color=color)
  plt.xlim([minx - dx, maxx + dx])
  plt.ylim([miny - dy, maxy + dy])
  
  if doshow:
    plt.show()

def plotPolyList(polyList, color='b', doshow=False, title=''):
  minx, miny = np.inf, np.inf
  maxx, maxy = -np.inf, -np.inf
  for p in polyList:
    xs = np.array([c[0] for c in p.boundary.coords[:]])
    ys = np.array([c[1] for c in p.boundary.coords[:]])
    plt.plot(xs, ys, color=color)
    minx = min(min(xs), minx)
    maxx = max(max(xs), maxx)
    miny = min(min(ys), miny)
    maxy = max(max(ys), maxy)
  dx = (maxx - minx)/15.
  dy = (maxy - miny)/15.
  plt.xlim([minx - dx, maxx + dx])
  plt.ylim([miny - dy, maxy + dy])
  if title != '':
    plt.title(title)
  
  if doshow:
    plt.show()

def plotFeMesh(nodes, connectionPolygons, doshow=False):
  polyNds = connectionPolygons.values()
  polyList = []
  for nds in polyNds:
    poly = []
    for n in nds:
      poly.append(nodes[n])
    polyList.append(g.Polygon(poly))
  plotPolyList(polyList, doshow=False, color='k')
  ndid = nodes.keys()
  ndcrd = np.array(nodes.values())
  plt.scatter(ndcrd[:,0], ndcrd[:,1], s=10, color='k')
  
  if doshow:
    plt.show()
    

