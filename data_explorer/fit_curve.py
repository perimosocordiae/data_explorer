#!/usr/bin/env python

from scipy.optimize import curve_fit
import re
from sys import stdin
from optparse import OptionParser

# These imports are primarily for use in user-supplied functions.
from numpy import loadtxt,log,log10,log2,sqrt
from math import e,pi


op = OptionParser(usage='%prog [options] <function_of_x> [input_file]')
op.add_option('-a','--args',type='str',default=None,
              help='CSV symbolic parameters')
op.add_option('-g','--guess',type='str',default=None,
              help='CSV initial guesses for parameters')
op.add_option('-c','--context',action='store_true',default=False,
              help='show the fitted parameters in context')
op.add_option('-p','--plot',action='store_true',default=False,
              help='plot the fitted function over the data')
opts,args = op.parse_args()
if not args:
  op.error('Must supply symbolic function. Example: a+x^b')

# here be dragons! beware malicious users
fstr = args[0].split('=')[-1].replace('^','**')
if opts.args is None:
  opts.args = ','.join(re.findall('[a-w]',fstr,re.I))
function = eval("lambda x,%s: %s" % (opts.args, fstr))

fh = open(args[1]) if len(args) >= 2 else stdin
data = loadtxt(fh)
if len(data.shape) != 2:
  op.error('Data must be two-dimensional (last column is y)')
x = data[:,:-1].T  # curve_fit expects X in DxN form??
if x.shape[0] == 1:
  x = x.flatten()
y = data[:,-1].flatten()

if opts.guess:
  p0 = map(float,opts.guess.split(','))
else:
  p0 = [1 for _ in opts.args.split(',')]

popt,pcov = curve_fit(function,x,y,p0)

if opts.context:
  fstr = args[0]
  for param,val in zip(opts.args.split(','),popt):
    fstr = fstr.replace(param,str(val))
  print fstr
else:
  for i,param in enumerate(opts.args.split(',')):
    print "%s = %f (%f)" % (param,popt[i],pcov[i,i])

if opts.plot:
  if len(x.shape)>1 and x.shape[1] != 1:
    op.error('Can only plot fitted curves for 1-d domains')
  from matplotlib import pyplot
  ynew = function(x,*popt)
  pyplot.plot(x,y,'b.',x,ynew,'r-')
  pyplot.show()
