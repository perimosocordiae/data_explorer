#!/usr/bin/env python
import sys
import re
from argparse import ArgumentParser
from datetime import datetime as dt
from time import mktime

ALL_FMTS = {
    2: ["%m %d"],
    3: ["%m %d %Y","%Y %m %d","%m %d %y","%y %m %d"],
    5: ["%a %b %d %H:%M:%S %Y"],
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


def main(fh, col, delim, comment_regex):
  ignore_patt = re.compile(comment_regex)
  for line in fh:
    if ignore_patt.match(line):
      sys.stdout.write(line)
      continue
    fields = line.strip().split(delim)
    date_str = fields[col-1]
    parts = filter(None,re.split('[\t /.-]+', date_str))
    if len(parts) not in ALL_FMTS:
      sys.stdout.write(line)
    else:
      stamp = try_parse(' '.join(parts), ALL_FMTS[len(parts)])
      unixtime = mktime(stamp.timetuple())
      fields[col-1] = str(unixtime)
      print delim.join(fields)


if __name__ == '__main__':
  ap = ArgumentParser(
      description='Convert textual dates into numeric timestamps.')
  ap.add_argument('file', type=open, nargs='?', default=sys.stdin,
                  help='Input file [default: stdin]')
  ap.add_argument('--col', type=int, default=1,
                  help='Column to convert [default: %(default)d]')
  ap.add_argument('--delim', type=str, default='\t',
                  help='Column delimiter [default: %(default)r]')
  ap.add_argument('--comment', type=str, default='^#',
                  help='Regexp for comment lines [default: %(default)s]')
  args = ap.parse_args()
  main(args.file, args.col, args.delim, args.comment)
