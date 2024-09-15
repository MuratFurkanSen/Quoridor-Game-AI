import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os
from Game.Pawn import Direction


class QLinearNet(nn.Module):
    def __init__(self, name, input_size, hidden1, hidden2, hidden3, output_size):
        super().__init__()
        self.name = name
        self.layer1 = nn.Linear(input_size, hidden1)
        self.layer2 = nn.Linear(hidden1, hidden2)
        self.layer3 = nn.Linear(hidden2, hidden3)
        self.layer4 = nn.Linear(hidden3, output_size)
        if torch.cuda.is_available():
            self.device = torch.device("cuda")

    def forward(self, x):
        x = F.relu(self.layer1(x)).to(self.device)
        x = F.relu(self.layer2(x)).to(self.device)
        x = F.relu(self.layer3(x)).to(self.device)
        x = F.sigmoid(self.layer4(x)).to(self.device)
        return x

    def save(self, file_name='model.pth'):
        model_folder_path = f'./models/Move_{self.name}/'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_name = os.path.join(model_folder_path, file_name)

        torch.save(self.state_dict(), file_name)


class QTrainer:
    def __init__(self, model, lr, gamma, device):
        self.lr = lr
        self.model = model
        self.gamma = gamma
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()
        self.device = device

    def train_step(self, state, action, reward, next_state, done, next_mask):
        state = torch.tensor(state, dtype=torch.float).to(self.device)
        next_state = torch.tensor(next_state, dtype=torch.float).to(self.device)
        if isinstance(action, tuple):
            if isinstance(action[0], Direction):
                action = torch.tensor([i.value for i in action]).to(self.device)
            else:
                action = torch.tensor(action).to(self.device)
        else:
            action = torch.tensor(action.value).to(self.device)

        reward = torch.tensor(reward, dtype=torch.float).to(self.device)
        # (n, x)

        if len(state.shape) == 1:
            # (1, x)
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            next_mask = torch.unsqueeze(next_mask, 0)
            done = (done,)

        # 1: predicted Q values with current state
        """
        First Q Approach
        pred = self.model(state)
        target = pred.clone()
        for idx in range(len(done)):
        
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))
            

            target[idx][torch.argmax(action[idx]).item()] = Q_new
        """
        """
        Second Q Approach
        with torch.no_grad():
        next_q_values = q_network(next_state_tensor)
        next_q_values_valid = next_q_values * mask
        target_q_value = reward + gamma * torch.max(next_q_values_valid).item()
        """
        # Result
        pred = self.model(state)
        target = pred.clone()
        for index in range(len(done)):
            Q_new = reward[index]
            if not done[index]:
                Q_new = reward[index] + self.gamma * torch.max(self.model(next_state[index]) * next_mask[index])
            target[index][torch.argmax(action[index]).item()] = Q_new

        loss = self.criterion(target, pred)
        loss.backward()
        self.optimizer.step()
