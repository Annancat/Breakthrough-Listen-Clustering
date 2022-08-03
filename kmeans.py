from time import time
import numpy as np
from tensorflow.python.keras import backend as K
from tensorflow.python.keras.layers import Layer, InputSpec, Dense, Input
from tensorflow.python.keras.models import Model
from tensorflow.keras.optimizers import SGD
from tensorflow.python.keras import callbacks
from tensorflow.python.keras.initializers import VarianceScaling
#import tensorflow as tf
from sklearn.cluster import KMeans
import metrics
from custom_layers import autoencoder as auto_encoder
from custom_layers import ClusteringLayer

import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_score
import cv2
import os, glob, shutil

# computing an auxiliary target distribution
def target_distribution(q):
    weight = q ** 2 / q.sum(0)
    return (weight.T / weight.sum(1)).T


if __name__ == '__main__':
    x_train = [cv2.resize(cv2.imread(file), (224, 224)) for file in glob.glob("input/train/images/*.png")]
    x_test = [cv2.resize(cv2.imread(file), (224, 224)) for file in glob.glob("input/test/images/*.png")]
    print("Images loaded")

    n_clusters = 5  # No. of clusters

    x = np.concatenate((x_train, x_test))
    x = x.reshape((x.shape[0], -1))
    x = np.divide(x, 255.)

    # dim[0] = og dimensions (w * h) dim[1:] = layers of auto encoder. Numbers equal the shape the encoder forces the data into in the layer.
    dims = [x.shape[-1], 500, 500, 2000, 10]
    init = VarianceScaling(scale=1. / 3., mode='fan_in',
                           distribution='uniform')
    pretrain_optimizer = SGD(learning_rate=1, momentum=0.9)
    pretrain_epochs = 300
    batch_size = 256
    save_dir = './results'

    autoencoder, encoder = auto_encoder(dims, init=init)

    autoencoder.compile(optimizer=pretrain_optimizer, loss='mse')
    autoencoder.fit(x, x, batch_size=batch_size, epochs=pretrain_epochs)  # , callbacks=cb)
    autoencoder.save_weights(save_dir + '/ae_weights.h5')

    autoencoder.load_weights(save_dir + '/ae_weights.h5')

    clustering_layer = ClusteringLayer(n_clusters, name='clustering')(encoder.output)
    model = Model(inputs=encoder.input, outputs=clustering_layer)
    model.compile(optimizer=SGD(0.01, 0.9), loss='kld')

    kmeans = KMeans(n_clusters=n_clusters, n_init=20, verbose=True)
    y_pred = kmeans.fit_predict(encoder.predict(x))
    y_pred_last = np.copy(y_pred)
    model.get_layer(name='clustering').set_weights([kmeans.cluster_centers_])

    loss = 0
    index = 0
    maxiter = 8000
    update_interval = 140
    index_array = np.arange(x.shape[0])
    tol = 0.001
    y = None

    for ite in range(int(maxiter)):
        if ite % update_interval == 0:
            q = model.predict(x, verbose=0)
            p = target_distribution(q)  # update the auxiliary target distribution p

            # evaluate the clustering performance
            y_pred = q.argmax(1)
            if y is not None:
                acc = np.round(metrics.acc(y, y_pred), 5)
                nmi = np.round(metrics.nmi(y, y_pred), 5)
                ari = np.round(metrics.ari(y, y_pred), 5)
                loss = np.round(loss, 5)
                print('Iter %d: acc = %.5f, nmi = %.5f, ari = %.5f' % (ite, acc, nmi, ari), ' ; loss=', loss)

            # check stop criterion - model convergence
            delta_label = np.sum(y_pred != y_pred_last).astype(np.float32) / y_pred.shape[0]
            y_pred_last = np.copy(y_pred)
            if ite > 0 and delta_label < tol:
                print('delta_label ', delta_label, '< tol ', tol)
                print('Reached tolerance threshold. Stopping training.')
                break
        idx = index_array[index * batch_size: min((index + 1) * batch_size, x.shape[0])]
        loss = model.train_on_batch(x=x[idx], y=p[idx])
        index = index + 1 if (index + 1) * batch_size <= x.shape[0] else 0

    model.save_weights(save_dir + '/DEC_model_final.h5')
