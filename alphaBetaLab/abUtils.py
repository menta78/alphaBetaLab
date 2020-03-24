import numpy as np

radiusEarth = 6371000 #m
defaultTolerance = 0.000000001

MESHTYPE_REGULAR = 'regular'
MESHTYPE_TRIANGULAR = 'triangular'

class abException(Exception):
  pass

def isClose(x1, x2, tolerance = defaultTolerance):
  return abs(x1 - x2) < tolerance

def greaterClose(x, y):
  return isClose(x, y) or (x > y)

def greater(x, y):
  return (not isClose(x, y)) and (x > y)

def lesserClose(x, y):
  return isClose(x, y) or (x < y)

def lesser(x, y):
  return (not isClose(x, y)) and (x < y)

def angleDiff(angle1, angle2):
  diff = angle1 - angle2
  while diff > np.pi:
    diff -= 2*np.pi
  while diff < -np.pi:
    diff += 2*np.pi
  return diff


