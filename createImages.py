# import matplotlib
# matplotlib.use('TkAgg')
# import matplotlib.pyplot as plt
import os, glob, shutil
import blimpy.calcload
import modified_functions as modif
from blimpy import Waterfall
import subprocess
import api_requests
import urllib

"""
Made for converting filterbank files into waterfall pngs to be fed
into a CNN. Requires the urls from api_requests.py to function.
Separated from api_requests.py so that the urls do not need to be gathered through api requests every time.
Assumes that it has access to the files via converting the urls and does not need to download them - downloading them
as the converter run would be even more costly than it already is!
"""


# TODO Overlap ranges
# TODO Normalise data better

def makeFinalImage(target="", splice=-1, freq=-1):
    for i in range(0, splice + 1):
        print("Creating final image for part " + str(i) +
              " of current target")
        modif.combine_pngs(target, i, freq)
        print("Completed creating images for cadence " + cur_url)


if __name__ == '__main__':
    api = api_requests.OpendataAPI()
    shutil.rmtree("tempImages")
    os.mkdir("tempImages")
    shutil.rmtree("images")
    os.mkdir("images")
    urls = open("urls_cleaned.txt", "r")  # URLs from api_requests.py
    cur_url = urls.readline()
    freqRange = 100  # The frequency range in Mhz for each image

    while cur_url != "":
        cadenceFiles = api.get_cadence(cur_url)
        observation = 0
        name = ""
        frequencies = []
        part = 0  # initialised here to avoid errors.
        target = cadenceFiles[0]["target"]

        for i in range(0, len(cadenceFiles)):   # Full observation split into 3 files for different frequency.
            if "0002.fil" in cadenceFiles[i]["url"]:
                # Converts url into location on server.
                path = cadenceFiles[i]["url"].replace(
                    "http://", "/mnt_").replace(".ssl.berkeley.edu", "/datax").replace("datax/dl2", "datax2/dl")
                print("Working on " + path)
                if not os.path.exists(path):
                    print("Path" + path + " does not exist!\n\n")
                    continue
                else:
                    print(path + " exists.\n Trying to make temp images")
                # try:
                # Max load is in gb. Only uses the resources it needs to load the .fil
                fil = Waterfall(path, load_data=False, max_load=blimpy.calcload.calc_max_load(path),
                                f_start=cadenceFiles[i]["center_freq"], f_stop=cadenceFiles[i]["center_freq"] + 1)
                print("Loaded file as Waterfall.")
                part = 0
                freqs = fil.get_freqs()
                maxFreq = freqs[0]
                curFreq = freqs[-1]

                if cadenceFiles[i]["target"] != target:
                    name = target + "_OFF_"  # OFF observation - not pointing at target
                else:
                    name = target + "_ON_"  # ON observation - pointing at target

                center_freq_ = round(cadenceFiles[i]["center_freq"], 2)
                if center_freq_ not in frequencies:
                    frequencies.append(center_freq_)

                while curFreq <= maxFreq - freqRange:
                    # reading large files causes an error in get_data . Attempted work around!
                    # Same premise as make_waterfall_plots in blimpy.stix but still cannot handle the 0001 files?
                    fil = Waterfall(path, max_load=blimpy.calcload.calc_max_load(path),
                                    f_start=curFreq, f_stop=curFreq + freqRange+20)
                    modif.waterfall_png(fil, "tempImages/" +
                                        name + "_FREQ_" +
                                        str(center_freq_) + "_" +
                                        str(observation) + "_" +
                                        str(part))
                    print("Made part " + str(part))
                    curFreq += freqRange
                    part += 1
                    del fil
                fil = Waterfall(path, max_load=blimpy.calcload.calc_max_load(path),
                                f_start=maxFreq - (maxFreq - curFreq)-20, f_stop=maxFreq)
                modif.waterfall_png(fil, "tempImages/" +
                                    name + "_FREQ_" +
                                    str(center_freq_) + "_" +
                                    str(observation) + "_" +
                                    str(part))
                print("Made part " + str(part))
                observation += 1
                del fil
                print("\n-----------------------------")
                print("Completed temporary images.")
                print("-----------------------------\n")

                """except:
                    print("Skipping cadence file at url " +
                          cur_url + "as the file size is too large to compute or file cannot be found.")"""
        for j in range(0, len(frequencies)):
            makeFinalImage(target, part, frequencies[j])

        cur_url = urls.readline()
