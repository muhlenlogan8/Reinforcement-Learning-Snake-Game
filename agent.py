import torch
import random
import numpy as np
from collections import deque # deque is a list-like container with fast appends and pops on either end
from SnakeGameAI import SnakeGameAI, Direction, Point, BLOCK_SIZE # SnakeGameAI is a class, Direction is an enum, Point is a namedtuple, BLOCK_SIZE is a constant
from model import Linear_QNet, QTrainer # Linear_QNet is a class, QTrainer is a class
from helper import plot # plot is a function

MAX_MEMORY = 100_000 # number of samples to store in memory
BATCH_SIZE = 1000 # number of samples to train on
LR = 0.001 # learning rate

class Agent:
    def __init__(self):
        self.n_games = 0 # number of games
        self.epsilon = 0 # randomness
        self.gamma = 0.9 # discount rate | 0.9 is good for games like snake | must be smaller than 1
        self.memory = deque(maxlen = MAX_MEMORY) # popleft() if maxlen is exceeded
        self.model = Linear_QNet(11, 256, 3) # input size, hidden size, output size | 11 states, 256 hidden nodes, 3 actions | hidden size can change but input size and output size cannot due to the snake game and how it is set up
        self.trainer = QTrainer(self.model, lr = LR, gamma = self.gamma) # model, learning rate, discount rate

    # all states stored here | 11 states total which is important for the neural network first layer
    def get_state(self, game):
        head = game.snake[0] # head of snake
        point_l = Point(head.x - BLOCK_SIZE, head.y) # point left
        point_r = Point(head.x + BLOCK_SIZE, head.y) # point right
        point_u = Point(head.x, head.y - BLOCK_SIZE) # point up
        point_d = Point(head.x, head.y + BLOCK_SIZE) # point down

        dir_l = game.direction == Direction.LEFT # direction is left
        dir_r = game.direction == Direction.RIGHT # direction is right
        dir_u = game.direction == Direction.UP # direction is up
        dir_d = game.direction == Direction.DOWN # direction is down

        state = [
            # Danger straight
            (dir_r and game.is_collision(point_r)) or # if direction is right and collision is true
            (dir_l and game.is_collision(point_l)) or # if direction is left and collision is true
            (dir_u and game.is_collision(point_u)) or # if direction is up and collision is true
            (dir_d and game.is_collision(point_d)), # if direction is down and collision is true

            # Danger right
            (dir_u and game.is_collision(point_r)) or # if direction is up and collision is true
            (dir_d and game.is_collision(point_l)) or # if direction is down and collision is true
            (dir_l and game.is_collision(point_u)) or # if direction is left and collision is true
            (dir_r and game.is_collision(point_d)), # if direction is right and collision is true

            # Danger left
            (dir_d and game.is_collision(point_r)) or # if direction is down and collision is true
            (dir_u and game.is_collision(point_l)) or # if direction is up and collision is true
            (dir_r and game.is_collision(point_u)) or # if direction is right and collision is true
            (dir_l and game.is_collision(point_d)), # if direction is left and collision is true

            # Move direction
            dir_l, 
            dir_r,
            dir_u,
            dir_d,

            # Food location
            game.food.x < game.head.x, # food left
            game.food.x > game.head.x, # food right
            game.food.y < game.head.y, # food up
            game.food.y > game.head.y # food down
        ]

        return np.array(state, dtype = int) # convert to numpy array and int so True -> 1, False -> 0

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft() if MAX_MEMORY is reached

    def train_long_memory(self): # train neural network with batches
        if len(self.memory) > BATCH_SIZE: # if memory is greater than batch size
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory # list of tuples
        
        states, actions, rewards, next_states, dones = zip(*mini_sample) # returns a zip object, which is an iterator of tuples where the first item in each passed iterator is paired together, and then the second item in each passed iterator are paired together etc.
        self.trainer.train_step(states, actions, rewards, next_states, dones) # train step
        # other way of doing above
        # for state, action, reward, next_state, done in mini_sample:
        #     self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done): # train neural network with single sample
        self.trainer.train_step(state, action, reward, next_state, done) # train step

    def get_action(self, state): # get action from model using epsilon-greedy algorithm
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.n_games # epsilon decays as n_games increases
        final_move = [0, 0, 0] # [straight, right, left]
        if random.randint(0, 200) < self.epsilon: # if random number is less than epsilon
            move = random.randint(0, 2) # move is random number between 0 and 2
            final_move[move] = 1 # set index to 1
        else: # get action from Q-network
            state0 = torch.tensor(state, dtype = torch.float) # convert to tensor
            prediction = self.model(state0) # get prediction from model
            move = torch.argmax(prediction).item() # get index of greatest value | e.g. [5.0, 2.7, 0.1] -> max -> [1,0,0] | .item() gets the value of the tensor (converts to one number)
            final_move[move] = 1 # set index to 1

        return final_move

def train():
    plot_scores = [] # list of scores
    plot_mean_scores = [] # list of mean scores
    total_score = 0 # total score
    record = 0 # record score
    agent = Agent() # agent
    game = SnakeGameAI() # game
    while True: 
        # get old state
        state_old = agent.get_state(game)

        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # train long memory, plot result
            game.reset()
            agent.n_games += 1 # increment number of games
            agent.train_long_memory()  # train long memory

            if score > record: # if score is greater than record
                record = score # record is score
                agent.model.save() # save model
            print('Game:', agent.n_games, 'Score:', score, 'Record:', record) # print game, score, and record

            # plot
            plot_scores.append(score) # append score to list of scores
            total_score += score # add score to total score
            mean_score = total_score / agent.n_games # mean score
            plot_mean_scores.append(mean_score) # append mean score to list of mean scores
            plot(plot_scores, plot_mean_scores) # plot scores and mean scores

if __name__ == '__main__':
    train() # train