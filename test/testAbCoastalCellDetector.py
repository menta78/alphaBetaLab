import unittest, os
from shapely import geometry as g
import cartopy

from alphaBetaLab import abCoastalCellDetector, abOptionManager

class testAbCoastalCellDetector(unittest.TestCase):
   
  def testCellOnLand(self):
    dtctr = abCoastalCellDetector.abCoastalCellDetector(None)
    cell = g.Polygon([[6, 47], [12, 47], [12, 49], [6, 49]])
    cellbnd = cell.boundary
    cellsfc = cell.area
    self.assertTrue(dtctr.isCoastalCell(cell))
    self.assertTrue(dtctr.isCoastalCell(cell, cellbnd))
    self.assertTrue(dtctr.isCoastalCell(cell, cellbnd, cellsfc))
   
  def testCellOnSea(self):
    dtctr = abCoastalCellDetector.abCoastalCellDetector(None)
    cell = g.Polygon([[-40, 47], [-35, 47], [-35, 49], [-40, 49]])
    cellbnd = cell.boundary
    cellsfc = cell.area
    self.assertFalse(dtctr.isCoastalCell(cell))
    self.assertFalse(dtctr.isCoastalCell(cell, cellbnd))
    self.assertFalse(dtctr.isCoastalCell(cell, cellbnd, cellsfc))
   
  def testCellOnCoast(self):
    dtctr = abCoastalCellDetector.abCoastalCellDetector(None)
    cell = g.Polygon([[-9.5, 40], [-8, 40], [-8, 41.5], [-9.5, 41.5]])
    cellbnd = cell.boundary
    cellsfc = cell.area
    self.assertTrue(dtctr.isCoastalCell(cell))
    self.assertTrue(dtctr.isCoastalCell(cell, cellbnd))
    self.assertTrue(dtctr.isCoastalCell(cell, cellbnd, cellsfc))
   
  def testCellOnCoast2(self):
    dtctr = abCoastalCellDetector.abCoastalCellDetector(None)
    cell = g.Polygon([[-9.5, 40], [-8.83, 40], [-8.83, 41], [-9.5, 41]])
    cellbnd = cell.boundary
    cellsfc = cell.area
    self.assertTrue(dtctr.isCoastalCell(cell))
    self.assertTrue(dtctr.isCoastalCell(cell, cellbnd))
    self.assertTrue(dtctr.isCoastalCell(cell, cellbnd, cellsfc))
   
  def testCellOnCoastLoadingWithFiona(self):
    cartopyDataDir = cartopy.config["data_dir"]
    coastalShapeFilePath = os.path.join(cartopyDataDir, 
            "shapefiles/natural_earth/physical/ne_110m_land.shp")
    opts = abOptionManager.abOptions(coastalShapeFilePath=coastalShapeFilePath)
    dtctr = abCoastalCellDetector.abCoastalCellDetector(opts)
    cell = g.Polygon([[-9.5, 40], [-8, 40], [-8, 41.5], [-9.5, 41.5]])
    cellbnd = cell.boundary
    cellsfc = cell.area
    self.assertTrue(dtctr.isCoastalCell(cell))
    self.assertTrue(dtctr.isCoastalCell(cell, cellbnd))
    self.assertTrue(dtctr.isCoastalCell(cell, cellbnd, cellsfc))


if __name__ == '__main__':
  unittest.main()
