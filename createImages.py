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


def makeFinalImage(target="", splice=-1, freq=-1):
    for i in range(0, splice + 1):
        print("Creating final image for splice " + str(i) +
                  " of current target")
        modif.combine_pngs(target,i,freq)
        print("Completed creating images for cadence " + cur_url)


# TODO find way to download files without ssh as a backup if someone does not have access.
if __name__ == '__main__':
    api = api_requests.OpendataAPI()
    shutil.rmtree("tempImages")
    os.mkdir("tempImages")
    shutil.rmtree("images")
    os.mkdir("images")
    urls = open("urls_cleaned.txt", "r")  # URLs from api_requests.py
    cur_url = urls.readline()
    freqRange = 200  # The frequency range in Mhz for each image

    while cur_url != "":
        cadenceFiles = api.get_cadence(cur_url)
        observation = 0
        name = ""
        frequencies = []
        splice = 0  # initialised here to avoid errors.
        target = ""

        for i in range(0, len(cadenceFiles)):  # Full observation split into 3 files for different frequency.
            if "0002.fil" in cadenceFiles[i]["url"]:
                # Converts url into location on server.
                path = cadenceFiles[i]["url"].replace(
                    "http://", "/mnt_").replace(".ssl.berkeley.edu", "/datax").replace("datax/dl2", "datax2/dl")
                print("Working on " + path)
                if not os.path.exists(path):
                    print("Path" + path + "does not exist!\n\n")
                    continue
                else:
                    print(path + " exists.\n Trying to make temp images")
                #try:
                # Max load is in gb. Only uses the resources it needs to load the .fil
                fil = Waterfall(path, max_load=blimpy.calcload.calc_max_load(path))
                print("Loaded file as Waterfall.")
                if i == 0:
                    target = fil.header["source_name"]
                splice = 0
                freqs = fil.get_freqs()
                maxFreq = freqs[0]
                curFreq = freqs[-1]

                if fil.header["source_name"] != target:
                    name = target + "_OFF"
                else:
                    name = target

                center_freq_ = cadenceFiles[i]["center_freq"]
                if center_freq_ not in frequencies:
                    frequencies.append(round(center_freq_, 2))

                while curFreq <= maxFreq - freqRange:
                    modif.waterfall_png(fil, "tempImages/" +
                                        name + "_FREQ_" +
                                        str(round(center_freq_, 2)) + "_" +
                                        str(observation) + "_" +
                                        str(splice),
                                        f_start=curFreq, f_stop=curFreq + freqRange)
                    print("Made Splice " + str(splice))
                    curFreq += freqRange
                    splice += 1

                modif.waterfall_png(fil, "tempImages/" +
                                    name + "_FREQ_" +
                                    str(round(center_freq_, 2)) + "_" +
                                    str(observation) + "_" +
                                    str(splice),
                                    f_start=maxFreq - (maxFreq - curFreq), f_stop=maxFreq)
                print("Made Splice " + str(splice))
                observation += 1
                print("\n-----------------------------")
                print("Completed temporary images.")
                print("-----------------------------\n")


                """except:
                    print("Skipping cadence file at url " +
                          cur_url + "as the file size is too large to compute or file cannot be found.")"""
        for j in range(0,len(frequencies)):
            makeFinalImage(target, splice, frequencies[j])

        cur_url = urls.readline()
