import numpy as np
from matplotlib import pyplot

__all__ = ["plot_1d", "plot_2d", "plot_3d"]


def plot_1d(
    ax,
    xdata,
    data,
    xlabel,
    line_labels,
    marker=None,
    color=None,
    logx=False,
    logy=False,
    cmap=None,
    colorname=None,
):
    data = np.column_stack((data,))
    plot = _make_plot_func(ax, marker, color, cmap)
    lines = zip(data.T, line_labels)
    if xdata is not None:
        for y, label in lines:
            p = plot(xdata, y, label=label)
    else:
        for y, label in lines:
            p = plot(y, label=label)
    _adjust_axis(ax, p, logx, logy, colorname)
    ax.set_xlabel(xlabel)


def plot_2d(
    ax,
    data,
    axis_labels,
    marker=None,
    color=None,
    logx=False,
    logy=False,
    cmap=None,
    colorname=None,
):
    assert (
        data.shape[1] % 2 == 0
    ), "must have even number of columns for paired plotting"
    plot = _make_plot_func(ax, marker, color, cmap)
    for i in range(0, data.shape[1], 2):
        p = plot(data[:, i], data[:, i + 1])
    _adjust_axis(ax, p, logx, logy, colorname)
    ax.set_xlabel(axis_labels[0])
    ax.set_ylabel(axis_labels[1])


def plot_3d(
    ax,
    data,
    axis_labels,
    marker=None,
    color=None,
    logx=False,
    logy=False,
    cmap=None,
    colorname=None,
):
    assert data.shape[1] % 3 == 0, "must have columns div. by 3"
    from mpl_toolkits.mplot3d import Axes3D

    assert isinstance(ax, Axes3D)
    plot = _make_plot_func(ax, marker, color, cmap)
    for i in range(0, data.shape[1], 3):
        p = plot(data[:, i], data[:, i + 1], data[:, i + 2])
    _adjust_axis(ax, p, logx, logy, colorname)
    ax.set_xlabel(axis_labels[0])
    ax.set_ylabel(axis_labels[1])
    ax.set_zlabel(axis_labels[2])


def _adjust_axis(ax, artist, logx, logy, colorname):
    if logx:
        ax.set_xscale("log")
    if logy:
        ax.set_yscale("log")
    if colorname is not None:
        # XXX: don't use pyplot interface for this
        cbar = pyplot.colorbar(artist)
        cbar.set_label(colorname)


def _make_plot_func(ax, marker, color, cmap):
    if color is not None:
        kwargs = dict(c=color, cmap=cmap)
        if marker is not None:
            kwargs["marker"] = marker
        return lambda *args: ax.scatter(*args, **kwargs)
    if marker is not None:
        return lambda *args, **kwargs: ax.plot(*(args + (marker,)), **kwargs)
    return ax.plot
