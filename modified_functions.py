import glob
import os
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import skimage.io
from PIL import Image, ImageOps
from blimpy.utils import rebin
from numpy import asarray
from skimage.exposure import match_histograms

MAX_IMSHOW_POINTS = (4096, 1268)
matplotlib.use("agg")


def waterfall_png(wf, name, f_start=None, f_stop=None,observation=0, part = 0, **kwargs,):
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

    # Load in the data from fil
    plot_f, plot_data = wf.grab_data(f_start=f_start, f_stop=f_stop)

    # Make sure waterfall plot is under 4k*4k
    dec_fac_x, dec_fac_y = 1, 1

    # rebinning data to plot correctly with fewer points
    try:
        if plot_data.shape[0] > MAX_IMSHOW_POINTS[0]:
            dec_fac_x = int(np.ceil(plot_data.shape[0] / MAX_IMSHOW_POINTS[0]))
        if plot_data.shape[1] > MAX_IMSHOW_POINTS[1]:
            dec_fac_y = int(np.ceil(plot_data.shape[1] / MAX_IMSHOW_POINTS[1]))
        plot_data = rebin(plot_data, dec_fac_x, dec_fac_y)
    except Exception:
        print("\n*** Oops, grab_data returned plot_data.shape={}, plot_f.shape={}"
              .format(plot_data.shape, plot_f.shape))
        print("Waterfall info for {}:".format(wf.filename))
        wf.info()
        raise ValueError("*** Something is wrong with the grab_data output!")

    # plot and scale intensity (log vs. linear)
    kwargs["cmap"] = kwargs.get("cmap", "viridis")
    plot_data = 10.0 * np.log10(plot_data)

    # get normalization parameters
    v_min = plot_data.min()
    v_max = plot_data.max()
    normalized_plot_data = (plot_data - v_min) / (v_max - v_min)
    if observation > 0:
        try:
            ref = np.array(Image.open(name + "0_" + str(part) + '.png'))
            normalized_plot_data = match_histograms(normalized_plot_data,ref)
        except:
            observation = 0
    name = name + str(observation) + "_" + str(part) + '.png'
    print(str(normalized_plot_data[0]))
    # Save waterfall plot at location
    # Really the only thing that has changed from plot_waterfall apart from removing axis and figure modifications.
    plt.imsave(name,normalized_plot_data,**kwargs)


# TODO Normalise data better!
def combine_pngs(name="", part=-1, freq=-1):
    r"""
    Create one png from the On and Off observation pngs created from waterfall_png.
    Parameters
    ----------
    name : Name of temp images to combine. Comes from header name of waterfall fil.
    part: Used if a cadence is split into a smaller range of frequencies.
    freq: Center frequency of the full file that the png comes from.
    Notes
    -----
    Combine temp waterfall pngs into one png so that the CNN can observe them in the correct format.
    Images get combined vertically.
    Used instead of built-in functions from blimpy as they output a plot instead of a simple image.
    Also allows for normalisation.
    """
    # With current layout, there should always only be 6 temp images max per call.
    # However, it will not crash if given more.
    if part != -1:
        files_on = sorted(
            glob.glob(os.path.join("tempImages", name + "*_ON__FREQ_" + str(freq) + "*_" + str(part) + ".png")))
        files_off = sorted(
            glob.glob(os.path.join("tempImages", name + "*_OFF__FREQ_" + str(freq) + "*_" + str(part) + ".png")))
    else:
        files_on = sorted(glob.glob(os.path.join("tempImages", name + "*_ON__FREQ_" + str(freq) + "*.png")))
        files_off = sorted(glob.glob(os.path.join("tempImages", name + "*_OFF__FREQ_" + str(freq) + "*.png")))

    if len(files_on) == 0:
        print("Couldn't find files for creating the final image!")
        raise Exception("Couldn't find files for creating the final image!")

    images_on = [Image.open(x) for x in files_on]
    widths_on, heights_on = zip(*(i.size for i in images_on))

    images_off = [Image.open(x) for x in files_off]
    widths_off, heights_off = zip(*(i.size for i in images_off))

    max_width = max([max(widths_on), max(widths_off)])
    total_height = (heights_on[0] * 3) + (heights_off[0] * 3)  # Images combined vertically.

    new_im = Image.new('RGB' , (max_width, total_height))

    y_offset = 0
    version = 0
    length = 0
    ref_on = []
    ref_off = []

    for i in range(0, len(images_on)):
        new_im.paste(images_on[i],(0,y_offset))
        y_offset += heights_on[i]
        new_im.paste(images_off[i],(0, y_offset))
        y_offset += heights_off[i]

        length += 2

        if length >= 6:
            length = 0
            new_im = ImageOps.mirror(new_im)

            if part != -1:
                new_im.save(
                    'images/' + name + "_FREQ_" + str(freq) + "_PART_" + str(part) + "_" + str(version) + '.png')

            else:
                occurrences = sorted(glob.glob(os.path.join("images", name + '_*.png')))
                new_im.save('images/' + name + "_FREQ_" + str(freq) + "_" + str(len(occurrences) + 1) + "_" +
                            str(version) + '.png')
            y_offset = 0
            new_im = Image.new('RGB', (max_width, total_height))
            version += 1

    if length != 0:
        new_im = ImageOps.mirror(new_im)

        if part != -1:
            new_im.save('images/' + name + "_FREQ_" + str(freq) + "_PART_" + str(part) + "_" + str(version) + '.png')

        else:
            occurrences = sorted(glob.glob(os.path.join("images", name + '_*.png')))
            new_im.save(
                'images/' + name + "_FREQ_" + str(freq) + "_" + str(len(occurrences) + 1) + "_" + str(version) +
                '.png')

    for file in files_on:
        os.remove(file)  # So temp images do not get mixed up with future observations.
    for file in files_off:
        os.remove(file)
