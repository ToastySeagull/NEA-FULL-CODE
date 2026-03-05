import pygame
pygame.init()


tileSize = 32
deviceInfo = pygame.display.Info()
deviceWidth = deviceInfo.current_w      # pixels
deviceHeight = deviceInfo.current_h     # pixels
deviceWidth = (deviceWidth//tileSize)*tileSize
deviceHeight = (deviceHeight//tileSize)*tileSize
backgroundColour = (48, 31, 36)

deviceWidthTiles = deviceWidth // tileSize
deviceHeightTiles = deviceHeight // tileSize
screenWidth = 0 #for now, px - FOR THE WINDOW
screenHeight = 0 #for now, px - FOR THE WINDOW

white =     (255, 255, 255) # walkable
black =     (0, 0, 0)       # nonwalkable
red =       (255, 4, 0)     # playerStart
green =     (0, 255, 21)    # shopAccess
blue =      (0, 97, 255)    # roundStart
yellow =    (248, 255, 0)   # NPCStart
darkGreen = (17, 54, 17)    # NPCStopPoint
purple =    (211, 3, 252)   # startTaskPoint
cyan =      (3, 231, 252)   # seatFrontAirport
navy =      (10, 9, 41)     # BLANK
orange =    (255, 161, 0)   # seatBackAirport
grey =      (129, 129, 129) # seatAirplane

nonWalkableColours = [black,cyan,orange,grey,navy]

tileColourFunctions = {red:       'playerStartSpawn',   # translates colours to text so they are easier to identify
                       orange:    'seatBackAirport',
                       yellow:    'NPCSpawnPoint',
                       green:     'shopAccessPoint',
                       darkGreen: 'NPCStopPoint',
                       blue:      'roundStartPoint',
                       cyan:      'seatFrontAirport',
                       purple:    'startTaskPoint',
                       grey:      'seatAirplane',
                       black:     None,
                       navy:      'seatAccess',
                       white:     None,
                       }
seats = ['seatBackAirport','seatFrontAirport','seatAirplane','seatAccess']

allColours = [white, # list is premade and ready for use in any random selections if needed.
              black,
              red,
              green,
              blue,
              yellow,
              darkGreen,
              purple,
              cyan,
              navy,
              orange,
              grey]

npcColours = [(222, 96, 82), # for NPC appearances
              (82, 222, 82),
              (82, 220, 222),
              (113, 117, 222),
              (207, 113, 222),
              white]

validTileDestinationColours = [darkGreen,orange,cyan,grey] # areas that NPCs should traverse to
allInputKeys= [pygame.K_a+i for i in range(26)]+[pygame.K_SPACE] # pygame A is 97, B is 98....
allInputKeys.remove(97) # A         removing movement keys from the selection
allInputKeys.remove(100)# D
allInputKeys.remove(115)# S
allInputKeys.remove(119)# W
letters = "abcdefghijklmnopqrstuvwxyz" # to display on screen in the instructions message

movementKeys = [97,100,115,119,1073741906,1073741905,1073741904,1073741903] # including WASD and arrow keys

timeBarColour = [(20, 31, 64),(97, 225, 238)] # rim, fill
healthBarColour = [(115, 26, 28), (230, 37, 41)]
