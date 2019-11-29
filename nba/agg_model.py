import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
import pandas as pd

BATCH_SIZE = 1
EPOCH = 50
LEARN_RATE = .0001

model_file_names = ['playing_time', 'home', 'dkp']
models = []
model_data = []
for model_file in model_file_names:
    models.append(keras.models.load_model(model_file))
for model_file_name in model_file_names:
    model_data.append(np.load(f'../data/{model_file_name}.npy'))
y = np.load('../data/y.npy')
matrix = np.load('../data/agg.npy')
model_results = []
index = 0
print('running pre predictions')
model_results = []
print('matrix shape: ' + str(matrix.shape))
for data in model_data:
    print(data.shape)
    matrix = np.append(matrix, models[index].predict(data), 1)
    print(matrix.shape)
    index += 1
print('matrix shape: ' + str(matrix.shape))
print('appending results')
print('training')
class PrintDot(keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs):
    if epoch % 100 == 0: print('')
    print('.', end='')
file = 'agg'
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
print(y)
history = model.fit(matrix, y, epochs=EPOCH, validation_split = 0.2, callbacks=[PrintDot()])
model.save(file)
