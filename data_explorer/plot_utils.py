import numpy as np
from matplotlib import pyplot


def _make_plot_func(ax, marker, color):
  kwargs = dict(marker=marker)
  if color is not None:
    kwargs['c'] = color
    fn = lambda *args: ax.scatter(*args, **kwargs)
  else:
    kwargs['hold'] = True
    fn = lambda *args: ax.plot(*args, **kwargs)
  return fn


def plot_1d(xdata, data, marker, color=None, log=False):
  data = np.column_stack((data,))
  ax = pyplot.gca()
  plot = _make_plot_func(ax, marker, color)
  if xdata is not None:
    for col in data.T:
      plot(xdata, col)
  else:
    for col in data.T:
      plot(col)
  if log:
    ax.set_yscale('log')


def plot_2d(data, marker, color=None, log=False):
  assert data.shape[1] % 2 == 0, (
      'must have even number of columns for paired plotting')
  ax = pyplot.gca()
  plot = _make_plot_func(ax, marker, color)
  for i in xrange(0, data.shape[1], 2):
    plot(data[:,i], data[:,i+1])
  if log:
    ax.set_yscale('log')


def plot_3d(data, marker, color=None, log=False):
  assert data.shape[1] % 3 == 0, 'must have columns div. by 3'
  from mpl_toolkits.mplot3d import Axes3D
  ax = Axes3D(pyplot.gcf())
  plot = _make_plot_func(ax, marker, color)
  for i in xrange(0, data.shape[1], 3):
    plot(data[:,i], data[:,i+1], data[:,i+2])
  if log:
    ax.set_yscale('log')
