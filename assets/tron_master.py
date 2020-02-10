# tron master node
import pygame
from pygame.locals import *
import socket, struct, threading, sys
import cPickle, time
from pprint import pprint
from helper import draw_logic, load_images, construct_list


MONITOR_GRIDX = 5 # width 
MONITOR_GRIDY = 3 # height
FULL_GRID_SIZE = (165, 63) # number of locations in full game 
WORKER_NODE_SIZE = (33,21)
PLAYER1_START = [0, FULL_GRID_SIZE[1]/2]
PLAYER2_START = [FULL_GRID_SIZE[0]-1, FULL_GRID_SIZE[1]/2]
SOCKET_DEL = '*ET*'
WIN_PAUSE = 3 # seconds
SPEED = 1
FPS = pygame.time.Clock()
NUM_OF_LEVELS = 7
LEVEL_INC = .5
LEVEL_MINUTES = []
last = 0 
for x in range(0, NUM_OF_LEVELS+1):
  LEVEL_MINUTES.append(last)
  last += LEVEL_INC
LEVEL_TIMES = [x*1000*60 for x in LEVEL_MINUTES]
LEVEL_SPEED = [x*15 for x in range(1,NUM_OF_LEVELS+2)]
LEVEL_TUPLES = zip(LEVEL_TIMES, LEVEL_SPEED)
LEVELS = dict(zip([x for x in range(1, NUM_OF_LEVELS+2)], LEVEL_TUPLES))
END_TIME = LEVEL_TIMES[-1] * 60 * 1000 # minutes x seconds x miliseconds 

class LightBike():
  def __init__(self, startloc, start_orient, startvel, start_dir):
    self.location = startloc[:]
    self.velocity = startvel[:]
    self.orientation = start_orient
    self.score = 0
    self.dir = start_dir

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

class MasterTron(object):
  """The class for the MasterTron node"""
  def __init__(self):
    pygame.init()
    self.player1 = LightBike(PLAYER1_START, 'hor', [1,0], 'left' )
    self.player2 = LightBike(PLAYER2_START, 'hor', [-1,0], 'right' )
    self.new_game_score()
    self.init_locations()
    self.window = pygame.display.set_mode((20,20))
    self.image_dict = load_images()
    self.sock_list = [[ [] for y in range(MONITOR_GRIDY)] for x in range(MONITOR_GRIDX)]
    ips = open('ip_list.txt', 'r')
    ips.readline() #comment line
    address = ips.readline().strip()
    ip_list = []
    while address:
        ip_list.append(address)
        address = ips.readline().strip()
    idx = 0
    for x in range(0, MONITOR_GRIDX):
      for y in range(0, MONITOR_GRIDY):
        self.sock_list[x][y] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_list[x][y].connect((ip_list[idx], 20000))
        idx += 1

    # self.ip_list = [('localhost', 20000), ('localhost', 20001)]#, ('localhost', 20001)]
    self.fliped_1x, self.fliped_1y, self.fliped_2x, self.fliped_2y = 4*[False]
    self.flip_1x, self.flip_1y, self.flip_2x, self.flip_2y = 4*[False]
    self.el_time = 0
    self.current_level = 1
    # pygame.mixer.init()
    # pygame.mixer.music.set_volume(1.0)
    # pygame.mixer.music.load("assets/backtrack.wav")
    # pygame.mixer.music.play()
    # self.explode = pygame.mixer.Sound('assets/explode.wav')
    # self.backtrack = pygame.mixer.Sound('assets/backtrack.mp3')
    # self.backtrack.play(-1)


  def run(self):
    """loop to run the game and decide which state the game is in and call the 
    functions accordingly""" 
    data = ''
    while True:
      if self.state == 'play':
        data, self.state = self.play_frame()
      elif self.state == 'win':
        # need to send win signal, reset locations and pause 
        self.win_signal(data)
      elif self.state == 'draw':
        self.win_signal(data)
      elif self.state == 'over':
        self.game_over_signal(data)
      self.el_time += FPS.tick(LEVELS[self.current_level][1])
      # print self.el_time
      # print LEVELS[self.current_level][0]
      if self.el_time > LEVELS[self.current_level][0]:
        if self.current_level == len(LEVELS):
          print "exiting at " + str(self.el_time)
          print "current level is " + str(self.current_level)
          self.state = 'over'
        self.current_level += 1

  def play_frame(self):
    events = pygame.event.get()
    self.handle_key_press(events)
    self.handle_joy_stick(events)
    self.last_2_loc_1 = self.last_loc_1[:]
    self.last_loc_1[0] = [self.player1.location[0], self.player1.location[1]]
    self.last_2_loc_2 = self.last_loc_2[:]
    self.last_loc_2[0] = [self.player2.location[0], self.player2.location[1]]
    self.player1.update()
    self.player2.update()
    player1_image_dict = draw_logic(self.last_2_loc_1, self.last_loc_1, self.player1,
                                    self.fliped_1x, self.fliped_1y, 'c')
    player2_image_dict = draw_logic(self.last_2_loc_2, self.last_loc_2, self.player2, 
                                    self.fliped_2x, self.fliped_2y, 'm')
    self.fliped_1x, self.fliped_1y = self.adjust_periodic(self.player1)
    self.fliped_2x, self.fliped_2y = self.adjust_periodic(self.player2)
    # flip_1x, flip_1y = self.adjust_periodic(self.player1)
    # flip_2x, flip_2y = self.adjust_periodic(self.player2)
    # if loc_collision(self.player1):
    #   close_sockets(sock_list)
    # if loc_collision(self.player2):
    #   close_sockets(sock_list)

    self.location[self.player1.location[0]][self.player1.location[1]] = 1
    self.location[self.player2.location[0]][self.player2.location[1]] = 1
    send_struct = {'player1_images': player1_image_dict,
                'player2_images':player2_image_dict,
                'player1_locs':[self.player1.location, self.last_loc_1[0], self.last_2_loc_1[0]],
                'player2_locs':[self.player2.location, self.last_loc_2[0], self.last_2_loc_2[0]],
                'state': 'play'}

    data = cPickle.dumps(send_struct, cPickle.HIGHEST_PROTOCOL) + '*ET*'
    for x in range(0, len(self.sock_list)):
      for y in range(0, len(self.sock_list[x])):
        self.sock_list[x][y].sendall(data)
    return_list = []

    for x in range(0, len(self.sock_list)):
      for y in range(0, len(self.sock_list[x])):
        return_list.append(self.get_whole_packet(self.sock_list[x][y]))

    num_of_wins = 0
    win_states = []
    for data in return_list:
      if data['state'] != 'play':
        if data['state'] == 'draw':
          # draw happend on the same screen
          print 'drew'
          return data, 'draw'
        if data['state'] == 'win':
          num_of_wins += 1
          win_states.append(data)
          # return (data, 'win')
    if num_of_wins > 1:
      pprint(return_list)
      print "NUM OF WINS IS LARGER THAN 1"
      return win_states, 'draw'
    elif num_of_wins == 1:
      return (win_states[0], 'win')


    if self.el_time > END_TIME:
      return (data, 'over')

    # return the state of the game
    return (data, 'play')

  def adjust_periodic(self, player):
    """Allows for periodic edges. Returns whether or not you need to flip the 
    corner piece."""
    flipx = False
    flipy = False
    if player.location[0] >= FULL_GRID_SIZE[0]:
      player.location[0] = 0
      flipx = True
    elif player.location[0] < 0: 
      player.location[0] = FULL_GRID_SIZE[0] - 1
      flipx = True
    if player.location[1] >= FULL_GRID_SIZE[1]:
      player.location[1] = 0
      flipy = True
    elif player.location[1] < 0: 
      player.location[1] = FULL_GRID_SIZE[1] - 1
      flipy = True
    return flipx, flipy

  def win_signal(self, data):
    """players scored, increment the score and send the win signal to all the nodes
    """
    explod_loc_list = []
    if isinstance(data, dict):
      # not a draw, check who won then.
      if data['which'] == 1:
        self.player1.score += 1
      else:
        self.player2.score += 1

      for loc in data['death_loc']:
        # print "BEFORE CONVERTING" + str(loc)
        explod_loc_list.append(self.convert_to_global(data['tile'],loc))
        # print "AFTER CONVERTING" + str(self.convert_to_global(data['tile'],loc))

    else:
      # it's a list of states so there was a draw
      print 'draw'
      for x in data:
        for loc in x['death_loc']:
          explod_loc_list.append(self.convert_to_global(x['tile'],loc))
    send_struct = {'state': 'win', 'death_loc':explod_loc_list,
                   'score':{'p1':self.player1.score, 'p2':self.player2.score}}
    #send to worker nodes
    data = cPickle.dumps(send_struct, cPickle.HIGHEST_PROTOCOL) + SOCKET_DEL                                       
    for x in range(0, len(self.sock_list)):
      for y in range(0, len(self.sock_list[x])):
        self.sock_list[x][y].sendall(data)

    # self.explode.play()

    self.init_locations()
    self.update_score_file()
    time.sleep(WIN_PAUSE)
    for x in range(0, len(self.sock_list)):
      for y in range(0, len(self.sock_list[x])):
        self.get_whole_packet(self.sock_list[x][y])
    pygame.event.clear()

  def game_over_signal(self, data):
    send_struct = {'state': 'over','score':{'p1':self.player1.score, 
                                            'p2':self.player2.score}}
    # data = cPickle.dumps(send_struct, cPickle.HIGHEST_PROTOCOL) + SOCKET_DEL                                       
    self.handshake(send_struct)
    reset = False
    self.update_score_file()

    # wait for rest key. TODO, add a kill key
    while not reset:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == KEYDOWN:
          if event.key == K_4:
            reset = True
    self.init_locations()
    self.player1.score = 0
    self.player2.score = 0
    self.new_game_score()
    for x in range(0, len(self.sock_list)):
      for y in range(0, len(self.sock_list[x])):
        self.sock_list[x][y].sendall('go' + SOCKET_DEL)

    for x in range(0, len(self.sock_list)):
      for y in range(0, len(self.sock_list[x])):
        self.get_whole_packet(self.sock_list[x][y])
    self.el_time = 0
    self.current_level = 1
    # reset the tick clock as fast as possible
    FPS.tick(3000000)
    # should be synced up for another game

  def new_game_score(self):
    """appends the new players to the end of the score file"""
    score_file = open('scores.txt', 'a')
    last_line = 'player1 = 0 player2 = 0\n'
    score_file.write(last_line)
    score_file.close()

  def update_score_file(self):
    """overwrites the last line of the score file with the changed scores"""
    score_file = open('scores.txt', 'rw+')
    last_line = score_file.readlines()[-1]
    # score_file.write(' '*len(last_line))
    score_file.seek(-len(last_line), 2)
    last_line = 'player1 = ' + str(self.player1.score) + ' player2 = ' + str(self.player2.score) + '\n'
    score_file.write(last_line)
    score_file.close()

  def handshake(self, data):
    """Passes data to the nodes then waits for there response to keep synchronization.
    The data is first pickled as a string then sent"""
    data = cPickle.dumps(data, cPickle.HIGHEST_PROTOCOL) + SOCKET_DEL   
    for x in range(0, len(self.sock_list)):
      for y in range(0, len(self.sock_list[x])):
        self.sock_list[x][y].sendall(data)

    return_list = []
    for x in range(0, len(self.sock_list)):
      for y in range(0, len(self.sock_list[x])):
        return_list.append(self.get_whole_packet(self.sock_list[x][y]))
    return return_list

  def handle_joy_stick(self, events):
    """handles the pygame keyboard events."""
    # bug that you can go back on yourself if you register a lot of button presses
    p1_moved = False
    p2_moved = False
    for event in events:
      if event.type == pygame.QUIT:
          sys.exit()
      if event.type == KEYDOWN:
        # check if trying to go back on themselves
        if event.key == K_KP4 and self.player1.dir != 'left' and not p1_moved:
          if self.player1.dir != 'right':
            self.player1.moveleft()
            self.dir = 'left'
            p1_moved = True
        if event.key == K_KP6 and self.player1.dir != 'right' and not p1_moved:
          if self.player1.dir != 'left':
            self.player1.moveright()
            self.player1.dir = 'right'
            p1_moved = True
        if event.key == K_KP8 and self.player1.dir != 'up' and not p1_moved:
          if self.player1.dir != 'down':
            self.player1.moveup()
            self.player1.dir = 'up'
            p1_moved = True
        if event.key == K_KP2 and self.player1.dir != 'down' and not p1_moved:
          if self.player1.dir != 'up':
            self.player1.movedown()
            self.player1.dir = 'down'
            p1_moved = True
        if event.key == K_d and self.player2.dir != 'left' and not p2_moved:
          if self.player2.dir != 'right':
            self.player2.moveleft()
            self.player2.dir = 'right'
            p2_moved = True
        if event.key == K_g and self.player2.dir != 'right' and not p2_moved:
          if self.player2.dir != 'left':
            self.player2.moveright()
            self.player2.dir = 'right'
            p2_moved = True
        if event.key == K_r and self.player2.dir != 'up' and not p2_moved:
          if self.player2.dir != 'down':
            self.player2.moveup()
            self.player2.dir = 'up'
            p2_moved = True
        if event.key == K_f and self.player2.dir != 'down' and not p2_moved:
          if self.player2.dir != 'up':
            self.player2.movedown()
            self.player2.dir = 'down'
            p2_moved = True
        if event.key == K_2:
          self.close_sockets(self.sock_list)

  def handle_key_press(self, events):
    """handles the pygame keyboard events."""
    # bug that you can go back on yourself if you register a lot of button presses
    p1_moved = False
    p2_moved = False
    for event in events:
      if event.type == pygame.QUIT:
          sys.exit()
      if event.type == KEYDOWN:
        # check if trying to go back on themselves
        if event.key == K_LSHIFT and self.player1.dir != 'left' and not p1_moved:
          if self.player1.dir != 'right':
            self.player1.moveleft()
            self.player1.dir = 'left'
            p1_moved = True
        if event.key == K_x and self.player1.dir != 'right' and not p1_moved:
          if self.player1.dir != 'left':
            self.player1.moveright()
            self.player1.dir = 'right'
            p1_moved = True
        if event.key == K_LALT and self.player1.dir != 'up' and not p1_moved:
          if self.player1.dir != 'down':
            self.player1.moveup()
            self.player1.dir = 'up'
            p1_moved = True
        if event.key == K_z and self.player1.dir != 'down' and not p1_moved:
          if self.player1.dir != 'up':
            self.player1.movedown()
            self.player1.dir = 'down'
            p1_moved = True
        if event.key == K_w and self.player2.dir != 'left' and not p2_moved:
          if self.player2.dir != 'right':
            self.player2.moveleft()
            self.player2.dir = 'left'
            p2_moved = True
        if event.key == K_LEFTBRACKET and self.player2.dir != 'right' and not p2_moved:
          if self.player2.dir != 'left':
            self.player2.moveright()
            self.player2.dir = 'right'
            p2_moved = True
        if event.key == K_s and self.player2.dir != 'up' and not p2_moved:
          if self.player2.dir != 'down':
            self.player2.moveup()
            self.player2.dir = 'up'
            p2_moved = True
        if event.key == K_e and self.player2.dir != 'down' and not p2_moved:
          if self.player2.dir != 'up':
            self.player2.movedown()
            self.player2.dir = 'down'
            p2_moved = True
        if event.key == K_2:
          self.close_sockets(self.sock_list)

  def get_whole_packet(self, socket):
    """ensures that we receive the whole stream of data"""
    data = ''
    while True:
      data += socket.recv(4024)
      split = data.split(SOCKET_DEL) # split at newline, as per our custom protocol
      if len(split) != 2: # it should be 2 elements big if it got the whole message
        pass
      else:
        x = cPickle.loads(split[0])
        return x

  def close_sockets(self, sock_list):
    """kills and shutdown all the sockets. Despite adhering to exactly how it
    should be done, seems to not work effectively"""
    kill_struct = {'state': 'kill' }
    kill_pickle = cPickle.dumps(kill_struct, cPickle.HIGHEST_PROTOCOL) + '*ET*'
    for x in range(0, len(sock_list)):
      for y in range(0, len(sock_list[x])):
        sock_list[x][y].sendall(kill_pickle)
        sock_list[x][y].shutdown(socket.SHUT_RDWR)
        sock_list[x][y].close()
    sys.exit()

  def init_locations(self):
    """initilizes all of the location varibles and players"""
    self.location = []
    for x in range(0,FULL_GRID_SIZE[0] ):
      self.location.append([])
      for y in range(0,FULL_GRID_SIZE[1]):
        self.location[x].append(0) # 0 

    self.player1.location = PLAYER1_START[:]
    self.player1.velocity = [1,0]
    self.player1.orientation = 'hor'
    self.player1.last_key = K_KP4    
    self.player2.location = PLAYER2_START[:]
    self.player2.velocity = [-1,0]
    self.player2.orientation = 'hor'
    self.player2.last_key = K_g

    self.last_loc_1 = [[-1, FULL_GRID_SIZE[1]/2], 'off'] # initilize off screen, shouldn't affect anythin
    self.last_2_loc_1 = [[-2, FULL_GRID_SIZE[1]/2], 'off']
    self.last_loc_2 = [[ FULL_GRID_SIZE[0], FULL_GRID_SIZE[1]/2] , 'off'] # initilize off screen, shouldn't affect anythin
    self.last_2_loc_2 = [[FULL_GRID_SIZE[0]+1, FULL_GRID_SIZE[1]/2], 'off']
    self.state = 'play'

  def convert_to_global(self, tile, location):
    x_pos = location[0] + tile[0]*WORKER_NODE_SIZE[0]
    y_pos = location[1] + tile[1]*WORKER_NODE_SIZE[1]
    return x_pos, y_pos

  # def loc_collision(bike):
  #   # check the location array to see if colided.
  #   if bike.location[0] < 0 or bike.location[0] > FULL_GRID_SIZE[0]:
  #     print "died of screen in x"
  #     return True
  #   if bike.location[1] < 0 or bike.location[1] > FULL_GRID_SIZE[1]:
  #     print "died off screen in y"
  #     return True

  # def handle_move(self):
  #    """handles the pygame keyboard events."""
  #    # bug that you can go back on yourself if you register a lot of button presses
  #    p1_moved = False
  #    p2_moved = False
  #    for event in pygame.event.get():
  #      if event.type == pygame.QUIT:
  #          sys.exit()
  #      if event.type == KEYDOWN:
  #        # check if trying to go back on themselves
  #        if event.key == self.player1.left and not p1_moved:
  #          if self.player1.last_key != self.player1.right and self.player1.last_key != self.player1.left:
  #            self.player1.moveleft()
  #            self.player1.last_key = self.player1.left
  #            p1_moved = True
  #        if event.key == self.player1.right and self.player1.last_key != self.player1.right and not p1_moved:
  #          if self.player1.last_key != self.player1.left:
  #            self.player1.moveright()
  #            self.player1.last_key = self.player1.right
  #            p1_moved = True
  #        if event.key == self.player1.up and self.player1.last_key != self.player1.up and not p1_moved:
  #          if self.player1.last_key != self.player1.down:
  #            self.player1.moveup()
  #            self.player1.last_key = self.player1.up
  #            p1_moved = True
  #        if event.key == self.player1.down and self.player1.last_key != self.player1.down and not p1_moved:
  #          if self.player1.last_key != self.player1.up:
  #            self.player1.movedown()
  #            self.player1.last_key = self.player1.down
  #            p1_moved = True
  #        if event.key == self.player2.left and self.player2.last_key != self.player2.left and not p2_moved:
  #          if self.player2.last_key != self.player2.right:
  #            self.player2.moveleft()
  #            self.player2.last_key = self.player2.right
  #            p2_moved = True
  #        if event.key == self.player2.right and self.player2.last_key != self.player2.right and not p2_moved:
  #          if self.player2.last_key != self.player2.left:
  #            self.player2.moveright()
  #            self.player2.last_key = self.player2.left
  #            p2_moved = True
  #        if event.key == self.player2.up and self.player2.last_key != self.player2.up and not p2_moved:
  #          if self.player2.last_key != self.player2.down:
  #            self.player2.moveup()
  #            self.player2.last_key = self.player2.up
  #            p2_moved = True
  #        if event.key == self.player2.down and self.player2.last_key != self.player2.down and not p2_moved:
  #          if self.player2.last_key != self.player2.up:
  #            self.player2.movedown()
  #            self.player2.last_key = self.player2.down
  #            p2_moved = True
  #        if event.key == K_2:
  #          self.close_sockets(self.sock_list)
  
if __name__ == '__main__':
  tron = MasterTron()
  tron.run()
  
