import numpy as np
from matplotlib import pyplot


def _make_plot_func(ax, marker, color, cmap):
  kwargs = dict()
  if color is not None:
    kwargs['c'] = color
    kwargs['cmap'] = cmap
    if marker is not None:
      kwargs['marker'] = marker
    fn = lambda *args: ax.scatter(*args, **kwargs)
  else:
    if marker is not None:
      fn = lambda *args: ax.plot(*(args + (marker,)), **kwargs)
    else:
      fn = lambda *args: ax.plot(*args, **kwargs)
  return fn


def plot_1d(xdata, data, marker=None, color=None, log=False, cmap=None):
  data = np.column_stack((data,))
  ax = pyplot.gca()
  plot = _make_plot_func(ax, marker, color, cmap)
  if xdata is not None:
    for col in data.T:
      p = plot(xdata, col)
  else:
    for col in data.T:
      p = plot(col)
  if log:
    ax.set_yscale('log')
  if color is not None:
    pyplot.colorbar(p)


def plot_2d(data, marker=None, color=None, log=False, cmap=None):
  assert data.shape[1] % 2 == 0, (
      'must have even number of columns for paired plotting')
  ax = pyplot.gca()
  plot = _make_plot_func(ax, marker, color, cmap)
  for i in xrange(0, data.shape[1], 2):
    p = plot(data[:,i], data[:,i+1])
  if log:
    ax.set_yscale('log')
  if color is not None:
    pyplot.colorbar(p)


def plot_3d(data, marker=None, color=None, log=False, cmap=None):
  assert data.shape[1] % 3 == 0, 'must have columns div. by 3'
  from mpl_toolkits.mplot3d import Axes3D
  ax = Axes3D(pyplot.gcf())
  plot = _make_plot_func(ax, marker, color, cmap)
  for i in xrange(0, data.shape[1], 3):
    p = plot(data[:,i], data[:,i+1], data[:,i+2])
  if log:
    ax.set_yscale('log')
  if color is not None:
    pyplot.colorbar(p)
