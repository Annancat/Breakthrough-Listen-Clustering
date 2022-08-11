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
* Example set of 1867 images split into training and test data. The autoencoder could use all images without the 
split but it speeds the training up if there is less test data to compare to.<br>
* Example output run using the training and test data. <br>
* Set of cleaned URLS that work with image_processing.py
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

<br>[Breakthrough Listen Opendata Archive API](https://github.com/ggroode/bl-opendata)<br>
[API tutorial](https://www.educative.io/answers/how-to-make-api-calls-in-python)<br>
[Auto-encoder and K-means code](https://github.com/Tony607/Keras_Deep_Clustering)