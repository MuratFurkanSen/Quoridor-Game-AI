import matplotlib.pyplot as plt
from IPython import display

plt.ion()

def plot(player_scores, player_mean_scores, opponent_scores, opponent_mean_scores):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Training...')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(player_scores)
    plt.plot(opponent_scores)
    plt.plot(player_mean_scores)
    plt.plot(opponent_mean_scores)
    plt.ylim(ymin=0)
    plt.text(len(player_scores)-1, player_scores[-1], str(player_scores[-1]))
    plt.text(len(player_mean_scores)-1, player_mean_scores[-1], str(player_mean_scores[-1]))
    plt.show(block=False)
    plt.pause(.1)
