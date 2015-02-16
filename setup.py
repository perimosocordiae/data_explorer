#!/usr/bin/env python
from setuptools import setup

version = "0.1.3"
setup(name='data_explorer',
      version=version,
      description='Command line utilities for data exploration',
      author='CJ Carey',
      author_email='perimosocordiae@gmail.com',
      url='http://github.com/perimosocordiae/data_explorer',
      license='MIT',
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Intended Audience :: System Administrators',
          'Topic :: Terminals',
      ],
      packages=['data_explorer'],
      scripts=[
          'data_explorer/plotter.py',
          'data_explorer/date2unixtime.py',
          'data_explorer/describe.py',
          'data_explorer/fit_curve.py'
      ]
      )
