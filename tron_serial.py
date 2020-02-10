import pygame, sys
from pygame.locals import *
loc = [] 
FPS = pygame.time.Clock()

#GRID_SIZEX = 1920/10 # will probably need to be rectangular
#GRID_SIZEY = 1080/10
GRID_SIZEX = 1280/10
GRID_SIZEY = 1024/10

class LightBike():
  def __init__(self, startloc, startvel, color):
    self.location = startloc
    self.velocity = startvel
    self.color = color
  def movedown(self):
    self.velocity[0] = 0
    self.velocity[1] = 1
  def moveup(self):
    self.velocity[0] = 0
    self.velocity[1] = -1
  def moveleft(self):
    self.velocity[0] = -1
    self.velocity[1] = 0
  def moveright(self):
    self.velocity[0] = 1
    self.velocity[1] = 0
  def update(self):
    self.location[0] += self.velocity[0]
    self.location[1] += self.velocity[1]


def loc_collision(loc, bike):
  # check the location array to see if colided.
  if bike.location[0] < 0 or bike.location[0] > GRID_SIZEX:
    return True
  if bike.location[1] < 0 or bike.location[1] > GRID_SIZEY:
    return True
  if loc[bike.location[0]][bike.location[1]] == 1:
    # something was drawn there you hit!!
    return True
  else:
    return False

if __name__ == '__main__':
  # intial game set up. 
  # loc will be local to each node
  for x in range(0,GRID_SIZEX + 1):
    loc.append([])
    for y in range(0,GRID_SIZEY + 1):
      loc[x].append(0) # 0 means not moved there yet

  SCALE = 10
  WIDTH = len(loc) * SCALE
  HEIGHT = len(loc[0]) * SCALE
  SIZE = (WIDTH, HEIGHT) # width of screen
  SPEED = 1 # amount to move in location grid ie
  velocity = [1,0] # start moving right
  current_loc = [0,0]

  player1 = LightBike([0,0], [1,0], (255,0,0))
  player2 = LightBike([40,40], [1,0], (0,255,0))

  # Display stuff Should be segmented later
  pygame.init() 
  window = pygame.display.set_mode(SIZE)

  # start with just a square


  # MAKE THIS OO!!!! 
  while True:

    # control block This will be the master node
    for event in pygame.event.get():
          if event.type == pygame.QUIT:
              sys.exit()
          if event.type == KEYDOWN:
              if event.key == K_LEFT:
                player1.moveleft()
              if event.key == K_RIGHT:
                player1.moveright()
              if event.key == K_UP:
                player1.moveup()
              if event.key == K_DOWN:
                player1.movedown()
              if event.key == K_a:
                player2.moveleft()
              if  event.key == K_d:
                player2.moveright()
              if event.key == K_w:
                player2.moveup()
              if event.key == K_s:
                player2.movedown()

    # update will only be called if there are players one your screen
    player1.update()
    player2.update()
    if loc_collision(loc, player1):
      # will have to send to master node that there is a winner!
      print 'PLAYER 2 WINS'
      sys.exit()
    if loc_collision(loc, player2):
      print 'PLAYER 1 WINS'
      sys.exit()

    loc[player1.location[0]][player1.location[1]] = 1
    loc[player2.location[0]][player2.location[1]] = 1

    pygame.draw.rect(window, player1.color, (player1.location[0]*SCALE, player1.location[1]*SCALE, SCALE, SCALE))
    pygame.draw.rect(window, player2.color, (player2.location[0]*SCALE, player2.location[1]*SCALE, SCALE, SCALE))
    pygame.display.flip()
    FPS.tick(20)


