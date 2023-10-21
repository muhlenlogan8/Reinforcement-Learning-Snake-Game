import matplotlib.pyplot as plt # for plotting
from IPython import display # for live plot

plt.ion() # turn on interactive mode

def plot(scores, mean_scores): # plot scores and mean scores
    display.clear_output(wait=True) # clear output
    display.display(plt.gcf()) # display
    plt.clf() # clear plot
    plt.title('Training...') # title
    plt.xlabel('Number of Games') # x label
    plt.ylabel('Score') # y label
    plt.plot(scores) # plot scores
    plt.plot(mean_scores) # plot mean scores
    plt.ylim(ymin=0) # set y min
    plt.text(len(scores)-1, scores[-1], str(scores[-1])) # set text
    plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1])) # set text
    plt.show(block=False) # show plot
    plt.pause(.1) # pause plot