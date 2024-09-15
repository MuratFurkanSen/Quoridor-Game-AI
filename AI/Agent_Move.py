import random
import time
from collections import deque
import os

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
        self.autoTrain = True

        # Training Values
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.startLevel = 0
        self.model = QLinearNet(name, 68, 16, 32, 16, 12)
        if not os.path.exists(f"model_saves/Move_{name}_Model.pth"):
            self.memory = deque(maxlen=MAX_MEMORY)
        else:
            checkpoint = torch.load(f"model_saves/Move_{name}_Model.pth")
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.memory = checkpoint['memory']
            self.n_games = checkpoint['n_games']
            self.startLevel = checkpoint['level']

        self.model = self.model.to(self.model.device)
        self.trainer = QTrainer(self.model, LR, self.gamma, self.model.device)

    def remember(self, state, action, reward, next_state, done, mask):
        self.memory.append((state, action, reward, next_state, done, mask))

    def train_short_memory(self, state, action, reward, next_state, done, mask):
        self.trainer.train_step(state, action, reward, next_state, done, mask)

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            sample = random.sample(self.memory, BATCH_SIZE)
        else:
            sample = self.memory
        # List of Each One
        state, action, reward, next_state, done, mask = zip(*sample)
        self.trainer.train_step(state, action, reward, next_state, done, mask)

    def get_state(self):
        """
        Will Return State that Contain:
        Current Location
        Opponent Location
        Distance to target
        Opponent's distance to target
        Remaining Walls of Opponent
        Remaining Walls
        Active Walls 60 [0-9]
        Up_Wall 0-1
        Left_Wall 0-1
        Right_Wall 0-1
        Down_Wall 0-1
        """
        activeWalls = [*self.activeWalls] + [(-1, -1, -1)] * (20 - len(self.activeWalls))
        activeWalls = [j for i in activeWalls for j in i]
        state = [self.pawn.x, self.pawn.y,
                 self.opponent.x, self.opponent.y,
                 self.pawn.closestPathLength(),
                 self.opponent.closestPathLength(),
                 self.pawn.remainingWalls,
                 self.opponent.remainingWalls,
                 *activeWalls]
        return state

    def get_action(self, state, epsilonStart):
        # Mask for Valid Actions
        mask = self.createMask()
        self.epsilon = epsilonStart - self.n_games
        if random.randint(0, epsilonStart) < self.epsilon:
            action = random.choice(self.pawn.possibleMoves())
        else:
            state0 = torch.tensor(state, dtype=torch.float).to(self.model.device)
            prediction = self.model(state0)
            # Eliminate Invalid Actions
            valid_prediction = prediction * mask
            move_index = torch.argmax(valid_prediction).item()
            action = [*Direction][move_index]
        return action

    def createMask(self):
        valid_moves = self.pawn.possibleMoves()
        mask = torch.zeros(len(Direction)).to(self.model.device)
        for index, move in enumerate(Direction):
            if move in valid_moves:
                mask[index] = 1
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
    game = QuoridorGame("Move_Mode")
    playerAgent = Agent("Player", game.playerPawn, game.opponentPawn, game.activeWalls)
    opponentAgent = Agent("Opponent", game.opponentPawn, game.playerPawn, game.activeWalls)
    game.level = playerAgent.startLevel
    totalGames = 0
    while True:
        # Get Old State
        old_state = playerAgent.get_state() if game.playerTurn else opponentAgent.get_state()

        # Get Move
        move = playerAgent.get_action(old_state, game.epsilonStart) if game.playerTurn else opponentAgent.get_action(
            old_state, game.epsilonStart)


        # Take Action
        reward, done, playerScore, opponentScore = game.playTurn(move)
        if not game.playerTurn:
            print(move)
            print(reward)
            print("-----------")
        new_state = playerAgent.get_state() if game.playerTurn else opponentAgent.get_state()
        next_mask = playerAgent.createMask()

        # train short memory
        if game.playerTurn:
            opponentAgent.train_short_memory(old_state, move, reward, new_state, done, next_mask)
        else:
            playerAgent.train_short_memory(old_state, move, reward, new_state, done, next_mask)

        # Remember
        if game.playerTurn:
            opponentAgent.remember(old_state, move, reward, new_state, done, next_mask)
        else:
            playerAgent.remember(old_state, move, reward, new_state, done, next_mask)

        if done:
            # train long memory, plot result
            playerAgent.n_games += 1
            opponentAgent.n_games += 1
            totalGames += 1
            if playerAgent.autoTrain:
                if playerAgent.n_games > game.maxGame:
                    playerAgent.n_games = 0
                    opponentAgent.n_games = 0
                    game.level = (game.level + 1) % len(game.levels)
            game.reset()
            playerAgent.train_long_memory()
            opponentAgent.train_long_memory()
            print(time.ctime())
            print(f"{playerAgent.n_games}. Game")
            print(f"Player Score: {playerScore}")
            print(f"Opponent Score: {opponentScore}")
            if playerScore > playerRecord or playerAgent.n_games % 5 == 0:
                playerRecord = playerScore
                playerAgent.model.save(f"Player_Model_Move-{playerAgent.n_games}.pth")
            if opponentScore > opponentRecord or opponentAgent.n_games % 5 == 0:
                opponentRecord = opponentScore
                opponentAgent.model.save(f"Opponent_Model_Move-{opponentAgent.n_games}.pth")
            playerScores.append(playerScore)
            opponentScores.append(opponentScore)

            playerTotalScore += playerScore
            opponentTotalScore += opponentScore
            playerMeanScore = playerTotalScore / totalGames
            opponentMeanScore = playerTotalScore / totalGames
            playerMeanScores.append(playerMeanScore)
            opponentMeanScores.append(opponentMeanScore)

            plot(playerScores, playerMeanScores, opponentScores, opponentMeanScores)

            if game.exit:
                model = playerAgent.model
                torch.save({
                    'model_state_dict': model.state_dict(),
                    'memory': playerAgent.memory,
                    'level': game.level,
                    'n_games': playerAgent.n_games,
                }, 'model_saves/Move_Player_Model.pth')

                model = opponentAgent.model
                torch.save({
                    'model_state_dict': model.state_dict(),
                    'memory': playerAgent.memory,
                    'level': game.level,
                    'n_games': playerAgent.n_games,
                }, 'model_saves/Move_Opponent_Model.pth')
                quit()


if __name__ == '__main__':
    train()
