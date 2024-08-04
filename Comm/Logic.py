import torch
from Game.Pawn import Pawn, Direction
import random

AI = torch.load("Model.pth")

def get_state(pawn, opponent, activeWalls):
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
    activeWalls = [*activeWalls] + [(-1, -1, -1)] * (20 - len(activeWalls))
    activeWalls = [j for i in activeWalls for j in i]
    state = [pawn.x, pawn.y,
             opponent.x, opponent.y,
             pawn.closestPathLength(),
             opponent.closestPathLength(),
             pawn.remainingWalls,
             opponent.remainingWalls,
             *activeWalls]
    return state


def get_action(model, state, playerPawn, opponentPawn):
    """
     ---ActionSet
     --Move()
     -PossibleMoves
     --PlaceWall
     -WallID'S
    """
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

    prediction = model(state0).tolist()
    prediction = list(map(lambda x: "1" if x >= 0.5 else "0", prediction))
    if prediction[-1]:
        move_x = int("".join(prediction[:2]) * 1 if prediction[2] else -1, 2)
        move_y = int("".join(prediction[3:5]) * 1 if prediction[5] else -1, 2)
        action = (move_x, move_y)
    else:
        wall_x = int("".join(prediction[6:10]), 2)
        wall_y = int("".join(prediction[10:14]), 2)
        alg = int(prediction[14])
        action = (wall_x, wall_y, alg)
    if len(action) == 2:
        try:
            action = Direction(action)
        except ValueError:
            return randomMove(playerPawn, opponentPawn, "Move")
        moves = opponentPawn.possibleMoves()
        if action not in moves:
            return randomMove(playerPawn, opponentPawn, "Move")
    else:
        walls = opponentPawn.possibleWalls()
        wallLeft = opponentPawn.remainingWalls
        if action not in walls or wallLeft < 0:
            return randomMove(playerPawn, opponentPawn, "Wall")
        else:
            playerPawn.placeWall(action)
            if not (playerPawn.canReachEnd() and opponentPawn.canReachEnd()):
                playerPawn.removeWall(action)
                return randomMove(playerPawn, opponentPawn, "Wall")
            playerPawn.removeWall(action)


def randomMove(playerPawn, opponentPawn, actionType):
    if type == "Move":
        return random.choice(playerPawn.possibleMoves()).value
    action = random.choice(playerPawn.possibleWalls())
    playerPawn.placeWall(action)
    while playerPawn.canReachEnd() and opponentPawn.canReachEnd():
        playerPawn.removeWall(action)
        action = random.choice(playerPawn.possibleWalls())
    return action