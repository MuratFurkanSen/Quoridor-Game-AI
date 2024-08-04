import random
from collections import deque

from pygments.lexers import pawn

from Game.Game import QuoridorGame
from Model import QLinearNet, QTrainer
from Game.Pawn import Direction
from helper import plot
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
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = QLinearNet(68, 256, 512, 256, 16)
        self.trainer = QTrainer(self.model, LR, self.gamma)

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
        self.epsilon = 256 - self.n_games
        if random.randint(0, 256) < self.epsilon:
            if random.randint(0, 1) and self.pawn.remainingWalls > 0:
                move = random.choice(self.pawn.possibleWalls())
            else:
                move = random.choice(self.pawn.possibleMoves()).value
        else:
            """
            --ActionSet in Binary
            0,1 = Move X
            2 = Move X + or -
            3,4 = Move Y
            5 = Move Y + or -
            6, 7, 8, 9 = PlaceWall X
            10, 11, 12, 13 = PlaceWall Y
            14 = PlaceWall Alignment
            15 = Decision Between Move and PlaceWall"""
            state0 = torch.tensor(state, dtype=torch.float)

            prediction = self.model(state0).tolist()
            prediction = list(map(lambda x: "1" if x >= 0.5 else "0", prediction))
            if int(prediction[-1]):
                move_x = int("".join(prediction[:2])*1 if prediction[2] else -1, 2)
                move_y = int("".join(prediction[3:5])*1 if prediction[5] else -1, 2)
                move = (move_x, move_y)
            else:
                wall_x = int("".join(prediction[6:10]), 2)
                wall_y = int("".join(prediction[10:14]), 2)
                alg = int(prediction[14])
                move = (wall_x, wall_y, alg)
        return move


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
            print(f"{playerAgent.n_games}. Game")
            print(f"Player Score: {playerScore}")
            print(f"Opponent Score: {opponentScore}")

            if playerScore > playerRecord:
                playerRecord = playerScore
                playerAgent.model.save("Player_Model.pth")
            if opponentScore > opponentRecord:
                opponentRecord = opponentScore
                opponentAgent.model.save("Opponent_Model.pth")
            playerScores.append(playerScore)
            opponentScores.append(opponentScore)

            playerTotalScore += playerScore
            opponentTotalScore += opponentScore
            playerMeanScore = playerTotalScore / playerAgent.n_games
            opponentMeanScore = playerTotalScore / opponentAgent.n_games
            playerMeanScores.append(playerMeanScore)
            opponentMeanScores.append(opponentMeanScore)

            plot(playerScores, playerMeanScores, opponentScores, opponentMeanScores)


if __name__ == '__main__':
    train()