import pygame
import random
from enum import Enum # an enumeration is a set of symbolic names (members) bound to unique, constant values
from collections import namedtuple # namedtuple is a tuple subclass that allows us to refer to each value in the tuple by a name

pygame.init() # initialize all imported pygame modules
# font = pygame.font.Font('ChrustyRock-ORLA.ttf', 25)   # issue with this font for numbers 3-9
font = pygame.font.Font('arial_bold.ttf', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y') # namedtuple is a tuple subclass that allows us to refer to each value in the tuple by a name

BLOCK_SIZE = 20 # size of each block
SPEED = 15 # speed of the game

# RGB colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)
GREEN1 = (0, 255, 0)
GREEN2 = (0, 200, 0)

class SnakeGame:
    def __init__(self, w = 640, h = 480): # w = width, h = height
        self.w = w # width
        self.h = h # height
        # init display
        self.display = pygame.display.set_mode((self.w, self.h)) # set display
        pygame.display.set_caption('Snake Game') # set caption
        self.clock = pygame.time.Clock() # create an object to help track time

        # init game state
        self.direction = Direction.RIGHT

        self.head = Point(self.w/2, self.h/2) # head of the snake
        self.snake = [self.head, Point(self.head.x - BLOCK_SIZE, self.head.y), Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)] # snake body

        self.score = 0 # score
        self.food = None # food
        self._place_food() # place food

    def _place_food(self): # place food
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE # random x coordinate
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE # random y coordinate
        self.food = Point(x, y) # food point
        if self.food in self.snake: # if food is in snake
            self._place_food() ## place food again

    def play_step(self): # play step
        # 1. collect user input
        for event in pygame.event.get(): # for each event
            if event.type == pygame.QUIT: # if event is quit
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN: # if event is key down
                if event.key == pygame.K_LEFT: # if key is left
                    self.direction = Direction.LEFT # direction is left
                elif event.key == pygame.K_RIGHT: # if key is right
                    self.direction = Direction.RIGHT # direction is right
                elif event.key == pygame.K_UP: # if key is up
                    self.direction = Direction.UP # direction is up
                elif event.key == pygame.K_DOWN: # if key is down
                    self.direction = Direction.DOWN # direction is down

        # 2. move
        self._move(self.direction) # update the head
        self.snake.insert(0, self.head) # insert the head at the beginning of the snake

        # 3. check if game over
        game_over = False
        if self._is_collision(): # if collision
            game_over = True
            return game_over, self.score

        # 4. place new food or just move
        if self.head == self.food: # if head is at food
            self.score += 1
            self._place_food() # place food
        else:
            self.snake.pop() # remove the last element of the snake

        # 5. update ui and clock
        self.update_ui()
        self.clock.tick(SPEED)

        # 6. return game over and score
        return game_over, self.score

    def _is_collision(self):
        # hits boundary
        if self.head.x > self.w - BLOCK_SIZE or self.head.x < 0 or self.head.y > self.h - BLOCK_SIZE or self.head.y < 0:
            return True
        # hits itself
        if self.head in self.snake[1:]:
            return True

        return False

    def update_ui(self):
        self.display.fill(BLACK) # fill display with black

        for pt in self.snake: # for each point in the snake
            pygame.draw.rect(self.display, GREEN1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE)) # draw a rectangle for snake inner | Rect(left, top, width, height)
            pygame.draw.rect(self.display, GREEN2, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12)) # draw a rectangle for snake outer | Rect(left, top, width, height)

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE)) # draw a rectangle for food inner | Rect(left, top, width, height)

        text = font.render('Score: ' + str(self.score), True, WHITE) # render text
        self.display.blit(text, [0, 0]) # draw text on display
        pygame.display.flip() # update the full display surface to the screen

    def _move(self, direction):
        x = self.head.x
        y = self.head.y

        if direction == Direction.RIGHT: # if direction is right
            x += BLOCK_SIZE # move right
        elif direction == Direction.LEFT: # if direction is left
            x -= BLOCK_SIZE # move left
        elif direction == Direction.UP: # if direction is up
            y -= BLOCK_SIZE # move up
        elif direction == Direction.DOWN: # if direction is down
            y += BLOCK_SIZE # move down

        self.head = Point(x, y)

        self.head = Point(x, y)

if __name__ == '__main__': # if this file is run directly
    game = SnakeGame() # create a game object

    # game loop
    while True:
        game_over, score = game.play_step()

        if game_over == True:
            break

    print('Final Score:', score) # print final score

    pygame.quit()