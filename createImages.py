import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
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
# TODO find way to download files without ssh as a backup if someone does not have access.
if __name__ == '__main__':
    api = api_requests.OpendataAPI()
    shutil.rmtree("tempImages")
    os.mkdir("tempImages")
    shutil.rmtree("images")
    os.mkdir("images")
    urls = open("urls_cleaned.txt", "r")  # From api_requests.py
    cur_url = urls.readline()
    test = subprocess.check_output(["echo", "Hello World"])
    print(str(test)[2:-3] + " test")

    freqRange = 300  # The frequency range in Mhz for each image
    while cur_url != "":
        cadenceFiles = api.get_cadence(cur_url)
        observation = 0
        name = ""
        splice = 0 #initialised here to avoid errors.
        for i in range(0, len(cadenceFiles)):  # Full observation split into 3 files for different frequency.
            if "0001.fil" in cadenceFiles[i]["url"]:
                try:
                    # Converts url into location on server.
                    script = subprocess.check_output(["~scroft/parsefile", str(cadenceFiles["data"][i]["url"])])
                    # TODO: ask for script to replicate work for future use.
                    path = str(script)[2:-3]  # Strips irrelevant characters from the returned output.
                    # Max load is in gb. Only uses the resources it needs to load the .fil
                    fil = Waterfall(path, max_load=blimpy.calcload.calc_max_load(path))
                    name = fil.header["source_name"]
                    splice = 0
                    freqs = fil.get_freqs()
                    maxFreq = freqs[0]
                    minFreq = freqs[-1]
                    curFreq = minFreq
                    while curFreq <= maxFreq - freqRange:
                        modif.waterfall_png(fil, "tempImages/" + name + str(observation) + "_" + str(splice),
                                            f_start=curFreq, f_stop=curFreq + freqRange)
                        curFreq += freqRange
                        splice += 1
                    modif.waterfall_png(fil, "tempImages/" + name + str(observation) + "_" + str(splice),
                                        f_start=maxFreq - (maxFreq - curFreq), f_stop=maxFreq)
                    observation += 1
                    print("\n-----------------------------")
                    print("Completed temporary images.")
                    print("-----------------------------\n")
                except:
                    print("Skipping cadence file at url " +
                          cur_url + "as the file size is too large to compute or file cannot be found.")


        for i in range(0, splice + 1):
            try:
                print("Creating final image for splice " + str(i) +
                        " of target " + name)
                modif.combine_pngs(name, i)
                print("Completed creating images for cadence " + cur_url)
            except:
                print("Skipping creating final image for cadence " + cur_url + "...")
        cur_url = urls.readline()
