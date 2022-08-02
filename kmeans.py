from time import time
import numpy as np
from tensorflow.python.keras import backend as K
from tensorflow.python.keras.layers import Layer, InputSpec,Dense, Input
from tensorflow.python.keras.models import Model
from tensorflow.keras.optimizers import SGD
from tensorflow.python.keras import callbacks
from tensorflow.python.keras.initializers import VarianceScaling
import tensorflow as tf
from sklearn.cluster import KMeans
import metrics
from custom_layers import autoencoder as auto_encoder
from custom_layers import ClusteringLayer

import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_score
import cv2
import os, glob, shutil

if __name__ == '__main__':
    (x_train, y_train), (x_test, y_test) = mnist.load_data()

    x = np.concatenate((x_train, x_test))
    y = np.concatenate((y_train, y_test))
    x = x.reshape((x.shape[0], -1))
    x = np.divide(x, 255.)
    autoencoder, encoder = auto_encoder(dims, init=init)