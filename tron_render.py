#!/usr/bin/env python
import pygame
import sys
import networking as n 
import tron
import socket

FPS = pygame.time.Clock()
# self.player1 = LightBike([0,0], [1,0], (255,0,0))
# player2 = LightBike([40,40], [1,0], (0,255,0))


# GRID_SIZEX = 100 # will probably need to be rectangular
# GRID_SIZEY = 100

grid_map_x = {1:0,4:0,7:0,2:1,5:1,8:1,3:2,6:2,9:2}
grid_map_y = {1:0,2:0,3:0,4:1,5:1,6:1,7:2,8:2,9:2}

# # change all of this to a game class
if __name__ == '__main__':
  # game = Game.Game() # initilize game and pygame
  # middleware = n.MiddleWare(game)
  # find which ip address to host on
  myhostname = socket.gethostname()
#  (_,xindx,yindx) = myhostname.split('-')
  val = int(myhostname[2:])
  xindx = grid_map_x[val]
  yindx = grid_map_y[val]
  xindx = int(xindx)
  yindx = int(yindx)
  print yindx
  print xindx
  first_hit = True
  for line in open('/etc/hosts').readlines():
    if myhostname in line:
      my_ip_address = line.split()[0]
      break

  if yindx == 2:
    yindx = 0
  elif yindx == 0:
    yindx = 2
  game = tron.Game([xindx, yindx])
  print my_ip_address
  server = n.Server(my_ip_address, 20000, game )
  server.open_connection()
  while True:
    server.recev_connection()

