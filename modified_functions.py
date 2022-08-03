import os
import glob
import matplotlib
import matplotlib.pyplot as plt
from PIL import Image, ImageOps
import sys
from os.path import dirname, abspath, isdir
import gc
from argparse import ArgumentParser
import logging
from skimage.exposure import match_histograms
from numpy import asarray
import numpy as np

logger_name = "stix"
logger = logging.getLogger(logger_name)
logger.setLevel(logging.INFO)

matplotlib.use("agg")

# Math/Science package imports
import numpy as np

# Blimpy imports
import blimpy as bl
from blimpy.utils import rebin
from blimpy import Waterfall
from blimpy.plotting import plot_waterfall

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
            dec_fac_x = int(np.ceil(plot_data.shape[0] / MAX_IMSHOW_POINTS[0]))
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
    kwargs["cmap"] = kwargs.get("cmap", "viridis")
    plot_data = 10.0 * np.log10(plot_data)

    # get normalization parameters
    vmin = plot_data.min()
    vmax = plot_data.max()
    normalized_plot_data = (plot_data - vmin) / (vmax - vmin)

    # Save waterfall plot at location
    plt.imsave(name, normalized_plot_data, **kwargs)


def combine_pngs(name="", part=-1, freq=-1):
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
            glob.glob(os.path.join("tempImages", name + "*_ON__FREQ_" + str(freq) + "*_" + str(part) + ".png")))
        files_off = sorted(
            glob.glob(os.path.join("tempImages", name + "*_OFF__FREQ_" + str(freq) + "*_" + str(part) + ".png")))
    else:
        files_on = sorted(glob.glob(os.path.join("tempImages", name + "*_ON__FREQ_" + str(freq) + "*.png")))
        files_off = sorted(glob.glob(os.path.join("tempImages", name + "*_OFF__FREQ_" + str(freq) + "*.png")))

    if len(files_on) == 0:
        print("Couldn't find files for creating the final image!")
        return
    images_on = [Image.open(x) for x in files_on]
    widths, heights = zip(*(i.size for i in images_on))

    images_off = [Image.open(x) for x in files_off]
    widths_off, heights_off = zip(*(i.size for i in images_off))

    max_width = max([max(widths), max(widths_off)])
    total_height = (heights[0]*3) + (heights_off[0]*3)  # Images combined vertically.

    new_im = Image.new('RGB', (max_width, total_height))

    y_offset = 0
    version = 0
    length = 0
    for i in range(0, len(images_on)):
        if y_offset ==0:
            ref = asarray(images_on[i])
        new_im.paste(images_on[i], (0, y_offset))
        y_offset += heights[i]
        new_im.paste(images_off[i], (0, y_offset))
        y_offset += heights_off[i]
        length +=2
        if length >= 6:
            length = 0
            new_im = match_histograms(asarray(new_im),ref,channel_axis=-1)
            new_im = ImageOps.mirror(new_im)
            if part != -1:
                new_im.save(
                    'images/' + name + "_FREQ_" + str(freq) + "_PART_" + str(part) + "_" + str(version) + '.png')
            else:
                occurrences = sorted(glob.glob(os.path.join("images", name + '_*.png')))
                new_im.save('images/' + name + + "_FREQ_" + str(freq) + "_" + str(len(occurrences) + 1) + "_" +
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
                'images/' + name + + "_FREQ_" + str(freq) + "_" + str(len(occurrences) + 1) + "_" + str(version) +
                '.png')

    for file in files_on:
        os.remove(file)  # So temp images do not get mixed up with future observations.
    for file in files_off:
        os.remove(file)


def sort2(x, y):
    r""" Return lowest value, highest value"""
    if y < x:
        return y, x
    return x, y


def make_waterfall_plots(input_file, chunk_count, plot_dir, width, height, dpi, source_name=None):
    r"""
           Make waterfall plots of a given huge-ish file.
           Parameters
           ----------
           input_file : str
               Path of Filterbank or HDF5 input file to plot in a stacked mode.
           chunk_count : int
               The number of chunks to divide the entire bandwidth into.
           plot_dir : str
               Directory for storing the PNG files.
           width : float
               Plot width in inches.
           height : float
               Plot height in inches.
           dpi : int
               Plot dots per inch.
           source_name : str
               Source name from the file header.
           """

    # Get directory path for storing PNG file
    if plot_dir is None:
        dirpath = dirname(abspath(input_file)) + "/"
    else:
        if not isdir(plot_dir):
            os.mkdir(plot_dir)
        dirpath = plot_dir

    # Calculate frequency boundary variables.
    wf1 = Waterfall(input_file, load_data=False)
    nf = wf1.n_channels_in_file
    if nf % chunk_count != 0:
        msg = "Number of frequency chunks ({}) does not evenly divide the number of frequencies ({})!" \
            .format(chunk_count, nf)
        logger.warning(msg)
    fchunk_f_start = wf1.file_header["fch1"]
    fchunk_size = int(nf / chunk_count)
    fchunk_f_offset = fchunk_size * wf1.file_header["foff"]
    fchunk_f_stop = fchunk_f_start + (fchunk_size - 1) * wf1.file_header["foff"]

    # Produce the source_name to be used in the image title.
    if source_name is None:
        source_name = wf1.header["source_name"]
        if source_name.upper() == "UNKNOWN":
            source_name = wf1.header["rawdatafile"].replace(".0000.raw", "")

    # Begin PNG file collection.
    png_collection = []

    # Generate a plot/PNG for each frequency chunk.
    logger.info("Image width = {}, height = {}, dpi = {}"
                .format(width, height, dpi))

    for ii in range(0, chunk_count):
        ii_lowest, ii_highest = sort2(fchunk_f_start, fchunk_f_stop)

        # read in data
        wf = Waterfall(input_file, f_start=ii_lowest, f_stop=ii_highest)

        # Validate frequency range.
        # Save the figures.
        path_png = dirpath + source_name + "_chunk_{}".format(ii + 1) + ".png"
        png_collection.append(path_png)
        plt.figure(frameon=False)
        plt.axis('off')
        plt.imsave(path_png, dpi=dpi)  # , bbox_inches='tight', pad_inches=0)

        # Delete Waterfall object.
        del wf
        gc.collect()
        plt.close("all")

        # Prepare for next chunk.
        fchunk_f_start += fchunk_f_offset
        fchunk_f_stop += fchunk_f_offset

    return png_collection, source_name
