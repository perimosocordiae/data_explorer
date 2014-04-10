# for reference when doing animations:
# http://matplotlib.sourceforge.net/examples/animation/animate_decay.html
# http://www.scipy.org/Cookbook/Matplotlib/Animations (GUI neutral)

# TODO: add some animation support to this

from matplotlib import pyplot
show = pyplot.show


def _make_plot_func(kwargs):
  plot = pyplot.plot
  if 'log' in kwargs:
    if kwargs['log']:
      plot = pyplot.semilogy
    del kwargs['log']
  kwargs['hold'] = True
  return plot


def plot_1d(data,*args,**kwargs):
  if len(data.shape) == 1:  # 1-d array
    data.shape = (data.shape[0],1)
  plot = _make_plot_func(kwargs)
  for i in xrange(data.shape[1]):
    plot(data[:,i],*args,**kwargs)


def plot_1d_with_x(data,*args,**kwargs):
  assert data.shape[1] > 1, 'must have at least 2 columns'
  plot = _make_plot_func(kwargs)
  for i in xrange(1,data.shape[1]):
    plot(data[:,0],data[:,i],*args,**kwargs)


def plot_2d(data,paired=True,*args,**kwargs):
  plot = _make_plot_func(kwargs)
  if paired:  # paired flag
    assert data.shape[1] % 2 == 0, 'must have even number of columns for paired plotting'
    for i in xrange(0,data.shape[1],2):
      plot(data[:,i],data[:,i+1],*args,**kwargs)
  else:
    for i in xrange(1,data.shape[1]):
      plot(data[:,0],data[:,i],*args,**kwargs)


def plot_3d(data,*args,**kwargs):
  assert data.shape[1] % 3 == 0, 'must have columns div. by 3'
  from mpl_toolkits.mplot3d import Axes3D
  ax = Axes3D(pyplot.gcf())
  for i in xrange(0,data.shape[1],3):
    ax.plot(data[:,i],data[:,i+1],data[:,i+2],*args,**kwargs)
