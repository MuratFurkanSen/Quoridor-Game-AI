import pygame

pygame.init()


class LevelCreator:
    def __init__(self):
        self.display = pygame.display.set_mode((530, 530))
        self.maze = [[[0, 0] for _ in range(9)] for _ in range(9)]
        self.clock = pygame.time.Clock()
        self.activeWalls = list()
        test_walls = [
    "vwall-4-4",
    "vwall-5-4",
    "hwall-1-6",
    "hwall-1-7",
    "vwall-5-6",
    "vwall-6-6",
    "hwall-2-6",
    "hwall-2-7",
    "hwall-0-4",
    "hwall-0-5",
    "hwall-7-7",
    "hwall-7-8",
    "hwall-4-0",
    "hwall-4-1",
    "vwall-3-6",
    "vwall-4-6",
    "hwall-6-2",
    "hwall-6-3",
    "hwall-4-5",
    "hwall-4-6",
    "vwall-6-3",
    "vwall-7-3",
    "vwall-4-1",
    "vwall-5-1",
    "vwall-1-7",
    "vwall-2-7",
    "hwall-5-3",
    "hwall-5-4",
    "vwall-6-1",
    "vwall-7-1",
    "hwall-6-7",
    "hwall-6-8"
]
        for i in test_walls:
            alg = 0 if i.startswith("vwall") else 1
            y, x = map(int, i.split("-")[1:])
            self.maze[y][x][alg] = 1
        self._updateUI()

    def loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                CellID = x // 60, y // 60
                isVer = (x % 60) - 50 > 0
                isHor = (y % 60) - 50 > 0
                if isHor and isVer:
                    pass
                elif isVer:
                    next_state = 0 if self.maze[CellID[1]][CellID[0]][0] else 1
                    self.maze[CellID[1]][CellID[0]][0] = next_state
                    self.maze[CellID[1] + 1][CellID[0]][0] = next_state
                    if next_state:
                        self.activeWalls.append((*CellID, 0))
                    else:
                        self.activeWalls.remove((*CellID, 0))
                elif isHor:
                    next_state = 0 if self.maze[CellID[1]][CellID[0]][1] else 1
                    self.maze[CellID[1]][CellID[0]][1] = next_state
                    self.maze[CellID[1]][CellID[0] + 1][1] = next_state
                    if next_state:
                        self.activeWalls.append((*CellID, 1))
                    else:
                        self.activeWalls.remove((*CellID, 1))
                print((len(self.activeWalls)))
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    mode = input("For which mode do u want to create this level for(Move-M/Wall-W)").upper()
                    maxTurn = input("Pls Enter The Max Turn for this Level: ")
                    maxGame = input("Pls Enter The Max Game for this Level: ")
                    epsilon = input("Pls Enter The Epsilon Value for this Level: ")
                    if mode == "M":
                        with open("./Game/MoveLevels", "a+") as File:
                            File.write(f"{self.maze}")
                            File.write("\n")
                            File.write(f"{self.activeWalls}")
                            File.write("\n")
                            File.write(f"{maxTurn}\n{maxGame}\n{epsilon}")
                            File.write("\n")

                    if mode == "W":
                        with open("./Game/WallLevels", "a+") as File:
                            File.write(f"{self.maze}")
                            File.write("\n")
                            File.write(f"{self.activeWalls}")
                            File.write("\n")
                            File.write(f"{maxTurn}\n{maxGame}\n{epsilon}")
                            File.write("\n")
                        print("Level Saved")
                if event.key == pygame.K_ESCAPE:
                    self.maze = [[[0, 0] for _ in range(9)] for _ in range(9)]
                    self.activeWalls = []
        self._updateUI()
        self.clock.tick(30)

    def _updateUI(self):
        # Screen
        self.display.fill((0, 255, 255))
        # Walls
        x, y = 0, 0
        for id_Y, row in enumerate(self.maze):
            for id_X, cell in enumerate(row):
                verColor = (125, 164, 180) if cell[0] == 0 else (95, 33, 45)
                horColor = (125, 164, 180) if cell[1] == 0 else (95, 33, 45)
                if x != 480:
                    pygame.draw.rect(self.display, verColor, (x + 50, y, 10, 50))
                if y != 480:
                    pygame.draw.rect(self.display, horColor, (x, y + 50, 50, 10))
                x += 60
            x = 0
            y += 60
        pygame.display.flip()

    def start(self):
        while True:
            self.loop()
