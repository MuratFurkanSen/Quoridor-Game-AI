from flask import Flask, request, jsonify
from Pawn import Pawn
from Logic import *
import torch

app = Flask(__name__)
AI = torch.load("Model.pth")

@app.route('/api', methods=['POST'])
def predict():
    data = request.get_json(force=True)

    maze = data['maze']
    playerPawn = data['playerPawn']  # X,Y
    opponentPawn = data['opponentPawn']  # X,Y
    walls = data['walls']  # Active Walls

    playerPawn = Pawn("Player", playerPawn[0], playerPawn[1], maze)
    opponentPawn = Pawn("Player", opponentPawn[0], opponentPawn[1], maze)
    state = get_state(playerPawn, opponentPawn, walls)
    action = get_action(AI, state)

    return jsonify(action)


if __name__ == '__main__':
    app.run(debug=True)
