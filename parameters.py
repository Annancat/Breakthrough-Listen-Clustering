# Image processing
FREQ_RANGE = 100  # Frequency range of each slice without any cross over. In Mhz.
CROSS_OVER = 20  # How many Mhz should each slice overlap? Full size of range is FREQ_RANGE + CROSS_OVER
# What resolution files to use. 0 = highest resolution, 2 = lowest resolution. Higher res = larger file size
RESOLUTION = 2
SAVE_LOCATION = "input/"  # Where to save the images
SPLIT_RATIO = (0.8,0.2)  # Ratio to split images into training and test data.
#
CLUSTERS = 10  # Number of clusters for kmeans to split the data into.
