import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
import pandas as pd

BATCH_SIZE = 32
EPOCH = 50
LEARN_RATE = .000001

files = ['full']
y = np.load('../data/y.npy')
class PrintDot(keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs):
    if epoch % 100 == 0: print('')
    print('.', end='')

for file in files:
  print(f'loading {file}')
  matrix = np.load(f'../data/{file}.npy')
  print(matrix.sum(axis=1))
  print(f'Matrix shape {matrix.shape}')
  width = matrix.shape[1]
  model = keras.Sequential([
      layers.Dense(width * 25, activation='relu', input_shape=[width]),
      layers.Dense(width * 10, activation='relu'),
      #layers.Dense(width * 2, activation='relu'),
      #layers.Dropout(rate=0.25),
      layers.Dense(1)
  ])
  optimizer = keras.optimizers.Adam(LEARN_RATE)

  model.compile(loss='mae', optimizer=optimizer, metrics=['mae', 'mse'])
  print(y)
  history = model.fit(matrix, y, epochs=EPOCH, batch_size=BATCH_SIZE, validation_split = 0.2, callbacks=[PrintDot()], shuffle=True)
  model.save(file)
