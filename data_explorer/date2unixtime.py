#!/usr/bin/env python
import sys
import re
from datetime import datetime as dt
from time import mktime

fmts = ["%m %d %Y","%Y %m %d","%m %d %y","%y %m %d"]


def try_parse(date_str):
  for i,fmt in enumerate(fmts):
    try:
      stamp = dt.strptime(date_str, fmt)
      break
    except ValueError:
      continue
  else:
    # no format was valid
    raise ValueError("couldn't parse '%s'" % date_str)
  # clever trick: move the matching fmt to the front of the list
  if i > 0:
    fmts.insert(0,fmts.pop(i))
  return stamp


def main(fh):
  for line in fh:
    parts = filter(None,re.split('\D+',line.strip()))
    if len(parts) == 2:
      parts.append('1970')  # XXX: or perhaps the current year?
    elif len(parts) != 3:
      continue
    date = ' '.join(map(str,parts))
    stamp = try_parse(date)
    print mktime(stamp.timetuple())


if __name__ == '__main__':
  # TODO: allow positional args too
  main(sys.stdin)
