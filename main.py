import pygame
from Game.Game import QuoridorGame
pygame.init()

game = QuoridorGame()
while True:
    values = game.playTurn("Test")
    print("Is Game Done: "+str(values[1]))
    if values[1]:
        game.reset()


