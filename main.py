import pygame
import os
from AI import Agent, Agent_Move, Agent_Wall
from Game.LevelCreator import LevelCreator

pygame.init()

# Choose one of the modes via indices
modes = ["Decision", "Move", "Wall", "Level Creator"]
mode = modes[3]

# Print Modes
for index, currMode in enumerate(modes):
    print(f"{index}: {currMode}")
# Select Mode
Input = input("Pls Enter the Mode Do U Want to Choose(as Num): ")

if Input == "":
    pass
else:
    mode = modes[int(Input)]

if mode == "Decision":
    Agent.train()
elif mode == "Move":
    Agent_Move.train()
elif mode == "Wall":
    Agent_Wall.train()
elif mode == "Level Creator":
    creator = LevelCreator()
    creator.start()
