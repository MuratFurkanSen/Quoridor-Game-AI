import os
import random
import time
from collections import deque

from Game.Game import QuoridorGame
from AI.Model import QLinearNet, QTrainer
from Game.Pawn import Direction
from AI.helper import plot
import torch

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001


class Agent:
    def __init__(self, name, pawn, opponent, activeWalls):
        # For ID
        self.name = name
        self.pawn = pawn
        self.opponent = opponent
        self.activeWalls = activeWalls

        # Training Values
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.model = QLinearNet(name, 68, 64, 128, 64, 1)
        if not os.path.exists(f"model_saves/Move_{name}_Model.pth"):
            self.memory = deque(maxlen=MAX_MEMORY)
        else:
            checkpoint = torch.load(f"model_saves/Move_{name}_Model.pth")
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            self.memory = checkpoint['memory']
        self.model = self.model.to(self.model.device)
        self.trainer = QTrainer(self.model, LR, self.gamma, self.model.device)

        self.Move_AI = QLinearNet(name, 68, 64, 128, 64, 12)
        self.Wall_AI = QLinearNet(name, 68, 64, 128, 64, 128)
        self.Move_AI.load_state_dict(torch.load(f"{name}_Move.pth", weights_only=False))
        self.Wall_AI.load_state_dict(torch.load(f"{name}_Wall.pth", weights_only=False))
        self.Move_AI.eval()
        self.Wall_AI.eval()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            sample = random.sample(self.memory, BATCH_SIZE)
        else:
            sample = self.memory
        # List of Each One
        state, action, reward, next_state, done = zip(*sample)
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_state(self):
        """
        Will Return State that Contain:
        Current Location
        Opponent Location
        Distance to target
        Opponent's distance to target
        Remaining Walls of Opponent
        Remaining Walls
        Active Walls
        """
        activeWalls = [*self.activeWalls] + [(-1, -1, -1)]*(20 - len(self.activeWalls))
        activeWalls = [j for i in activeWalls for j in i]
        state = [self.pawn.x, self.pawn.y,
                 self.opponent.x, self.opponent.y,
                 self.pawn.closestPathLength(),
                 self.opponent.closestPathLength(),
                 self.pawn.remainingWalls,
                 self.opponent.remainingWalls,
                 *activeWalls]
        return state

    def get_action(self, state):
        """
         ---ActionSet
         --Move()
         -PossibleMoves
         --PlaceWall
         -WallID'S
        """
        self.epsilon = 2 - self.n_games
        if random.randint(0, 256) < self.epsilon:
            if random.randint(0, 1) and self.pawn.remainingWalls > 0:
                move = random.choice(self.pawn.possibleWalls())
            else:
                move = random.choice(self.pawn.possibleMoves()).value
        else:
            state0 = torch.tensor(state, dtype=torch.float).to(self.model.device)
            prediction = self.model(state0).tolist()
            if round(prediction[0]):
                move_pred = self.model(state0)
                # Eliminate Invalid Actions
                valid_pred = move_pred * self.createMoveMask()
                move_index = torch.argmax(valid_pred).item()
                action = [*Direction][move_index]
            else:
                state0 = torch.tensor(state, dtype=torch.float).to(self.model.device)
                prediction = self.model(state0)
                # Eliminate Invalid Actions
                q_values_valid = prediction * self.createWallMask()
                Wall_ID = torch.argmax(q_values_valid).item()
                action = (Wall_ID // 16, (Wall_ID % 16) // 2, Wall_ID % 2)
            return action

    def createMoveMask(self):
        valid_moves = self.pawn.possibleMoves()
        mask = torch.zeros(len(Direction)).to(self.model.device)
        for index, move in enumerate(Direction):
            if move in valid_moves:
                mask[index] = 1
        return mask

    def createWallMask(self):
        # Has a bug indices can be same with this method
        mask = torch.ones(128).to(self.model.device)
        for wall in self.activeWalls:
            index = wall[0]*9 + wall[1]+wall[2]
            mask[index] = 0
        return mask


def train():
    playerScores = []
    playerMeanScores = []
    opponentScores = []
    opponentMeanScores = []
    playerTotalScore = 0
    opponentTotalScore = 0
    playerRecord = 0
    opponentRecord = 0
    game = QuoridorGame()
    playerAgent = Agent("Player", game.playerPawn, game.opponentPawn, game.activeWalls)
    opponentAgent = Agent("Opponent", game.opponentPawn, game.playerPawn, game.activeWalls)
    playerScore = 0
    opponentScore = 0

    while True:
        # Get Old State
        old_state = playerAgent.get_state() if game.playerTurn else opponentAgent.get_state()

        # Get Move
        move = playerAgent.get_action(old_state) if game.playerTurn else opponentAgent.get_action(old_state)

        # Take Action
        reward, done, score = game.playTurn(move)
        new_state = playerAgent.get_state() if game.playerTurn else opponentAgent.get_state()

        # train short memory
        if game.playerTurn:
            opponentAgent.train_short_memory(old_state, move, reward, new_state, done)
        else:
            playerAgent.train_short_memory(old_state, move, reward, new_state, done)

        # Remember
        if game.playerTurn:
            opponentAgent.remember(old_state, move, reward, new_state, done)
        else:
            playerAgent.remember(old_state, move, reward, new_state, done)

        if game.playerTurn:
            opponentScore = score
        else:

            playerScore = score

        if done:
            # train long memory, plot result
            game.reset()
            playerAgent.n_games += 1
            opponentAgent.n_games += 1
            playerAgent.train_long_memory()
            opponentAgent.train_long_memory()
            print(time.ctime())
            print(f"{playerAgent.n_games}. Game")
            print(f"Player Score: {playerScore}")
            print(f"Opponent Score: {opponentScore}")

            if playerScore > playerRecord or playerAgent.n_games%5==0:
                playerRecord = playerScore
                playerAgent.model.save(f"Player_Model-{playerAgent.n_games}.pth")
            if opponentScore > opponentRecord or opponentAgent.n_games%5==0:
                opponentRecord = opponentScore
                opponentAgent.model.save(f"Opponent_Model-{opponentAgent.n_games}.pth")
            playerScores.append(playerScore)
            opponentScores.append(opponentScore)

            playerTotalScore += playerScore
            opponentTotalScore += opponentScore
            playerMeanScore = playerTotalScore / playerAgent.n_games
            opponentMeanScore = playerTotalScore / opponentAgent.n_games
            playerMeanScores.append(playerMeanScore)
            opponentMeanScores.append(opponentMeanScore)

            plot(playerScores, playerMeanScores, opponentScores, opponentMeanScores)
            if game.exit:
                model = playerAgent.model
                torch.save({
                    'model_state_dict': model.state_dict(),
                    'optimizer_state_dict': model.optimizer.state_dict(),
                    'memory': playerAgent.memory
                }, 'model_saves/Player_Model.pth')

                model = opponentAgent.model
                torch.save({
                    'model_state_dict': model.state_dict(),
                    'optimizer_state_dict': model.optimizer.state_dict(),
                    'memory': opponentAgent.memory
                }, 'model_saves/Opponent_Model.pth')
                quit()


if __name__ == '__main__':
    train()