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
  ap.add_argument('--log', action='store_true', default=False,
                  help='Use a log scale for the y axis')
  ap.add_argument('--hist', type=int, default=0,
                  help='When >0, plots a histogram with n buckets')

  ag = ap.add_argument_group('Input Options')
  ag.add_argument('-x', action='store_true', default=False,
                  help='Use first column for x values')
  ag.add_argument('-2', action='store_true', default=False, dest='two_d',
                  help='Treat pairs of columns as (x,y) points')
  ag.add_argument('-3', action='store_true', default=False, dest='three_d',
                  help='Treat triples of columns as (x,y,z) points')
  ag.add_argument('--transpose', action='store_true', default=False,
                  help='Convert rows to columns before plotting')
  ag.add_argument('--delim', type=str, default=None,
                  help='Column delimiter (default: whitespace)')
  ag.add_argument('--columns', type=int, nargs='+', default=[],
                  help='Space-separated column numbers to use; first col is 1.')
  ag.add_argument('--skip', type=int, default=0,
                  help='Number of rows to skip (default: 0)')
  ag.add_argument('--comment', type=str, default='#',
                  help='Start of comment character (default: #)')

  ag = ap.add_argument_group('Styling Options')
  ag.add_argument('--marker', type=str, default=None,
                  help='Line style/marker flag')
  ag.add_argument('--xlabel', type=str, default='', help='X axis label')
  ag.add_argument('--ylabel', type=str, default='', help='Y axis label')
  ag.add_argument('--title', type=str, default='%s',
                  help='Plot title (%(default)s expands to filename)')
  ag.add_argument('--legend', type=str, default='',
                  help='Legend labels, comma-separated')
  ag.add_argument('--color', type=int, default=None,
                  help='Column to use for color mapping; first col is 1.')
  ag.add_argument('--colormap', type=str, default='jet',
                  help='Name of colormap to use (default: jet)')

  ag = ap.add_argument_group('Preprocessing Options')
  ag.add_argument('--smooth', type=int, default=1,
                  help='When >2, smooth data with window of size n')
  ag.add_argument('--rolling', type=int,
                  help='Animate a rolling graph with buffer of size n')
  ag.add_argument('--downsample', type=float,
                  help='Sampling rate, as a ratio of total # samples')
  ag.add_argument('--time', action='store_true', default=False,
                  help='Treat the first column as date/time. (Implies -x)')
  return ap.parse_args()


def preprocess(data, opts):
  if opts.transpose:
    data = data.T
  if opts.smooth > 2:
    if opts.two_d or opts.three_d:
      raise ValueError('Can only convolve 1-d sequences')
    window = np.ones(opts.smooth) / float(opts.smooth)
    if data.ndim == 1:
      data = np.convolve(window, data, mode='valid')
    else:
      for i in xrange(data.shape[1]):
        data[:,i] = np.convolve(window, data[:,i], mode='same')
      pad = opts.smooth // 2
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
  if opts.color:
    c = data[:,opts.color-1]
    data = np.delete(data, opts.color-1, axis=1)
  else:
    c = None
  kwargs = dict(marker=opts.marker, color=c, log=opts.log, cmap=opts.colormap)
  if opts.three_d:
    assert data.shape[1] >= 3
    return plot_3d(data, **kwargs)
  if opts.two_d:
    assert data.shape[1] >= 2
    return plot_2d(data, **kwargs)
  if opts.x:
    assert data.shape[1] >= 2
    xdata = data[:,0]
    data = data[:,1:]
  elif opts.time:
    assert data.shape[1] >= 2
    xdata = map(datetime.fromtimestamp, data[:,0])
    data = data[:,1:]
  else:
    assert data.shape[1] >= 1
    xdata = None
  plot_1d(xdata, data, **kwargs)


def decorate(opts, filename, ax=None):
  if ax is None:
    ax = pyplot.gca()
  ax.set_xlabel(opts.xlabel)
  ax.set_ylabel(opts.ylabel)
  ax.set_title(re.subn('%s', filename, opts.title)[0])
  if opts.legend:
    ax.legend(opts.legend.split(','), loc='best')


def static_plot(opts, fh, filename):
  if opts.columns:
    cols = [c-1 for c in opts.columns]
  else:
    cols = None
  data = np.loadtxt(fh, delimiter=opts.delim, usecols=cols, skiprows=opts.skip,
                    comments=opts.comment)
  data = preprocess(data, opts)
  pyplot.figure()
  if opts.hist > 0:
    pyplot.hist(data, opts.hist)
  else:
    plot(data, opts)
  decorate(opts, filename)


def rolling_plot(opts, fh, filename):
  disallowed_options = [
      ('--transpose',opts.transpose), ('-3',opts.three_d), ('-2',opts.two_d),
      ('-x',opts.x), ('--time',opts.time), ('--hist', opts.hist),
      ('--smooth > 1', opts.smooth > 1), ('--downsample', opts.downsample),
      ('--columns', opts.columns), ('--skip', opts.skip),
      ('--comment', opts.comment != '#'), ('--color', opts.color is not None)
  ]
  for name,check in disallowed_options:
    if check:
      print "Option %s is not supported for rolling plots." % name
      return

  fig, ax = pyplot.subplots()
  ax.set_autoscale_on(True)
  decorate(opts, filename, ax=ax)
  marker = opts.marker or '-'

  data = np.zeros(opts.rolling)
  if opts.log:
    line2d, = ax.semilogy(data+1, marker)
  else:
    line2d, = ax.plot(data, marker)

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
