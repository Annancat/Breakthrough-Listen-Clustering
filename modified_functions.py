import os
import glob
import matplotlib
import matplotlib.pyplot as plt
from PIL import Image, ImageOps

matplotlib.use("agg")

# Math/Science package imports
import numpy as np

# Blimpy imports
import blimpy as bl
from blimpy.utils import rebin

MAX_IMSHOW_POINTS = (4096, 1268)


def waterfall_png(wf, name, f_start=None, f_stop=None, **kwargs):
    r"""
    Modified from blimpy.stax.plot_waterfall.
    Create waterfall png from data in a .fil or .h5 file.
    Parameters
    ----------
    wf : blimpy.Waterfall object
        Waterfall object of an H5 or Filterbank file containing the dynamic spectrum data.
    name : temp png name
    f_start : float
        Start frequency, in MHz.
    f_stop : float
        Stop frequency, in MHz.
    kwargs : dict
        Keyword args to be passed to matplotlib imshow().
    Notes
    -----
    Create a single-panel waterfall png (frequency vs. time vs. intensity DO NOT MATTER HERE -
    CNN does not need it to function)
    for one of the files in the set of interest, at the
    frequency of the expected event.

    Removed automatic styling to imsave that cannot be changed by kwargs
    """
    # change to full file name
    name = name + '.png'

    # Load in the data from fil
    plot_f, plot_data = wf.grab_data(f_start=f_start, f_stop=f_stop)

    # Make sure waterfall plot is under 4k*4k
    dec_fac_x, dec_fac_y = 1, 1

    # rebinning data to plot correctly with fewer points
    try:
        if plot_data.shape[0] > MAX_IMSHOW_POINTS[0]:
            dec_fac_x = plot_data.shape[0] / MAX_IMSHOW_POINTS[0]
        if plot_data.shape[1] > MAX_IMSHOW_POINTS[1]:
            dec_fac_y = int(np.ceil(plot_data.shape[1] / MAX_IMSHOW_POINTS[1]))
        plot_data = rebin(plot_data, dec_fac_x, dec_fac_y)
    except Exception as ex:
        print("\n*** Oops, grab_data returned plot_data.shape={}, plot_f.shape={}"
              .format(plot_data.shape, plot_f.shape))
        print("Waterfall info for {}:".format(wf.filename))
        wf.info()
        raise ValueError("*** Something is wrong with the grab_data output!")

    # determine extent of the plotting panel for imshow
    nints = plot_data.shape[0]
    bottom = (nints - 1) * wf.header["tsamp"]  # in seconds
    extent = (plot_f[0],  # left
              plot_f[-1],  # right
              bottom,  # bottom
              0.0)  # top

    # plot and scale intensity (log vs. linear)
    if "_OFF__FREQ" in name:
        kwargs["cmap"] = kwargs.get("cmap", "inferno")
    else:
        kwargs["cmap"] = kwargs.get("cmap", "viridis")
    plot_data = 10.0 * np.log10(plot_data)

    # get normalization parameters
    vmin = plot_data.min()
    vmax = plot_data.max()
    normalized_plot_data = (plot_data - vmin) / (vmax - vmin)

    # Save waterfall plot at location
    plt.imsave(name, normalized_plot_data,**kwargs)

def combine_pngs(name = "", part = -1, freq = -1):
    r"""
    Create one png from the On and Off observation pngs created from waterfall_png.
    Parameters
    ----------
    name : Name of temp images to combine. Comes from header name of waterfall fil.
    part: Used if a cadence is split into a smaller range of frequencies.
    Notes
    -----
    Combine temp waterfall pngs into one png so that the CNN can observe them in the correct format.
    Images get combined vertically.
    """
    # With current layout, there should always only be 6 temp images max per call.
    # However it will not crash if given more.
    if part != -1:
        files_on = sorted(
            glob.glob(os.path.join("tempImages", "*_ON__FREQ_" + str(freq) + "*" + str(part) + ".png")))
        files_off = sorted(
            glob.glob(os.path.join("tempImages", "*_OFF__FREQ_" + str(freq) + "*" + str(part) + ".png")))
    else:
        files_on = sorted(glob.glob(os.path.join("tempImages", "*_ON__FREQ_" + str(freq) + "*.png")))
        files_off = sorted(glob.glob(os.path.join("tempImages", "*_OFF__FREQ_" + str(freq) + "*.png")))

    if len(files_on) == 0:
        print("Couldn't find files for creating the final image!")
        return
    images_on = [Image.open(x) for x in files_on]
    widths, heights = zip(*(i.size for i in images_on))

    images_off = [Image.open(x) for x in files_off]
    widths_off,heights_off = zip(*(i.size for i in images_off))

    max_width = max([max(widths),max(widths_off)])
    total_height = sum(heights) + sum(heights_off) # Images combined vertically.

    new_im = Image.new('RGB', (max_width, total_height))

    y_offset = 0
    split = 0
    for i in range(0,len(images_on)):
        new_im.paste(images_on[i], (0,y_offset))
        y_offset += images_on[i].size[1]
        new_im.paste(images_off[i], (0,y_offset))
        y_offset += images_off[i].size[1]
        if i % 3 == 0:
            new_im = ImageOps.mirror(new_im)
            if part != -1:
                new_im.save('images/' + name + "_FREQ_" + str(freq) + "_PART_" + str(part) + '_SPLIT_' + str(split) + '.png')
            else:
                occurrences = sorted(glob.glob(os.path.join("images", name + '_*.png')))
                new_im.save('images/' + name + "_FREQ_" + str(freq) + "_" + str(len(occurrences) + 1) + '_SPLIT_' +
                            str(split) + '.png')
            new_im = Image.new('RGB', (max_width, total_height))
            y_offset = 0
            split +=1
            for file in files_on:
                os.remove(file)  # So temp images do not get mixed up with future observations.
            for file in files_off:
                os.remove(file)
