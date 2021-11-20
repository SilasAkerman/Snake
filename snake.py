import pygame
import numpy
import time
import random

from pygame import mixer

# This is going to be tricky. Inspired by snake-game from my TI-84 calculator
# Let's have one 2D array of the board containing information for each square
# The snake is represented by the path the snake took, or the direction
# The head of the snake takes the current (or set) direction and walks that way
# The tail of the snake follows the direction and removes the data (set to None)

# Directions are "left", "right", "up", "down"
# Apples are represented with the word "apple" and maybe drawn with a sprite
# When we draw the window, only draw where there is data
# Maybe some sprite for the apple, but the snake should be green

# When the snake eats an apple, the data is replaced with the direction
# and the tail skips for one turn, simulating the extension of the end of the snake

# If the snake ever walks onto a square with a "direction" (ignores None and "apple"),
# then the game is over. Maybe grey out the snake.
# Display game over and the length of the snake (or the count of "direction" squares)


class Snake():
     def __init__(self, startRow, startCol, startDirection, wrapMode):
          # A new plan for tail and head movement, the tail first moves by reading the data, removing it
          # while the head does this afterwards by moving and then writing the data
          # For convinience, the head of the snake will write the data "active"
          self.headCoords = [startRow, startCol]
          self.tailCoords = self.headCoords 
          self.setDirection(startDirection)
          self.wrapMode = wrapMode

          self.growth = True # For the current plan to work, the tail needs to wait for one turn
          self.length = 2 # The head will expand the tail for one turn, so the snake will start at this
          self.living = True


     def move(self, game):
          self.tailMove(game)
          self.headMove(game)
          if self.growth: # If we ate something
               game.appleEaten()
     
     def tailMove(self, game):
          if self.growth:
               self.growth = False
          else:
               currentDirection = game.board[self.tailCoords[0], self.tailCoords[1]]
               nextSquareCoords = self.getNextSquare(currentDirection, self.tailCoords, game.square_dim)
               # Now delete the data on this square and move on to the next
               game.board[self.tailCoords[0], self.tailCoords[1]] = None
               self.tailCoords = nextSquareCoords

     def headMove(self, game):
          # This needs to account for out of bounds. In this case, kill the snake
          nextSquareCoords = self.getNextSquare(self.direction, self.headCoords, game.square_dim)
          if nextSquareCoords[0] >= game.square_dim or nextSquareCoords[0] < 0 or nextSquareCoords[1] >= game.square_dim or nextSquareCoords[1] < 0:
               # This means that the snake died, don't move and kill the snake
               self.living = False
          elif game.isDirection(nextSquareCoords[0], nextSquareCoords[1]):
               # This also kills the snake
               self.living = False
          else:
               # The spot is safe! Write the data
               game.board[self.headCoords[0], self.headCoords[1]] = self.direction
               if game.board[nextSquareCoords[0], nextSquareCoords[1]] == "apple":
                    self.growth = True
                    self.length += 1
               # Now move the head and write "active"
               self.headCoords = nextSquareCoords
               game.board[self.headCoords[0], self.headCoords[1]] = "active"
               

     def getNextSquare(self, direction, coordinates, dim_size):
          # Will return the coordinates of the next square
          if direction == "left":
               coords = [coordinates[0]-1, coordinates[1]]
          if direction == "right":
               coords = [coordinates[0]+1, coordinates[1]]
          if direction == "up":
               coords = [coordinates[0], coordinates[1]-1]
          if direction == "down":
               coords = [coordinates[0], coordinates[1]+1]
          
          # Now do a different check if the wrapMode is true
          if self.wrapMode:
               if coords[0] < 0:
                    coords[0] = dim_size - 1
               if coords[0] >= dim_size:
                    coords[0] = 0
               if coords[1] < 0:
                    coords[1] = dim_size - 1
               if coords[1] >= dim_size:
                    coords[1] = 0
          
          return coords

     def setDirection(self, direction, sound=False):
          self.direction = direction
          if sound:
               sound.play()

     def drawPixel(self, game, row, col):
          pixelRect = self.getPixelRect(game, row, col) # Also comes with coordinates
          if self.living: # If the snake is alive, draw it green. Else, draw it grey
               pygame.draw.rect(game.screen, (0, 255, 0), pixelRect)
          else:
               pygame.draw.rect(game.screen, (100, 120, 100), pixelRect)
     

     def getPixelRect(self, game, row, col):
          # Also defines coordinates
          return pygame.Rect(row*game.square_size, col*game.square_size, game.square_size, game.square_size)

class Apple():
     def __init__(self, startRow, startCol):
          #self.image = some image or sprite
          # Until I get a sprite, let's just have a smaller rectangel
          # self.squareSize = 40
          self.row = startRow
          self.col = startCol


     def create(self, game):
          # Plan is to create a list of empty spots and then randomly pick one
          emptyCoords = []
          for row in range(game.square_dim):
               for col in range(game.square_dim):
                    if game.board[row, col] is None:
                         emptyCoords.append((row, col))
          choice = random.choice(emptyCoords)
          self.row = choice[0]
          self.col = choice[1]
          game.board[self.row, self.col] = "apple"

     def getRect(self, game, row, col):
          rowCoordinate = row*game.square_size
          colCoordinate = col*game.square_size
          return pygame.Rect(rowCoordinate, colCoordinate, game.square_size, game.square_size)

     def draw(self, game):
          appleRect = self.getRect(game, self.row, self.col)
          if game.snake.living: # If the snake is alive, draw it red. Else, draw it grey
               pygame.draw.rect(game.screen, (255, 0, 0), appleRect)
          else:
               pygame.draw.rect(game.screen, (120, 100, 100), appleRect)



class Game():
     def __init__(self, square_dim, updateSpeed, wrapMode):
          pygame.init()
          self.screen = pygame.display.set_mode((800, 800))

          self.square_dim = square_dim
          self.square_size = pygame.display.get_window_size()[1] // square_dim # Width and height of each square
          self.updateSpeed = updateSpeed
          self.wrapMode = wrapMode

          self.gameOverFont = pygame.font.Font("freesansbold.ttf", 64)
          self.scoreFont = pygame.font.Font("freesansbold.ttf", 32)
          self.infoFont = pygame.font.Font("freesansbold.ttf", 16)

          self.deathSound = mixer.Sound("Silas Projects/Games/Snake/Death.wav")
          self.eatSound = mixer.Sound("Silas Projects/Games/Snake/Eat.wav")
          self.directionSound = mixer.Sound("Silas Projects/Games/Snake/Direction.wav")

          self.initGame()


     def initGame(self):
          self.board = numpy.array([[None for _ in range(self.square_dim)] for _ in range(self.square_dim)])

          self.snake = Snake(self.square_dim//4, self.square_dim//2, "right", self.wrapMode)
          self.board[self.square_dim//4, self.square_dim//2] = "right"

          self.apple = Apple(self.square_dim//4 * 3, self.square_dim//2)
          self.board[self.square_dim//4 * 3, self.square_dim//2] = "apple"


     def isDirection(self, row, col):
          # The head of the snake will wait for the command, but still register as valid data
          directions = {"left", "right", "up", "down", "active"} # This is a set
          return self.board[row, col] in directions

     def drawBoard(self):
          self.screen.fill((0, 0, 0))
          for row in range(self.square_dim):
               for col in range(self.square_dim):
                    if self.isDirection(row, col):
                         self.snake.drawPixel(self, row, col)
                    if self.board[row, col] == "apple":
                         self.apple.draw(self)
          
          pygame.display.update()
     
     def appleEaten(self):
          self.eatSound.play()
          self.apple.create(self)

     def gameOver(self):
          self.deathSound.play()
          gameOver_text = self.gameOverFont.render("Game Over", True, (255, 0, 0))
          score_text = self.scoreFont.render("Score: " + str(self.snake.length-2), True, (255, 255, 255))
          info_text = self.infoFont.render("Press P to play again or BACKSPACE to quit", True, (255, 255, 255))

          self.screen.blit(gameOver_text, (pygame.display.get_window_size()[0]//4 - 50, pygame.display.get_window_size()[1]//2 - 100))
          self.screen.blit(score_text, (pygame.display.get_window_size()[0]//4 - 50, pygame.display.get_window_size()[1]//2 + 100))
          self.screen.blit(info_text, (pygame.display.get_window_size()[0]//4 - 100, pygame.display.get_window_size()[1] - 100))
          pygame.display.update()

          # Now loop through the inputs until the player either quits or presses enter to play again
          game_running = True
          while game_running:
               for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                         game_running = False
                    if event.type == pygame.KEYDOWN:
                         if event.key == pygame.K_p:
                              game_running = False
                              self.initGame()
                              self.play()
                         if event.key == pygame.K_BACKSPACE:
                              game_running = False



     def play(self):
          game_running = True

          while game_running:
               inputAcquired = False # This is so that the player can't accedentily put in two inputs and walk into the snake by going backwards

               for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                         game_running = False
                    
                    if event.type == pygame.KEYDOWN and not inputAcquired:
                         inputAcquired = True
                         if event.key == pygame.K_UP:
                              self.snake.setDirection("up", self.directionSound)
                         if event.key == pygame.K_DOWN:
                              self.snake.setDirection("down", self.directionSound)
                         if event.key == pygame.K_RIGHT:
                              self.snake.setDirection("right", self.directionSound)
                         if event.key == pygame.K_LEFT:
                              self.snake.setDirection("left", self.directionSound)
               
               self.snake.move(self)
               self.drawBoard()
               time.sleep(self.updateSpeed)

               if not self.snake.living:
                    game_running = False

          self.gameOver()


if __name__ == "__main__":
     snake = Game(15, 0.1, True)
     snake.play()