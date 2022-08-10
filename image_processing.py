"""
Made for converting filterbank files into waterfall pngs to be fed
into an autoencoder. Requires the urls created and cleaned by create_urls.py to function.
Separated from api_requests.py so that the urls do not need to be gathered through api requests every time.
Assumes that it has access to the files via converting the urls and does not need to download them - downloading them
as the converter ran would be even more costly than it already is!

Multiple parameters can be changed by going to parameters.py under the Image Processing section.
"""

import math
import os
import shutil
import blimpy.calcload
from blimpy import Waterfall
import api_requests
import modified_functions as modif
import parameters
import splitfolders


def make_final_image(target="", total_parts=-1, freq=-1):
    for i in range(0, total_parts + 1):
        print("Creating final image for part " + str(i) +
              " of current target")
        modif.combine_pngs(target, i, freq)
        print("Completed creating images for cadence " + cur_url + ", center frequency " + str(freq))


if __name__ == '__main__':

    # Removes any old images that could affect the naming scheme of the pngs.
    if os.path.exists("tempImages"):
        shutil.rmtree("tempImages")
    os.mkdir("tempImages")

    api = api_requests.OpendataAPI()
    urls = open("urls_cleaned.txt", "r")  # URLs from api_requests.py
    cur_url = urls.readline()
    freq_range = parameters.FREQ_RANGE  # The frequency range in Mhz for each image
    cross_over = parameters.CROSS_OVER  # How much the splits cross over in Mhz

    while cur_url != "":

        cadence_files = api.get_cadence(cur_url)
        observation = 0
        name = ""
        frequencies = []
        part = 0  # Initialised here to avoid errors.
        target = cadence_files[0]["target"]
        # Full observation split into files of different center frequencies -
        # - more than simply 6 files for 3 on and 3 off observations

        for i in range(0, len(cadence_files)):

            if "000" + str(parameters.RESOLUTION) + ".fil" in cadence_files[i]["url"]:
                # Converts url into location on server.
                path = cadence_files[i]["url"].replace(
                    "http://", "/mnt_").replace(".ssl.berkeley.edu", "/datax").replace("datax/dl2", "datax2/dl")
                print("Working on " + path)

                if not os.path.exists(path):
                    print("Path" + path + " does not exist!\n\n")
                    continue

                else:
                    print(path + " exists.\nTrying to make temp images")
                # Only needs the header from the file to get the frequencies.
                fil = Waterfall(path, load_data=False)
                freqs = fil.get_freqs()
                max_freq = freqs[0]
                cur_freq = int(math.ceil(freqs[-1]))
                # Floats do not work well with slicing. Current starting frequency for slices.
                print("Getting frequencies from file.")

                part = 0
                if cadence_files[i]["target"] == target:
                    name = target + "_ON_"  # ON observation - pointing at target
                else:
                    name = target + "_OFF_"  # OFF observation - not pointing at target

                # Keeping track of the different frequencies.
                center_freq_ = round(cadence_files[i]["center_freq"], 2)
                if center_freq_ not in frequencies:
                    frequencies.append(center_freq_)

                # Max load is in gb. Max load slightly more than what it takes to load the file just in case.
                fil = Waterfall(path, max_load=blimpy.calcload.calc_max_load(path),
                                f_stop=cur_freq + freq_range + cross_over)  # Starting slice. Allows no cutoff.
                print("Loaded slice.")
                modif.waterfall_png(fil, "tempImages/" + name + "_FREQ_" + str(center_freq_) + "_",
                                    observation=observation, part=part)
                print("Made part " + str(part))

                cur_freq += freq_range
                part += 1
                del fil

                # Splits any remaining range.
                while cur_freq <= max_freq - (freq_range + cross_over):
                    fil = Waterfall(path, max_load=blimpy.calcload.calc_max_load(path),
                                    f_start=cur_freq,
                                    f_stop=cur_freq + freq_range + cross_over)  # Any middle slices
                    print("Loaded slice.")
                    modif.waterfall_png(fil, "tempImages/" + name + "_FREQ_" + str(center_freq_) + "_",
                                        observation=observation, part=part)
                    print("Made part " + str(part))

                    cur_freq += freq_range
                    part += 1
                    del fil

                fil = Waterfall(path, max_load=blimpy.calcload.calc_max_load(path),
                                f_start=int(round(max_freq - (max_freq - cur_freq)) - cross_over))
                # Ending Slice. Allows no cutoff. May overlap more with other slices but keeps the same width.
                print("Loaded slice.")
                modif.waterfall_png(fil, "tempImages/" + name + "_FREQ_" + str(center_freq_) + "_",
                                    observation=observation, part=part)
                print("Made part " + str(part))
                observation += 1
                del fil
                print("\n-----------------------------")
                print("Completed temporary images.")
                print("-----------------------------\n")

        # Actual creation of final images
        for j in range(0, len(frequencies)):
            make_final_image(target, part, frequencies[j])

        cur_url = urls.readline()

    shutil.rmtree("tempImages")

    print("Created all images. Splitting into training and test data.")

    splitfolders.ratio(parameters.SAVE_LOCATION + "images", parameters.SAVE_LOCATION,
                       seed=1337, ratio=parameters.SPLIT_RATIO)

    if not os.path.exists(parameters.SAVE_LOCATION + "test"):
        os.rename(parameters.SAVE_LOCATION + "val", parameters.SAVE_LOCATION + "test")

    print("Images have been split into training and test folders.\nImage processing complete.")
