#!/usr/bin/env python
import sys
import re
from datetime import datetime as dt
from time import mktime

ALL_FMTS = {
    2: ["%m %d"],
    3: ["%m %d %Y","%Y %m %d","%m %d %y","%y %m %d"],
    4: ["%a %b %d %H:%M:%S %Y"],
}


def try_parse(date_str, fmts):
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
    if len(parts) not in ALL_FMTS:
      continue
    stamp = try_parse(' '.join(parts), ALL_FMTS[len(parts)])
    print mktime(stamp.timetuple())


if __name__ == '__main__':
  # TODO: allow positional args too
  main(sys.stdin)
