from enum import Enum


class Direction(Enum):
    UP = [0, -1]
    LEFT = [-1, 0]
    RIGHT = [1, 0]
    DOWN = [0, 1]

    DOUBLE_UP = [0, -2]
    DOUBLE_LEFT = [-2, 0]
    DOUBLE_RIGHT = [2, 0]
    DOUBLE_DOWN = [0, 2]

    UP_LEFT = [-1, -1]
    UP_RIGHT = [1, -1]
    DOWN_LEFT = [-1, 1]
    DOWN_RIGHT = [1, 1]


class Pawn:
    def __init__(self, name, x, y, maze, activeWalls):
        self.name = name
        self.x = x
        self.y = y
        self.remainingWalls = 10
        self.maze = maze
        self.color = (0, 255, 0) if self.name == "Player" else (255, 0, 0)
        self.target = 0 if name == "Player" else 8
        self.opponent = None
        self.nope = False
        self.activeWalls = activeWalls

    def setOpponent(self, opponent):
        self.opponent = opponent

    def closestPathLength(self):
        paths = list()
        paths.append([(self.x, self.y)])
        boolMap = [[False for _ in range(len(self.maze))] for __ in range(len(self.maze))]
        boolMap[self.y][self.x] = True
        while len(paths) > 0:
            i = 0
            length = len(paths)
            while i < length:
                path = paths[0]
                if path[-1] == [8, 8]:
                    pass
                moves = self.possibleMoves(*path[-1])
                for move in moves:
                    next_pos = [a + b for a, b in zip(path[-1], move.value)]
                    try:
                        if not boolMap[next_pos[1]][next_pos[0]]:
                            boolMap[next_pos[1]][next_pos[0]] = True
                            paths.append(path + [next_pos])
                            if paths[-1][-1][1] == self.target:
                                return len(paths[-1]) - 1
                    except IndexError:
                        print(next_pos)
                paths.pop(0)
                i += 1
        return -1

    def possibleMoves(self, x=-1, y=-1):
        """Returns the available possible moves for the
        given coordinates or current location of pawn when left blank."""
        if x == -1 or y == -1:
            x = self.x
            y = self.y
        moves = list()
        # --Move Checks
        # -Direction Up
        if y > 0 and self.maze[y - 1][x][1] == 0:
            # Next Cell is Empty
            if not (self.x == self.opponent.x and self.y - 1 == self.opponent.y):
                moves.append(Direction.UP)
            else:  # Next Cell Have Opponent
                if y - 1 > 0 and self.maze[y - 2][x][1] == 0:
                    moves.append(Direction.DOUBLE_UP)
                else:  # Wall Blocks Double Up
                    if x > 0 and self.maze[y - 1][x - 1][0] == 0:
                        moves.append(Direction.UP_LEFT)
                    if x < 8 and self.maze[y - 1][x][0] == 0:
                        moves.append(Direction.UP_RIGHT)
        # -Direction Left
        if x > 0 and self.maze[y][x - 1][0] == 0:
            # Next Cell is Empty
            if not (self.x - 1 == self.opponent.x and self.y == self.opponent.y):
                moves.append(Direction.LEFT)
            else:  # Next Cell Have Opponent
                if x - 1 > 0 and self.maze[y][x - 2][0] == 0:
                    moves.append(Direction.DOUBLE_LEFT)
                else:  # Wall Blocks Double Left
                    if y > 0 and self.maze[y - 1][x - 1][1] == 0:
                        moves.append(Direction.UP_LEFT)
                    if y < 8 and self.maze[y][x - 1][1] == 0:
                        moves.append(Direction.DOWN_LEFT)
        # -Direction Right
        if x < 8 and self.maze[y][x][0] == 0:
            # Next Cell is Empty
            if not (self.x + 1 == self.opponent.x and self.y == self.opponent.y):
                moves.append(Direction.RIGHT)
            else:  # Next Cell Have Opponent
                if x + 1 < 8 and self.maze[y][x + 1][0] == 0:
                    moves.append(Direction.DOUBLE_RIGHT)
                else:  # Wall Blocks Double Right
                    if y > 0 and self.maze[y - 1][x + 1][1] == 0:
                        moves.append(Direction.UP_RIGHT)
                    if y < 8 and self.maze[y][x + 1][1] == 0:
                        moves.append(Direction.DOWN_RIGHT)

        # -Direction Down
        if y < 8 and self.maze[y][x][1] == 0:
            # Next Cell is Empty
            if not (self.x == self.opponent.x and self.y + 1 == self.opponent.y):
                moves.append(Direction.DOWN)
            else:  # Next Cell Have Opponent
                if y + 1 < 8 and self.maze[y + 1][x][1] == 0:
                    moves.append(Direction.DOUBLE_DOWN)
                else:  # Wall Blocks Double Down
                    if x > 0 and self.maze[y + 1][x - 1][0] == 0:
                        moves.append(Direction.DOWN_LEFT)
                    if x < 8 and self.maze[y + 1][x][0] == 0:
                        moves.append(Direction.DOWN_RIGHT)
        return moves

    def move(self, moveDir):
        moveCords = moveDir.value
        self.x += moveCords[0]
        self.y += moveCords[1]

    def tempMove(self, moveDir):
        """Shows the """
        moveCords = moveDir.value
        return self.x + moveCords[0], self.y + moveCords[1]

    def possibleWalls(self):
        walls = list()
        if self.remainingWalls < 0:
            return walls
        for i in range(len(self.maze) - 1):
            for j in range(len(self.maze[i]) - 1):
                if self.maze[i][j][0] == self.maze[i + 1][j][0] == 0 and (i, j, 1) not in self.activeWalls:
                    self.placeWall((i, j, 0))
                    if self.canReachEnd() and self.opponent.canReachEnd:
                        walls.append((i, j, 0))
                    self.removeWall((i, j, 0))
                if self.maze[i][j][1] == self.maze[i][j + 1][1] == 0 and (i, j, 0) not in self.activeWalls:
                    self.placeWall((i, j, 1))
                    if self.canReachEnd() and self.opponent.canReachEnd():
                        walls.append((i, j, 1))
                    self.removeWall((i, j, 1))
                if not (self.canReachEnd() and self.opponent.canReachEnd()):
                    print("Shit")
        return walls

    def placeWall(self, wallID):
        self.remainingWalls -= 1
        y, x, alg = wallID
        self.maze[y][x][alg] = 1
        if alg == 0:
            y += 1
        else:
            x += 1
        self.maze[y][x][alg] = 1

    def removeWall(self, wallID):
        self.remainingWalls += 1
        y, x, alg = wallID
        self.maze[y][x][alg] = 0
        if alg == 0:
            y += 1
        else:
            x += 1
        self.maze[y][x][alg] = 0

    def canReachEnd(self):
        visitedCells = [(self.x, self.y)]
        currentPath = [(self.x, self.y)]
        virPawn = Pawn("Virtual", self.x, self.y, self.maze, self.activeWalls)
        virPawn.setOpponent(Pawn("Virtual Opponent", self.opponent.x, self.opponent.y, self.maze, self.activeWalls))
        while True:
            moves = virPawn.possibleMoves()
            isMoved = False
            for move in moves:
                if visitedCells.count(virPawn.tempMove(move)) == 0:
                    visitedCells.append(virPawn.tempMove(move))
                    currentPath.append(virPawn.tempMove(move))
                    virPawn.move(move)
                    isMoved = True
                    break
            if virPawn.y == self.target:
                return True
            if not isMoved:
                if len(currentPath) == 0:
                    break
                else:
                    virPawn.x, virPawn.y = currentPath.pop()
        return False

    def isTargetReached(self):
        return self.y == self.target
