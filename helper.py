#helper function that cleans everything up

#Load images method from the master file put here
import pygame

def load_images():
  image_dict = {}
  image_dict['c_hd_rt'] = pygame.image.load('assets/comet_head.png').convert_alpha()
  image_dict['c_hd_dn'] = pygame.transform.rotate(image_dict['c_hd_rt'], -90)
  image_dict['c_hd_lf'] = pygame.transform.rotate(image_dict['c_hd_rt'], -180)
  image_dict['c_hd_up'] = pygame.transform.rotate(image_dict['c_hd_rt'], -270)

  image_dict['m_hd_rt'] = pygame.image.load('assets/meteor_head.png').convert_alpha()
  image_dict['m_hd_dn'] = pygame.transform.rotate(image_dict['m_hd_rt'], -90)
  image_dict['m_hd_lf'] = pygame.transform.rotate(image_dict['m_hd_rt'], -180)
  image_dict['m_hd_up'] = pygame.transform.rotate(image_dict['m_hd_rt'], -270)

  image_dict['c_md_hor_r'] = pygame.image.load('assets/comet_mid.png').convert_alpha()
  image_dict['c_md_ver_u'] = pygame.transform.rotate(image_dict['c_md_hor_r'], 90)
  image_dict['c_md_hor_l'] = pygame.transform.rotate(image_dict['c_md_hor_r'], 180)
  image_dict['c_md_ver_d'] = pygame.transform.rotate(image_dict['c_md_hor_r'], 270)

  image_dict['c_tl_hor'] = pygame.image.load('assets/comet_tail.png').convert_alpha()
  image_dict['c_tl_ver'] = pygame.transform.rotate(image_dict['c_tl_hor'], 90)

  image_dict['m_md_hor_r'] = pygame.image.load('assets/meteor_mid.png').convert_alpha()
  image_dict['m_md_ver_u'] = pygame.transform.rotate(image_dict['m_md_hor_r'], 90)
  image_dict['m_md_hor_l'] = pygame.transform.rotate(image_dict['m_md_hor_r'], 180)
  image_dict['m_md_ver_d'] = pygame.transform.rotate(image_dict['m_md_hor_r'], 270)

  image_dict['m_tl_hor'] = pygame.image.load('assets/meteor_tail.png').convert_alpha()
  image_dict['m_tl_ver'] = pygame.transform.rotate(image_dict['m_tl_hor'], 90)

  image_dict['m_co_ur'] = pygame.image.load('assets/meteor_corner.png').convert_alpha()
  image_dict['m_co_lr'] = pygame.transform.rotate(image_dict['m_co_ur'], -90)
  image_dict['m_co_ll'] = pygame.transform.rotate(image_dict['m_co_ur'], -180)
  image_dict['m_co_ul'] = pygame.transform.rotate(image_dict['m_co_ur'], -270)

  image_dict['c_co_ur'] = pygame.image.load('assets/comet_corner.png').convert_alpha()
  image_dict['c_co_lr'] = pygame.transform.rotate(image_dict['c_co_ur'], -90)
  image_dict['c_co_ll'] = pygame.transform.rotate(image_dict['c_co_ur'], -180)
  image_dict['c_co_ul'] = pygame.transform.rotate(image_dict['c_co_ur'], -270)

  image_dict['explode0'] = pygame.image.load('assets/explosion_128.png').convert_alpha()
  image_dict['explode1'] = pygame.image.load('assets/explosion_256.png').convert_alpha()
  image_dict['explode2'] = pygame.image.load('assets/explosion_512.png').convert_alpha()
  image_dict['explode3'] = pygame.image.load('assets/explosion_1024a.png').convert_alpha()
  image_dict['explode4'] = pygame.image.load('assets/explosion_1024b.png').convert_alpha()
  return image_dict


def construct_list(last_2_loc, last_loc, head, middle, tail):
  """logic for corner cases when drawing the corners. The case for 
  when there is a corner followed by another corner. Lets the drawing nodes
  know that the second to last location was also a corner so leave it unchagned"""
  if last_loc[1] == 'cor':
    return [head, middle, 'corner']
  else:
    return[head, middle, tail]


def draw_logic(last_2_loc, last_loc, player, flipx, flipy, which):
  """decides which images to tell the render nodes to draw"""
  image_key_list = []
  if last_loc[0][0] == player.location[0] and last_loc[0][0] == last_2_loc[0][0]:
    # traveling vertically straight
    if last_loc[0][1] > player.location[1]:
      # traveling UP
      image_key_list.append(which + '_hd_up')
      image_key_list.append(which + '_md_ver_u')
    else:
      # traveling DOWN
      image_key_list.append(which + '_hd_dn')
      image_key_list.append(which + '_md_ver_d')
    if last_2_loc[1] != 'cor':
      # don't override corners for tail
      image_key_list.append(which + '_tl_'+last_loc[1])
    else: 
      image_key_list.append('corner')
    last_loc[1] = 'ver'
    # player.orientation = 'ver'
  elif last_loc[0][1] == player.location[1] and last_loc[0][1] == last_2_loc[0][1]:
    # traveling horizontally straight
    if last_loc[0][0] > player.location[0]:
       # traveling left
      image_key_list.append(which + '_hd_lf')
      image_key_list.append(which + '_md_hor_l')
    else:
       # traveling right
      image_key_list.append(which + '_hd_rt')
      image_key_list.append(which + '_md_hor_r')
    if last_2_loc[1] != 'cor':
      # don't override corners for tail
      image_key_list.append(which + '_tl_'+last_loc[1])
    else:
      # don't need to update corner drawing
      image_key_list.append('corner')
    last_loc[1] = 'hor' 
  else:
    #traveling the corners
    # print "here"
    # print "player.location = " + str(player.location) + "prev_loc = " + str(last_loc) + " last_2_loc = " + str(last_2_loc)
    # at a corner, checking explicitly for the eight cases
    if (player.location[0] == last_loc[0][0] and player.location[0] > last_2_loc[0][0]
      and player.location[1] > last_loc[0][1] and player.location[1] > last_2_loc[0][1]):
      #upper right, going down
      if flipy or flipx:
        print "FLIPING!"
        image_key_list = construct_list(last_2_loc, last_loc, which + '_hd_dn', which + '_co_ll', which + '_tl_hor')
      else:
        image_key_list = construct_list(last_2_loc, last_loc, which + '_hd_dn', which + '_co_ur', which + '_tl_hor')
      last_loc[1] = 'cor'
    elif (player.location[0] < last_loc[0][0] and player.location[0] < last_2_loc[0][0]
      and player.location[1] == last_loc[0][1] and player.location[1] < last_2_loc[0][1]):
      #upper right, going left
      image_key_list = construct_list(last_2_loc, last_loc, which + '_hd_lf', which + '_co_ur',which + '_tl_ver' )
      last_loc[1] = 'cor'

    elif (player.location[0] > last_loc[0][0] and player.location[0] > last_2_loc[0][0]
      and player.location[1] == last_loc[0][1] and player.location[1] > last_2_loc[0][1]):
      # lower left, going right
      image_key_list = construct_list(last_2_loc, last_loc, which + '_hd_rt', which + '_co_ll',which + '_tl_ver' )
      last_loc[1] = 'cor'

    elif (player.location[0] == last_loc[0][0] and player.location[0] < last_2_loc[0][0]
      and player.location[1] < last_loc[0][1] and player.location[1] < last_2_loc[0][1]):
       # lower left, clockwise
      image_key_list = construct_list(last_2_loc, last_loc, which + '_hd_up', which + '_co_ll',which + '_tl_hor' )
      last_loc[1] = 'cor'
       
    elif (player.location[0] > last_loc[0][0] and player.location[0] > last_2_loc[0][0]
      and player.location[1] == last_loc[0][1] and player.location[1] < last_2_loc[0][1]):
      # upper left clockwise
      image_key_list = construct_list(last_2_loc, last_loc, which + '_hd_rt', which + '_co_ul',which + '_tl_ver' )
      last_loc[1] = 'cor'
       
    elif (player.location[0] == last_loc[0][0] and player.location[0] < last_2_loc[0][0]
      and player.location[1] > last_loc[0][1] and player.location[1] > last_2_loc[0][1]):
      # upper left counterclockwise
      image_key_list = construct_list(last_2_loc, last_loc, which + '_hd_dn', which + '_co_ul',which + '_tl_hor' )
      last_loc[1] = 'cor'
       
    elif (player.location[0] == last_loc[0][0] and player.location[0] > last_2_loc[0][0]
      and player.location[1] < last_loc[0][1] and player.location[1] < last_2_loc[0][1]):
      # lower right counterclockwise
      image_key_list = construct_list(last_2_loc, last_loc, which + '_hd_up', which + '_co_lr',which + '_tl_hor' )
      last_loc[1] = 'cor'
       
    elif (player.location[0] < last_loc[0][0] and player.location[0] < last_2_loc[0][0]
      and player.location[1] == last_loc[0][1] and player.location[1] > last_2_loc[0][1]):
      # lower right clockwise
      image_key_list = construct_list(last_2_loc, last_loc, which + '_hd_lf', which + '_co_lr',which + '_tl_ver' )
      last_loc[1] = 'cor'
  return image_key_list