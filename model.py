import torch # pytorch
import torch.nn as nn # neural network
import torch.optim as optim # optimizer
import torch.nn.functional as F # relu, tanh, etc.
import os # for saving and loading models

class Linear_QNet(nn.Module): # neural network class
    def __init__(self, input_size, hidden_size, output_size): 
        super().__init__()  # super class
        self.linear1 = nn.Linear(input_size, hidden_size) # input layer
        self.linear2 = nn.Linear(hidden_size, output_size) # hidden layer

    def forward(self, x): # forward propagation
        x = F.relu(self.linear1(x)) # relu activation function
        x = self.linear2(x) # output layer
        return x # return output
    
    def save(self, file_name = 'model.pth'): # save model
        model_folder_path = './model' # model folder path
        if not os.path.exists(model_folder_path): # if model folder does not exist
            os.makedirs(model_folder_path) # create model folder

        file_name = os.path.join(model_folder_path, file_name) # file path
        torch.save(self.state_dict(), file_name) # save model

class QTrainer: # Q-learning class
    def __init__(self, model, lr, gamma):
        self.lr = lr # learning rate
        self.gamma = gamma # discount rate
        self.model = model # model
        self.optimizer = optim.Adam(model.parameters(), lr = self.lr) # optimizer | Adam is a type of optimizer
        self.criterion = nn.MSELoss() # loss function


    def train_step(self, state, action, reward, next_state, done): # train step
        state = torch.tensor(state, dtype = torch.float) # convert to tensor
        next_state = torch.tensor(next_state, dtype = torch.float) # convert to tensor
        action = torch.tensor(action, dtype = torch.long) # convert to tensor
        reward = torch.tensor(reward, dtype = torch.float) # convert to tensor

        if len(state.shape) == 1: # if state is 1D
            state = torch.unsqueeze(state, 0) # add a dimension to the tensor
            next_state = torch.unsqueeze(next_state, 0) # add a dimension to the tensor
            action = torch.unsqueeze(action, 0) # add a dimension to the tensor
            reward = torch.unsqueeze(reward, 0) # add a dimension to the tensor
            done = (done, ) # convert to tuple

        # 1: predicted Q values with current state
        pred = self.model(state)

        # 2: Q_new = r + y * max(next_predicted Q value) -> only do this if not done
        target = pred.clone() # clone pred
        for idx in range(len(done)): # for each done
            Q_new = reward[idx] # if done, Q_new = reward
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx])) # if not done, Q_new = reward + gamma * max(next_predicted Q value)
            
            target[idx][torch.argmax(action[idx]).item()] = Q_new # target = pred | .item() gets the value of the tensor

        self.optimizer.zero_grad() # zero gradients
        loss = self.criterion(target, pred) # calculate loss
        loss.backward() # backpropagation
        self.optimizer.step() # update weights