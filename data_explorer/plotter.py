#!/usr/bin/env python
from data_explorer.plot_utils import plot_1d, plot_2d, plot_3d
import re
import numpy as np
from datetime import datetime
from matplotlib import pyplot, animation
from sys import stdin
from argparse import ArgumentParser
from collections import deque


def parse_args():
  ap = ArgumentParser(description='General-purpose plotter for columns of data')
  ap.add_argument('files', nargs='*', default=('-',), help='File(s) to plot')
  ap.add_argument('-2', action='store_true', default=False,
                  help='Treat columns as (x,y) points', dest='two_d')
  ap.add_argument('-3', action='store_true', default=False,
                  help='Treat columns as (x,y,z) points', dest='three_d')
  ap.add_argument('-t','--transpose', action='store_true', default=False,
                  help='Convert rows to columns before plotting')
  ap.add_argument('-x', action='store_true', default=False,
                  help='Use first column for x values')
  ap.add_argument('--log', action='store_true', default=False,
                  help='Use a log scale for the y axis')
  ap.add_argument('--delim', type=str, default=None,
                  help='Column delimiter (default: whitespace)')
  ap.add_argument('--hist', type=int, default=0,
                  help='When >0, plots a histogram with n buckets')

  ag = ap.add_argument_group('Styling Options')
  ag.add_argument('--marker', type=str, default='-',
                  help='Line style/marker flags [default: %(default)s]')
  ag.add_argument('--xlabel', type=str, default='', help='X axis label')
  ag.add_argument('--ylabel', type=str, default='', help='Y axis label')
  ag.add_argument('--title', type=str, default='%s',
                  help='Plot title (%s expands to filename)')
  ag.add_argument('--legend', type=str, default='',
                  help='Legend labels, comma-separated')

  ag = ap.add_argument_group('Preprocessing Options')
  ag.add_argument('-s', type=int, default=1,
                  help='When >2, smooth data with window of size n')
  ag.add_argument('-r', '--rolling', type=int,
                  help='Animate a rolling graph with buffer of size n')
  ag.add_argument('-d', '--downsample', type=float,
                  help='Sampling rate, as a ratio of total # samples')
  ag.add_argument('--time', action='store_true', default=False,
                  help='Treat the first column as date/time. (Implies -x)')
  return ap.parse_args()


def preprocess(data, opts):
  if opts.transpose:
    data = data.T
  if opts.s > 2:
    if opts.two_d or opts.three_d:
      raise ValueError('Can only convolve 1-d sequences')
    window = np.ones(opts.s)/float(opts.s)
    if data.ndim == 1:
      data = np.convolve(window, data, mode='valid')
    else:
      for i in xrange(data.shape[1]):
        data[:,i] = np.convolve(window, data[:,i], mode='same')
      pad = opts.s//2
      data = data[pad:-pad]
  if opts.downsample:
    assert data.ndim == 1, 'Multiple line downsampling is NYI'
    old_len = len(data)
    new_len = int(old_len * opts.downsample)
    old_xs = np.arange(old_len)
    new_xs = np.unique(np.linspace(0,old_len,new_len).astype(int))
    data = np.interp(new_xs, old_xs, data)
  return data


def plot(data, opts):
  if opts.three_d:
    return plot_3d(data, opts.marker)
  if opts.two_d:
    return plot_2d(data, opts.marker, log=opts.log)
  if opts.x:
    xdata = data[:,0]
    data = data[:,1:]
  elif opts.time:
    xdata = map(datetime.fromtimestamp, data[:,0])
    data = data[:,1:]
  else:
    xdata = None
  plot_1d(xdata, data, opts.marker, log=opts.log)


def decorate(opts, filename, ax=None):
  if ax is None:
    ax = pyplot.gca()
  ax.set_xlabel(opts.xlabel)
  ax.set_ylabel(opts.ylabel)
  ax.set_title(re.subn('%s', filename, opts.title)[0])
  if opts.legend:
    ax.legend(opts.legend.split(','), loc='best')


def static_plot(opts, fh, filename):
  data = np.loadtxt(fh, delimiter=opts.delim)
  data = preprocess(data, opts)
  pyplot.figure()
  if opts.hist > 0:
    pyplot.hist(data, opts.hist)
  else:
    plot(data, opts)
  decorate(opts, filename)


def rolling_plot(opts, fh, filename):
  disallowed_options = [
      ('-t',opts.transpose), ('-3',opts.three_d), ('-2',opts.two_d),
      ('-x',opts.x), ('--time',opts.time),
      ('-s > 1', opts.s > 1), ('-d', opts.downsample), ('--hist', opts.hist)
  ]
  for name,check in disallowed_options:
    if check:
      print "Option %s is not supported for rolling plots." % name
      return

  fig, ax = pyplot.subplots()
  ax.set_autoscale_on(True)
  decorate(opts, filename, ax=ax)

  data = np.zeros(opts.rolling)
  if opts.log:
    line2d, = ax.semilogy(data+1, opts.marker)
  else:
    line2d, = ax.plot(data, opts.marker)

  buf = deque(maxlen=opts.rolling)
  delim = opts.delim if opts.delim is not None else ' '

  def anim_helper(line):
    buf.append(np.fromstring(line, sep=delim))
    data[:len(buf)] = np.array(buf).ravel()
    line2d.set_ydata(data)
    ax.relim()
    ax.autoscale_view(True,True,True)
    ax.figure.canvas.draw()
    return line2d,

  return animation.FuncAnimation(fig, anim_helper, fh, blit=True,
                                 interval=10, repeat=False)

if __name__ == '__main__':
  args = parse_args()
  for f in args.files:
    fh = stdin if f == '-' else open(f)
    if args.rolling:
      _ = rolling_plot(args, fh, f)
    else:
      static_plot(args, fh, f)
  pyplot.show()
