from .Pawn import Pawn, Direction
import pygame
import copy

pygame.init()


class QuoridorGame:
    def __init__(self, name):
        # Setting up Screen
        self.display = pygame.display.set_mode((550, 600))
        self.clock = pygame.time.Clock()

        # Game Variables
        self.name = name
        self.maxTurn = 100
        self.n_turns = 0
        self.maze = list()
        self.levels = list()
        self.level = 0
        self.currLevel = 0
        self.speed = 1
        self.selection = 0
        self.activeWalls = list()
        self.highlighted = list()
        self.playerPawn = None
        self.opponentPawn = None
        self.playerTurn = True
        self.exit = False
        self.maxGame = 0
        self.epsilonStart = 0
        if self.name == "Move_Mode":
            with open(r"./Game/MoveLevels.txt", "r") as File:
                for line in File:
                    # Maze, ActiveWalls, MaxTurn, MaxGame, Epsilon
                    maze = eval(line.strip("\n"))
                    activeWalls = eval(File.readline().strip("\n"))
                    maxTurn = eval(File.readline().strip("\n"))
                    maxGame = eval(File.readline().strip("\n"))
                    epsilon = eval(File.readline().strip("\n"))
                    level = (maze, activeWalls, maxTurn, maxGame, epsilon)
                    self.levels.append(level)
        else:
            with open(r"./Game/WallLevels.txt", "r") as File:
                for line in File:
                    # Maze, ActiveWalls, MaxTurn, MaxGame, Epsilon
                    maze = eval(line.strip("\n"))
                    activeWalls = eval(File.readline().strip("\n"))
                    maxTurn = eval(File.readline().strip("\n"))
                    maxGame = eval(File.readline().strip("\n"))
                    epsilon = eval(File.readline().strip("\n"))
                    level = (maze, activeWalls, maxTurn, maxGame, epsilon)
                    self.levels.append(level)
        self.reset()
        self.start_dis = self.playerPawn.closestPathLength()
        self.opp_start_dis = self.opponentPawn.closestPathLength()

    def reset(self):
        # Create Maze
        # Vertical Wall, Horizontal Wall
        self.currLevel = self.level
        levelPieces = self.levels[self.level]
        self.maze[:] = copy.deepcopy(levelPieces[0])
        self.activeWalls[:] = copy.deepcopy(levelPieces[1])
        self.maxTurn = levelPieces[2]
        self.maxGame = levelPieces[3]
        self.epsilonStart = levelPieces[4]
        self.n_turns = 0
        self.playerTurn = True

        if self.playerPawn is None:
            self.playerPawn = Pawn("Player", 4, 8, self.maze, self.activeWalls)
            self.opponentPawn = Pawn("Opponent", 4, 0, self.maze, self.activeWalls)
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
        playerScore = 0
        oppScore = 0
        gameOver = False

        # Collect inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.exit = True

                changeVal = 0
                if event.key == pygame.K_SPACE:
                    self.speed = 20
                if event.key == pygame.K_TAB:
                    self.selection = (self.selection + 1) % 3
                if event.key == pygame.K_UP and self.selection == 0:
                    changeVal += 10
                if event.key == pygame.K_LEFT:
                    changeVal -= 1
                if event.key == pygame.K_RIGHT:
                    changeVal += 1
                if event.key == pygame.K_DOWN and self.selection == 0:
                    changeVal -= 10
                if self.selection == 0:
                    self.speed += changeVal
                elif self.selection == 1:
                    self.level += changeVal
                elif self.selection == 2:
                    self.maxTurn += changeVal
        old_dis = self.playerPawn.closestPathLength() if self.playerTurn else self.opponentPawn.closestPathLength()
        old_opp_dis = self.opponentPawn.closestPathLength() if self.playerTurn else self.playerPawn.closestPathLength()

        # Play Action
        if isinstance(action, Direction):
            if self.playerTurn:
                self.playerPawn.move(action)
            else:
                self.opponentPawn.move(action)
        else:
            if self.playerTurn:
                self.playerPawn.placeWall(action)
                self.activeWalls.append(action)
            else:
                self.opponentPawn.placeWall(action)
                self.activeWalls.append(action)
        new_dis = self.playerPawn.closestPathLength() if self.playerTurn else self.opponentPawn.closestPathLength()
        new_opp_dis = self.opponentPawn.closestPathLength() if self.playerTurn else self.playerPawn.closestPathLength()

        # Rewards
        if isinstance(action, Direction):
            reward += (old_dis - new_dis if self.playerTurn else old_opp_dis - new_opp_dis) * 10
        else:
            reward += (new_opp_dis - old_opp_dis if self.playerTurn else new_dis - old_dis) * 10

        # Check if one of the Pawns reached their target
        if self.playerPawn.isTargetReached() or self.opponentPawn.isTargetReached() or self.n_turns > self.maxTurn:
            if isinstance(action, Direction):
                playerScore = 100 - (self.n_turns - (self.start_dis + self.playerPawn.closestPathLength()))
                oppScore = 100 - (self.opp_start_dis + 0.5 + self.opponentPawn.closestPathLength()) * 2
            else:
                playerScore = (self.opponentPawn.closestPathLength() - self.opp_start_dis)*10
                oppScore = (self.playerPawn.closestPathLength() - self.start_dis)*10
            print(len(self.activeWalls))
            gameOver = True
        # Turn Calculations
        self.n_turns += 0.5
        self.playerTurn = not self.playerTurn
        # Update UI
        self._updateUI()
        self.clock.tick(self.speed)
        return reward, gameOver, playerScore, oppScore

    def _updateUI(self):
        self.display.fill((0, 255, 255))
        frameColor = (50, 79, 90)
        font_color = (255, 0, 0)
        text_highlight = (255, 0, 255)
        # --Frame
        # -Top Up
        pygame.draw.rect(self.display, frameColor, (0, 0, 550, 10))
        # -Top Down
        pygame.draw.rect(self.display, frameColor, (0, 50, 550, 10))
        # -Left
        pygame.draw.rect(self.display, frameColor, (0, 0, 10, 600))
        # -Right
        pygame.draw.rect(self.display, frameColor, (540, 0, 10, 600))
        # -Bottom
        pygame.draw.rect(self.display, frameColor, (0, 590, 550, 10))
        # --Info
        font = pygame.font.Font(None, 32)
        speed = rf"SPEED: {self.speed}"
        level = rf"LEVEL(C\N\M): {self.currLevel} {self.level} {len(self.levels)-1}"
        turn = rf"MAX_TURN: {self.maxTurn}"

        speed_text = font.render(speed, True, text_highlight if self.selection == 0 else font_color)
        levels_text = font.render(level, True, text_highlight if self.selection == 1 else font_color)
        turns_text = font.render(turn, True, text_highlight if self.selection == 2 else font_color)
        self.display.blit(speed_text, (10, 10))
        self.display.blit(levels_text, (150, 10))
        self.display.blit(turns_text, (370, 10))

        # Squares
        self.highlighted.clear()
        moves = self.playerPawn.possibleMoves() if self.playerTurn else self.opponentPawn.possibleMoves()
        for move in moves:
            self.highlighted.append(self.playerPawn.tempMove(move)
                                    if self.playerTurn else self.opponentPawn.tempMove(move))
        # Walls
        x, y = 10, 60
        for id_Y, row in enumerate(self.maze):
            for id_X, cell in enumerate(row):
                if (id_X, id_Y) in self.highlighted:
                    pygame.draw.rect(self.display, (243, 255, 106), (x, y, 50, 50))
                verColor = (125, 164, 180) if cell[0] == 0 else (95, 33, 45)
                horColor = (125, 164, 180) if cell[1] == 0 else (95, 33, 45)
                if id_X != len(self.maze[0]) - 1:
                    pygame.draw.rect(self.display, verColor, (x + 50, y, 10, 50))
                if id_Y != len(self.maze) - 1:
                    pygame.draw.rect(self.display, horColor, (x, y + 50, 50, 10))
                x += 60
            x = 10
            y += 60
            
        # Pawns
        pawn_x, pawn_y = self.playerPawn.x * 60 + 35, self.playerPawn.y * 60 + 85
        pygame.draw.circle(self.display, self.playerPawn.color, (pawn_x, pawn_y), 15)
        pawn_x, pawn_y = self.opponentPawn.x * 60 + 35, self.opponentPawn.y * 60 + 85
        pygame.draw.circle(self.display, self.opponentPawn.color, (pawn_x, pawn_y), 15)
        pygame.display.flip()

if __name__ == "__main__":
    game = QuoridorGame()

    while True:
        gameOver = None
        if gameOver:
            break
