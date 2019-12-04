import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
import pandas as pd

BATCH_SIZE = 32
EPOCH = 100
LEARN_RATE = .001

files = ['empty']
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
      #layers.Dense(width, activation='relu', input_shape=[width]),
      #layers.Dense(width, activation='relu'),
      #layers.Dropout(rate=0.25),
      layers.Dense(1, input_shape=[width])
  ])
  optimizer = keras.optimizers.Adam(LEARN_RATE)

  model.compile(loss='mse', optimizer=optimizer, metrics=['mae', 'mse'])
  print(y)
  history = model.fit(matrix, y, epochs=EPOCH, batch_size=BATCH_SIZE, validation_split = 0.2, callbacks=[PrintDot()], shuffle=True)
  model.save(file)
