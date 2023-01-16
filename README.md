# data_explorer

[![PyPI version](https://badge.fury.io/py/data_explorer.svg)](http://badge.fury.io/py/data_explorer)

Command-line utilities for exploring data.

Somewhat inspired by [bit.ly's data_hacks](https://github.com/bitly/data_hacks).

Install from source with: `pip install -e .`.

## Contents

### plotter.py

Useful for plotting data stored in delimited text files.

Use the `--help` flag to see usage information.

Dependencies:

  * numpy
  * matplotlib


### fit_curve.py

Fit a function to your data by parameter optimization.

Example usage:

    fit_curve.py -c -p --args a,b "a*x + b" data_file.txt

    fit_curve.py -c -p --args a,b,c "a*log(x/b) + c^x" data_file.txt

Dependencies:

   * numpy
   * scipy
   * matplotlib (only if the `-p`/`--plot` option is used)


### date2unixtime.py

Converts text-formatted dates to unix timestamps.
Useful for converting dates into a plottable format.

Example usage:

    cut -f1 something.log | date2unixtime.py


### describe.py

Computes summary statistics for a set of data.

Example usage:

    describe.py <data_file.txt

Dependencies:

   * numpy
   * scipy
