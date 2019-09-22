"""
Temporary fix for basemap.
"""
import sys, os

if not 'PROJ_LIB' in os.environ:
  projLib = os.path.join(sys.prefix, 'share', 'proj')
  os.environ['PROJ_LIB'] = projLib
