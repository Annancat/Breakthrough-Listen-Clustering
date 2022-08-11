# Unsupervised clustering of observations from Breakthrough Listen
## Basic Set Up
Jupyter notebook must be installed. </br>
kmeans.ipynb, create_urls.py ran on Python 3.6.10 <br>
image_processing.py ran on Python 3.7.6 <br>
<sub>I have not tested them on different versions, so I do not know of any problems that would arise
if something is ran on versions other than the ones specified. Please let me know if you encounter an issue.<br> </sub>
### Required Libraries:
```
pip3 install -r requirements.txt
```
### What is included:
* Set of cleaned URLS that work with image_processing.py <br>
* Example set of 1867 images split into training and test data. The autoencoder could use all images without the 
split but it speeds the training up if there is less test data to compare to.<br>
* Example output run using the training and test data. <br>
* Example trained weights from the run.
## Image Processing
If you only want to use the provided test data and do not want to create your own images, 
go to the [Image Clustering Section](#image-clustering).<br>
Otherwise, <b> image_processing.py assumes it is running on the Breakthrough Listen Berkeley 
network and will not work if it is not. </b> <br>
<br>
To create URLS, run:
```
python3 create_urls.py
```
Once URLS are created, run:
```
python3 image_processing.py
```
Parameters for image_processing.py can be found in [parameters.py](parameters.py).<br>
image_processing.py creates temporary images before making a final observation image but will delete any leftover images afterwards. <br>
The images will automatically be copied into train and test folders but the full set can be found in the SAVE_LOCATION/images folder.

## Image Clustering
After you have your images, open a jupyter notebook and open kmeans.ipynb within it. <br>
Images will be loaded from the save location specified in parameters.py. <br>
You will need to have a `weights` folder within the project folder for weights to save, create one if you do not have it.
Restart and rerun the notebook. After the first run, you will have trained weights. <br>
The created clusters can be seen in the output folder.
## TODO
* Complete Documentation / add details to Image Clustering section in README
* Test on different versions of python
* Test using different versions of libraries
* Test different settings for the autoencoder
* Try and train another autoencoder on an already sorted cluster & split it into smaller clusters
* Try and combine training set into one set.

## CREDITS
Data provided by: [Breakthrough Listen](https://breakthroughinitiatives.org/initiative/1) <br>
Used as base for api_requests.py : [How to make API calls in Python](https://www.educative.io/answers/how-to-make-api-calls-in-python) by Kedar Kodgire<br>
For instructions on how to access the API: [Breakthrough Listen Opendata Archive API](https://github.com/ggroode/bl-opendata)<br>
For the auto-encoder, clustering layers, and base code for kmeans.ipynb: [Keras_Deep_Clustering](https://github.com/Tony607/Keras_Deep_Clustering) by Chengwei Zhang