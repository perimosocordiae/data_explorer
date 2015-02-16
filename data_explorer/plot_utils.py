import numpy as np
from matplotlib import pyplot


def _make_plot_func(kwargs):
  plot = pyplot.plot
  if 'log' in kwargs:
    if kwargs['log']:
      plot = pyplot.semilogy
    del kwargs['log']
  kwargs['hold'] = True
  return plot


def plot_1d(xdata, data, *args, **kwargs):
  data = np.column_stack((data,))
  plot = _make_plot_func(kwargs)
  if xdata is not None:
    for col in data.T:
      plot(xdata, col, *args, **kwargs)
  else:
    for col in data.T:
      plot(col, *args, **kwargs)


def plot_2d(data, *args, **kwargs):
  assert data.shape[1] % 2 == 0, (
      'must have even number of columns for paired plotting')
  plot = _make_plot_func(kwargs)
  for i in xrange(0,data.shape[1],2):
    plot(data[:,i],data[:,i+1],*args,**kwargs)


def plot_3d(data,*args,**kwargs):
  assert data.shape[1] % 3 == 0, 'must have columns div. by 3'
  from mpl_toolkits.mplot3d import Axes3D
  ax = Axes3D(pyplot.gcf())
  for i in xrange(0,data.shape[1],3):
    ax.plot(data[:,i],data[:,i+1],data[:,i+2],*args,**kwargs)
