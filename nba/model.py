import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable

BATCH_SIZE = 64
EPOCH = 200
LEARN_RATE = .01
class Net(torch.nn.Module):
    def __init__(self, n_feature, n_hidden, n_output):
        super(Net, self).__init__()
        self.hidden = torch.nn.Linear(n_feature, n_hidden)   # hidden layer
        self.predict = torch.nn.Linear(n_hidden, n_output)   # output layer

    def forward(self, x):
        x = F.relu(self.hidden(x))      # activation function for hidden layer
        x = self.predict(x)             # linear output
        return x


matrix = np.load('../data/matrix.npy')
print(f'Matrix shape {matrix.shape}')
y_train = matrix[:, 0]
x_train = matrix[:, 1:]
print(f'Y Shape {y_train.shape}')
print(f'X Shape {x_train.shape}')

net = Net(x_train.shape[1], x_train.shape[1], 1)
optimizer = torch.optim.SGD(net.parameters(), lr=LEARN_RATE)
loss_func = torch.nn.MSELoss()
x = Variable(torch.from_numpy(x_train))
y = Variable(torch.from_numpy(y_train))
for epoch in range(EPOCH):
    prediction = net(x)
    loss = loss_func(prediction, y)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    print(loss.item())