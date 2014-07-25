#!/usr/bin/env python
from data_explorer.plot_utils import plot_1d, plot_2d, plot_3d
import re
import numpy as np
from matplotlib import pyplot
from sys import stdin
from optparse import OptionParser
from collections import deque


def parse_args():
  op = OptionParser()
  op.add_option('-3', action='store_true', default=False,
                help='plot in 3D', dest='three_d')
  op.add_option('-t','--transpose', action='store_true',
                default=False, help='transpose data')
  op.add_option('-y', action='store_true', default=False,
                help='use a 1:n range for x values')
  op.add_option('-x', action='store_true', default=False,
                help='use first column for x values')
  op.add_option('--log', action='store_true',
                default=False, help='plot with log scale y')
  op.add_option('--marker', type=str, default='-',
                help='line style/marker flags')
  op.add_option('--legend', type=str, default='', help='CSV legend labels')
  op.add_option('--xlabel', type=str, default='', help='X axis label')
  op.add_option('--ylabel', type=str, default='', help='Y axis label')
  op.add_option('--title', type=str, default='%s',
                help='Plot title (%s expands to filename)')
  op.add_option('--delim', type=str, default=None,
                help='Column delimiter (default: whitespace)')
  op.add_option('-s', type=int, default=1,
                help='smoothing value (default 1,no smoothing)')
  op.add_option('-r', '--rolling', type=int,
                help='animated rolling graph buffer size')
  op.add_option('-d', '--downsample', type=float,
                help='sampling rate, as a ratio of total # samples')
  op.add_option('--hist', type=int, default=0,
                help='When >0, plots a histogram with n buckets')
  return op.parse_args()


def preprocess(data, opts):
  if opts.transpose:
    data = data.T
  if opts.s > 2:
    window = np.ones(opts.s)/float(opts.s)
    if len(data.shape) == 1:
      data = np.convolve(window,data,mode='valid')
    else:
      if len(data.shape) > 1:
        assert opts.y, 'Can only convolve 1-d sequences'
      for i in xrange(data.shape[1]):
        data[:,i] = np.convolve(window,data[:,i],mode='same')
      pad = opts.s//2
      data = data[pad:-pad]
  if opts.downsample:
    assert len(data.shape) == 1, 'Multiple line downsampling is NYI'
    new_len = int(len(data) * opts.downsample)
    old_xs = np.arange(len(data))
    new_xs = np.unique(np.linspace(0,len(data),new_len).astype(int))
    data = np.interp(new_xs, old_xs, data)
  return data


def plot(data, opts):
  if opts.three_d:
    plot_3d(data,opts.marker)
  elif len(data.shape) == 1 or data.shape[1] == 1:
    plot_1d(data,opts.marker,log=opts.log)
  elif opts.y:
    plot_1d(data,opts.marker,log=opts.log)
  else:
    plot_2d(data,(not opts.x),opts.marker,log=opts.log)


def decorate(opts, filename):
  if opts.legend:
    pyplot.legend(opts.legend.split(','),loc='best')
  if opts.xlabel:
    pyplot.xlabel(opts.xlabel)
  if opts.ylabel:
    pyplot.ylabel(opts.ylabel)
  if opts.title:
    pyplot.title(re.subn('%s', filename, opts.title)[0])


def static_plot(opts, fh, filename):
  data = np.loadtxt(fh, delimiter=opts.delim)
  data = preprocess(data, opts)
  if opts.hist > 0:
    pyplot.hist(data, opts.hist)
  else:
    plot(data, opts)
  decorate(opts, filename)


def rolling_plot(opts, fh, filename):
  disallowed_options = [
      ('-t',opts.transpose), ('-3',opts.three_d), ('-x',opts.x), ('-y',opts.y),
      ('-s > 1', opts.s > 1), ('-d', opts.downsample), ('--hist', opts.hist)
  ]
  for name,check in disallowed_options:
    if check:
      print "Option %s is not supported for rolling plots." % name
      return
  pyplot.ion()
  data = np.zeros(opts.rolling)
  ax = pyplot.gca()
  op.add_option('--ylabel', type=str, default='', help='Y axis label')
  ax.set_autoscale_on(True)
  ax.set_xlabel(opts.xlabel)
  ax.set_ylabel(opts.ylabel)
  ax.set_title(re.subn('%s', filename, opts.title)[0])
  if opts.log:
    line2d, = ax.semilogy(data+1, opts.marker)
  else:
    line2d, = ax.plot(data, opts.marker)
  buf = deque(maxlen=opts.rolling)
  delim = opts.delim if opts.delim is not None else ' '

  line = fh.readline()
  while line:
    buf.append(np.fromstring(line, sep=delim))
    data[:len(buf)] = np.array(buf).ravel()
    line2d.set_ydata(data)
    ax.relim()
    ax.autoscale_view(True,True,True)
    pyplot.draw()
    pyplot.pause(0.0001)
    line = fh.readline()


if __name__ == '__main__':
  opts, args = parse_args()
  files = args if args else ('-',)
  for f in files:
    fh = stdin if f == '-' else open(f)
    pyplot.figure()
    if opts.rolling:
      rolling_plot(opts, fh, f)
    else:
      static_plot(opts, fh, f)
  pyplot.show()
