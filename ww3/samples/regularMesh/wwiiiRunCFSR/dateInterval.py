#!/usr/bin/python

"""
sample calls
$ ./dateInterval.py -f "%Y%m%d %H%M%S" -s "20150803 000000" -e "20150804 000000" -d 3600
24
"""

from datetime import datetime
import sys
from getopt import getopt

opts = dict(getopt(sys.argv[1:], 's:e:d:f:')[0])

frmt = opts.get('-f', '%Y%m%d %H%M%S')
startdtstr = opts['-s']
startdate = datetime.strptime(startdtstr, frmt)
enddstr = opts['-e']
enddate = datetime.strptime(enddstr, frmt)
delta = opts['-d']

interval = enddate - startdate
nint = interval.total_seconds() / float(delta)
print(int(round(nint)))


