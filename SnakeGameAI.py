import pygame
import random
from enum import Enum # enum is a class that represents data that is limited to a fixed set of values
from collections import namedtuple # namedtuple is a tuple subclass that allows us to refer to each value in the tuple by a name
import numpy as np # numpy is a library for scientific computing

pygame.init() # initialize all imported pygame modules
# font = pygame.font.Font('ChrustyRock-ORLA.ttf', 25)   # issue with this font for numbers 3-9
font = pygame.font.Font('arial_bold.ttf', 25) # font

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y') # namedtuple is a tuple subclass that allows us to refer to each value in the tuple by a name

BLOCK_SIZE = 20 # size of each block
SPEED = 50 # speed of the game

# RGB colors
WHITE = (255, 255, 255)
RED1 = (255, 0, 0)
RED2 = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)
GREEN1 = (0, 255, 0)
GREEN2 = (0, 200, 0)
GREY = (128, 128, 128)

class SnakeGameAI:
    def __init__(self, w = 640, h = 480): # w = width, h = height
        self.w = w # width
        self.h = h # height
        # init display
        self.display = pygame.display.set_mode((self.w, self.h)) # set display
        pygame.display.set_caption('Snake Game') # set caption
        self.clock = pygame.time.Clock() # create an object to help track time
        self.reset() # reset game state

    def reset(self):
        # init game state
        self.direction = Direction.RIGHT

        self.head = Point(self.w/2, self.h/2) # head of the snake
        self.snake = [self.head, Point(self.head.x - BLOCK_SIZE, self.head.y), Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)] # snake body

        self.score = 0 # score
        self.food = None # food
        self._place_food() # place food
        self.frame_iteration = 0 # frame iteration

    def _place_food(self): # place food
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE # random x coordinate
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE # random y coordinate
        self.food = Point(x, y) # food point
        if self.food in self.snake: # if food is in snake
            self._place_food() #    place food again

    def play_step(self, action): # play step
        self.frame_iteration += 1 # frame iteration
        # 1. collect user input
        for event in pygame.event.get(): # for each event
            if event.type == pygame.QUIT: # if event is quit
                pygame.quit()
                quit()

        # 2. move
        self._move(action) # update the head
        self.snake.insert(0, self.head) # insert the head to the snake

        # 3. check if game over
        reward = 0 # reward
        game_over = False
        if self.is_collision() or self.frame_iteration > 100 * len(self.snake): # if collision or frame iteration is greater than 100 * length of snake
            game_over = True # game over
            reward = -10 # reward
            return reward, game_over, self.score

        # 4. place new food or just move
        if self.head == self.food: # if head is at food
            self.score += 1 # score
            reward = 10 # reward
            self._place_food() # place food
        else:
            self.snake.pop() # remove the last element of the snake

        # 5. update ui and clock
        self.update_ui() # update ui
        self.clock.tick(SPEED) # tick the clock

        # 6. return game over and score
        return reward, game_over, self.score

    def is_collision(self, pt = None): # is collision
        if pt is None: # if point is none
            pt = self.head # point is head
        # hits boundary
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0: # if point is out of bounds
            return True
        # hits itself
        if pt in self.snake[1:]: # if point is in snake
            return True

        return False

    def update_ui(self):
        self.display.fill(BLACK) # fill display with black

        for pt in self.snake:
            pygame.draw.rect(self.display, GREEN1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE)) # draw a rectangle for Green1
            pygame.draw.rect(self.display, GREEN2, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12)) # draw a rectangle for Green2

        pygame.draw.rect(self.display, RED1, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE)) # draw a rectangle for Red1
        pygame.draw.rect(self.display, RED2, pygame.Rect(self.food.x + 4, self.food.y + 4, 12, 12)) # draw a rectangle for food for Red2

        text = font.render('Score: ' + str(self.score), True, WHITE) # render text
        self.display.blit(text, [0, 0]) # blit draws one image onto another | blit(source, dest, area = None, special_flags = 0) -> Rect
        pygame.display.flip()

    def _move(self, action): # move
        # [straight, right, left]

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP] # clockwise
        idx = clock_wise.index(self.direction) # index of direction

        if np.array_equal(action, [1, 0, 0]): # if action is [1, 0, 0]
            new_direction = clock_wise[idx] # no change
        elif np.array_equal(action, [0, 1, 0]): # if action is [0, 1, 0]
            next_idx = (idx + 1) % 4 # next index
            new_direction = clock_wise[next_idx] # right turn r -> d -> l -> u
        else: # [0, 0, 1]
            next_idx = (idx - 1) % 4 # next index
            new_direction = clock_wise[next_idx] # left turn r -> u -> l -> d

        self.direction = new_direction

        x = self.head.x
        y = self.head.y

        if self.direction == Direction.RIGHT: # if direction is right
            x += BLOCK_SIZE # move right
        elif self.direction == Direction.LEFT: # if direction is left
            x -= BLOCK_SIZE # move left
        elif self.direction == Direction.UP: # if direction is up
            y -= BLOCK_SIZE # move up
        elif self.direction == Direction.DOWN: # if direction is down
            y += BLOCK_SIZE # move down

        self.head = Point(x, y) # head is Point(x, y)