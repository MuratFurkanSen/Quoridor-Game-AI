from .Pawn import Pawn, Direction
import pygame
import random

pygame.init()

SPEED = 120

class QuoridorGame:
    def __init__(self, maze=None):
        # Setting up Screen
        self.display = pygame.display.set_mode((530, 530))
        clock = pygame.time.Clock()

        # Game Variables
        self.n_turns = 0
        self.maze = maze
        self.activeWalls = list()
        self.highlighted = list()
        self.playerPawn = None
        self.opponentPawn = None
        self.playerTurn = True
        self.nope = False
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        # Create Maze
        # Vertical Wall, Horizontal Wall
        if self.maze is None:
            self.maze = [[[0, 0] for _ in range(9)] for __ in range(9)]
        else:
            for i in range(len(self.maze)):
                for j in range(len(self.maze[0])):
                    self.maze[i][j] = [0, 0]
        self.activeWalls = []
        self.n_turns = 0
        self.playerTurn = True

        if self.playerPawn is None:
            self.playerPawn = Pawn("Player", 4, 8, self.maze)
            self.opponentPawn = Pawn("Opponent", 4, 0, self.maze)
            self.playerPawn.setOpponent(self.opponentPawn)
            self.opponentPawn.setOpponent(self.playerPawn)
        else:
            self.nope = True
            self.playerPawn.x = 4
            self.playerPawn.y = 8
            self.playerPawn.remainingWalls = 10
            self.opponentPawn.x = 4
            self.opponentPawn.y = 0
            self.opponentPawn.remainingWalls = 10

        self._updateUI()

    def playTurn(self, action):
        """Plays the given Action and returns (reward,gameOver, score)"""
        # Return Values
        reward = 0
        score = 0
        gameOver = False
        # Action Validation
        if len(action) == 2:
            try:
                action = Direction(action)
            except ValueError:
                reward -= 200
                return reward, gameOver, score
            moves = self.playerPawn.possibleMoves() if self.playerTurn else self.opponentPawn.possibleMoves()
            if action not in moves:
                reward -= 50
                return reward, gameOver, score
        else:
            walls = self.playerPawn.possibleWalls() if self.playerTurn else self.opponentPawn.possibleWalls()
            wallLeft = self.playerPawn.remainingWalls if self.playerTurn else self.opponentPawn.remainingWalls
            if wallLeft < 0:
                reward -= 100
                return reward, gameOver, score
            if action not in walls:
                reward -= 30
                return reward, gameOver, score

            self.playerPawn.placeWall(action)
            if not (self.playerPawn.canReachEnd() and self.opponentPawn.canReachEnd()):
                reward -= 20
                self.playerPawn.removeWall(action)
                return reward, gameOver, score
            self.playerPawn.removeWall(action)


        # Collect inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    action = Direction.LEFT
                elif event.key == pygame.K_RIGHT:
                    action = Direction.RIGHT
                elif event.key == pygame.K_UP:
                    action = Direction.UP
                elif event.key == pygame.K_DOWN:
                    action = Direction.DOWN
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.playerTurn = not self.playerTurn

        old_dis = self.playerPawn.closestPathLength() if self.playerTurn else self.opponentPawn.closestPathLength()
        old_opp_dis = self.opponentPawn.closestPathLength() if self.playerTurn else self.playerPawn.closestPathLength()

        # Play Action
        if action == "Test":
            pass
        elif self.playerTurn:
            if isinstance(action, Direction):
                self.playerPawn.move(action)
            else:
                self.playerPawn.placeWall(action)
        else:
            if isinstance(action, Direction):
                self.opponentPawn.move(action)
            else:
                self.activeWalls.append(action)
                self.opponentPawn.placeWall(action)
        new_dis = self.playerPawn.closestPathLength() if self.playerTurn else self.opponentPawn.closestPathLength()
        new_opp_dis = self.opponentPawn.closestPathLength() if self.playerTurn else self.playerPawn.closestPathLength()

        # Rewards
        if new_opp_dis - new_dis > 0 and isinstance(action, Direction):
            reward += 15
        if new_dis - new_opp_dis > 0 and not isinstance(action, Direction):
            reward += 15

        reward += 10 if self.playerPawn.remainingWalls > self.opponentPawn.remainingWalls else 0
        reward += (old_dis - new_dis) * 30
        reward += (new_opp_dis - old_opp_dis) * 20

        # Check if one of the Pawns reached their target
        if self.playerPawn.isTargetReached() or self.opponentPawn.isTargetReached() or self.n_turns > 150:
            if self.n_turns < 30:
                reward += 30
                score += 100
            reward += 15
            score += 100
            score += new_opp_dis * 40
            score += (self.playerPawn.remainingWalls if self.playerTurn else self.opponentPawn.remainingWalls) * 10
            score = 0 if self.n_turns > 150 else score
            gameOver = True
        # Turn Calculations
        self.n_turns += 0.5
        self.playerTurn = not self.playerTurn
        # Update UI
        self._updateUI()
        self.clock.tick(SPEED)
        return reward, gameOver, score

    def _updateUI(self):
        self.display.fill((0, 255, 255))
        # Squares
        self.highlighted.clear()
        moves = self.playerPawn.possibleMoves() if self.playerTurn else self.opponentPawn.possibleMoves()
        for move in moves:
            self.highlighted.append(self.playerPawn.tempMove(move)
                                    if self.playerTurn else self.opponentPawn.tempMove(move))
        # Walls
        x, y = 0, 0
        for id_Y, row in enumerate(self.maze):
            for id_X, cell in enumerate(row):
                if (id_X, id_Y) in self.highlighted:
                    pygame.draw.rect(self.display, (243, 255, 106), (x, y, 50, 50))
                verColor = (125, 164, 180) if cell[0] == 0 else (95, 33, 45)
                horColor = (125, 164, 180) if cell[1] == 0 else (95, 33, 45)
                if x != 480:
                    pygame.draw.rect(self.display, verColor, (x + 50, y, 10, 50))
                if y != 480:
                    pygame.draw.rect(self.display, horColor, (x, y + 50, 50, 10))
                x += 60
            x = 0
            y += 60
        # Pawns
        pawn_x, pawn_y = self.playerPawn.x * 60 + 25, self.playerPawn.y * 60 + 25
        pygame.draw.circle(self.display, self.playerPawn.color, (pawn_x, pawn_y), 15)
        pawn_x, pawn_y = self.opponentPawn.x * 60 + 25, self.opponentPawn.y * 60 + 25
        pygame.draw.circle(self.display, self.opponentPawn.color, (pawn_x, pawn_y), 15)
        pygame.display.flip()


if __name__ == "__main__":
    game = QuoridorGame()

    while True:
        gameOver = None
        if gameOver:
            break
