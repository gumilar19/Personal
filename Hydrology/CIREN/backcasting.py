# -*- coding: utf-8 -*-
"""
Created on Sun May  9 12:19:14 2021

@author: Carlos
"""

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
%matplotlib qt
import csv
from tensorflow.math import reduce_prod


# funciones
def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
    series = tf.expand_dims(series, axis=-1)
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size + 1, shift=1, drop_remainder=True)
    ds = ds.flat_map(lambda w: w.batch(window_size + 1))
    ds = ds.shuffle(shuffle_buffer)
    ds = ds.map(lambda w: (w[:-1], w[1:]))
    return ds.batch(batch_size).prefetch(1)

def model_backcast(model, series, window_size):
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size, shift=1, drop_remainder=True)
    ds = ds.flat_map(lambda w: w.batch(window_size))
    ds = ds.batch(32).prefetch(1)
    backcast = model.predict(ds)
    return backcast

def plot_series(time, series, format = "-", start=0, end=None):
    plt.plot(time[start:end], series[start:end], format)
    plt.xlabel("time")
    plt.ylabel("value")
    plt.grid(True)
    
    
# cargar datos de mean sunspot y graficar

time_step = []
mean_sunspot = []

with open(r'C:\Users\Carlos\Downloads\sunspots.csv') as csvfile:
  reader = csv.reader(csvfile, delimiter = ',')
  next(reader)
  for row in reader:
    time_step.append(int(row[0]))
    mean_sunspot.append(float(row[2]))


time = np.array(time_step)
series = np.array(mean_sunspot)
plt.figure(figsize=(10,6))
plot_series(time,series)


# ahora revertimos el orden de las series desde el presente hacia el pasado
# series son los datos

time = np.array(time_step)
series = np.array(mean_sunspot)
series = series[::-1]
plt.figure(figsize=(10,6))
plot_series(time,series)

# ahora separamos hasta el tiempo que queremos entrenar y el de validar 
split_time = 3000
time_train = time[:split_time]
ss_train = series[:split_time]
time_valid = time[split_time:]
ss_valid = series[split_time:]

# parámetros de ventana de tiempo, batch y buffer
window_size = 30
batch_size = 32
shuffle_buffer_size = 1000

plt.figure(figsize=(10,6))
plot_series(time_train,ss_train)

# ahora construir y entrenar el modelo

tf.keras.backend.clear_session()
tf.random.set_random_seed(51)
np.random.seed(51)
train_set = windowed_dataset(ss_train, window_size=60, batch_size=30, shuffle_buffer=shuffle_buffer_size)
model = tf.keras.models.Sequential([
  tf.keras.layers.Conv1D(filters=80, kernel_size=5,
                      strides=1, padding="causal",
                      activation="relu",
                      input_shape=[None, 1]),
  tf.keras.layers.LSTM(60, return_sequences=True),
  tf.keras.layers.LSTM(60, return_sequences=True),
  tf.keras.layers.Dense(30, activation="relu"),
  tf.keras.layers.Dense(10, activation="relu"),
  tf.keras.layers.Dense(1),
  tf.keras.layers.Lambda(lambda x: x * 400)
])

optimizer = tf.keras.optimizers.SGD(lr=8e-6, momentum=0.9)
model.compile(loss=tf.keras.losses.Huber(),
              optimizer=optimizer,
              metrics=["mae"])
history = model.fit(train_set,epochs=500)

rnn_backcast = model_backcast(model, series[...,np.newaxis], window_size)
rnn_backcast = rnn_backcast[split_time-window_size:-1, -1, 0]
print(rnn_backcast.shape)

# graficar la serie modelada y los datos de validacion
plt.figure(figsize=(10, 6))
plot_series(time_valid, ss_valid[::-1])
plot_series(time_valid, rnn_backcast[::-1])

model.save('my_model_new.h5')