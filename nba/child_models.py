import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
import pandas as pd

BATCH_SIZE = 1
EPOCH = 100
LEARN_RATE = .0001

files = ['home', 'player']
y = np.load('../data/y.npy')
class PrintDot(keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs):
    if epoch % 100 == 0: print('')
    print('.', end='')

for file in files:
  print(f'loading {file}')
  matrix = np.load(f'../data/{file}.npy')
  print(f'Matrix shape {matrix.shape}')
  width = matrix.shape[1]
  model = keras.Sequential([
      layers.Dense(width, activation='relu', input_shape=[width]),
      layers.Dense(width, activation='relu'),
      layers.Dense(1)
  ])

  optimizer = keras.optimizers.RMSprop(LEARN_RATE)

  model.compile(loss='mse', optimizer=optimizer, metrics=['mae', 'mse'])
  print(file)
  history = model.fit(matrix, y, epochs=EPOCH, validation_split = 0.4, callbacks=[PrintDot()])
  model.save(file)
  print(model.predict(matrix[:100, :]))
  print(y[:100])