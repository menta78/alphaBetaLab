#!/usr/bin/python

"""
sample calls
$ ./date.py -f %Y%m%d -s 20150115 -t month -d 1 -m
20150201
$ ./date.py -f "%Y%m%d %H%M%S" -s "20150115 000000" -t hour -d -1
20150114 230000
$ ./date.py -f "%Y%m%d %H%M%S" -s "20150115 000000" -t second -d -3600
20150114 230000
$ ./date.py -f %Y%m%d -s 20150115 -t month -d 1 -m -o %Y%m
201502
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta
import sys
import getopt

try:
  opts = dict(getopt.getopt(sys.argv[1:], 'f:s:t:d:mo:')[0])
except getopt.GetoptError as err:
  print(str(err))
  raise

frmt = opts['-f']
inputDateStr = opts['-s']
deltatype = opts['-t']
delta = int(opts['-d']) if '-d' in opts else 1
roundToMonth = '-m' in opts
outfrmt = opts['-o'] if '-o' in opts else frmt

tm = datetime.strptime(inputDateStr, frmt)
if deltatype == 'month':
  dt = relativedelta(months = delta)
elif deltatype == 'day':
  dt = relativedelta(days = delta)
elif deltatype == 'hour':
  dt = relativedelta(hours = delta)
elif deltatype == 'second':
  dt = relativedelta(seconds = delta)
elif deltatype == 'halfmonth':
  assert delta == 1, 'for deltatype == halfmonth only delta == 1 is supported'
  if tm.day == 1:
    tm2 = datetime(tm.year, tm.month, 15)
  else:
    dt = relativedelta(months = 1)
    tm2 = tm + dt
    tm2 = datetime(tm2.year, tm2.month, 1)
  dt = tm2 - tm
newdate = tm + dt
if roundToMonth:
  rslt = datetime(newdate.year, newdate.month, 1)
else:
  rslt = newdate
print(rslt.strftime(outfrmt))


