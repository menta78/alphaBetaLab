from matplotlib import pyplot as plt
import numpy as np
import os

def plotHiResAlphaMtx(title, alphaMtx, theta, freqindx = 0):
  return plotAlphaMtx(title, alphaMtx.xs, alphaMtx.ys, alphaMtx.alphas, alphaMtx.polygon, theta, freqindx)

def plotHiResAlphaMtxAndSave(title, alphaMtx, theta, origPolygon, contextStrs, freqindx = 0):
  fg = plotAlphaMtx(title, alphaMtx.xs, alphaMtx.ys, alphaMtx.alphas, alphaMtx.polygon, theta, freqindx)

  dirname = os.path.join('diagnostics', *contextStrs)
  try:
    os.makedirs(dirname)
  except:
    pass
  cellcenter = origPolygon.centroid.coords[0]
  idstr = 'cell:' + str(cellcenter[0]) + '_' + str(cellcenter[1])
  thetastr = 'dir:' + str(int(np.round(theta/np.pi*180.))).rjust(3, '0') + 'deg'
  imagefilename = os.path.join(dirname, idstr + '_' + thetastr +  '.png')
  fg.savefig(imagefilename)

  plt.close(fg)

def plotHiResAlphaMtxAndShow(title, alphaMtx, theta, freqindx = 0):
  plotHiResAlphaMtx(title, alphaMtx, theta, freqindx)
  plt.show()

def plotAlphaMtx(title, xs, ys, alphas, cell, theta, freqindx = 0):
  xlst = 2*xs[-1] - xs[-2]
  xs1 = np.concatenate((xs, np.array([xlst])), 0) 
  ylst = 2*ys[-1] - ys[-2]
  ys1 = np.concatenate((ys, np.array([ylst])), 0)
  alphas1 = alphas if len(alphas.shape) == 2 else alphas[:,:,freqindx]
  alphas1 = np.column_stack((alphas1, np.zeros(alphas.shape[0])))
  alphas1 = np.row_stack((alphas1, np.zeros(alphas1.shape[1])))

  fg = plt.figure()
  ax = fg.gca()
  ax.set_title(title, fontsize = 30)
  ax.pcolor(xs1, ys1, alphas1, cmap = 'gray')
  ax.set_xticks(xs1)
  ax.set_yticks(ys1)
  ax.tick_params(axis='x', labelsize=20)
  ax.tick_params(axis='y', labelsize=20)
  ax.set_aspect('equal', adjustable='box')
  ax.grid()

  if cell:
    cx, cy = cell.exterior.xy
    ax.plot(cx, cy, linewidth = 3, color = 'b')
  if theta:
    ox, oy = min(xs1), min(ys1)
    axlen = (max(xs) - min(xs)) / 2
    sgncos = np.sign(np.cos(theta))
    mx = ox + axlen*sgncos
    my = oy + axlen*sgncos*np.tan(theta)
    while (mx > max(xs)) or (my > max(ys)):
      mx = mx - (mx - ox)/2
      my = my - (my - oy)/2
    if mx < ox:
      d = ox - mx
      ox += d
      mx += d
    if my < oy:
      d = oy - my
      oy += d
      my += d
      
    ax.arrow(ox, oy, mx - ox, my - oy, fc = 'r', ec = 'r', length_includes_head=True, width = .02, head_width=.1)
    #ax.plot([ox, mx], [oy, my], color = 'r')
  return fg
    


