import os, glob, shutil
import modified_functions as modif
import matplotlib.pyplot as plt
from blimpy import Waterfall
from pathlib import Path

if __name__ == '__main__':
    files = sorted(glob.glob(os.path.join("data", '*.fil')))

    for file in files:
        fil = Waterfall(file, max_load=5)
        modif.waterfall_png(fil, fil.header["source_name"])