import os, glob, shutil
import modified_functions as modif
from blimpy import Waterfall
from pathlib import Path
import subprocess
"""
Made for converting filterbank files into waterfall pngs to be fed
into a CNN. Requires the urls from api_requests.py to function.
Separated from api_requests.py so that the urls do not need to be gathered through api requests every time.
Assumes that it has access to the files via converting the urls and does not need to download them - downloading them
as the converter run would be even more costly than it already is!
"""
if __name__ == '__main__':
    shutil.rmtree("images")
    os.mkdir("images")
    urls = open("urls.txt", "r") #From api_requests.py
    cur_url = urls.readline()
    test = subprocess.check_output(["echo", "Hello World"])
    print(str(test)[2:-3] + "test")
    while cur_url != "":
        #Converts url into location on server.
        script = subprocess.check_output(["~scroft/parsefile"], str(cur_url))  # may need to ask for script :/
        path = str(script)[2:-3]
        try:
            fil = Waterfall(path, max_load=10)
            modif.waterfall_png(fil, "images/" + fil.header["source_name"])
        except:
            print("Skipping file at " + path + " as the file size is too large to compute or an error occurred.")
        cur_url = urls.readline()
