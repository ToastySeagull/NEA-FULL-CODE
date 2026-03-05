import pygame
import constants
import extraFunctions as funks
import json
import sys
import os

# for start screens, loading screens, etc.
class Screens:
	def __init__(self, name):
		self.currentBackground = "Screens/clouds.png"
		self.title = self.getTitle(name)
		self.trueTileSize = constants.tileSize

# separate function for big heading cuz font size is different.
	def getTitle(self, name):
		fontSize = 64
		font = pygame.font.Font(None,fontSize)
		return font.render(name,True,(0,50,50))

# creates the pygaem window
	def makeSurface(self): # creates the main pygame surface/window
		screenWidth = constants.deviceWidth - (5*self.trueTileSize)
		constants.screenWidth = (screenWidth//self.trueTileSize)*self.trueTileSize # set val in constants to be used for rest of game
		screenHeight = constants.deviceHeight - (5*self.trueTileSize)
		constants.screenHeight = (screenHeight//self.trueTileSize)*self.trueTileSize
		# imgSize = [1216,704]
		surface = pygame.display.set_mode((constants.screenWidth,constants.screenHeight))
		self.currentBackground = pygame.image.load(self.currentBackground).convert_alpha()	# actual initialisation of self.currentBackground cuz this cant be done before pygame.display.set_mode() is called.
		self.currentBackground = pygame.transform.scale(self.currentBackground,(constants.screenWidth,constants.screenHeight)) # makes sure image is same size as pyWindow.
		return surface	# for while loop
	
class startScreen(Screens):
	def __init__(self):
		super().__init__("The Plane Game") # inherits all from parent class

	def loop(self):
		surface = self.makeSurface()	# initiates the surface obj.
		surface.blit(self.currentBackground,(0,0))	# drawing bg onto surface.
		xCoord = (constants.screenWidth//2)
		yCoord = constants.screenHeight//4
		surface.blit(self.title,(xCoord - (self.title.get_width()//2),yCoord))	# draws title on surface
		playButton = Buttons("play") # creates the Play button
		surface.blit(playButton.image,(xCoord-(playButton.image.get_width()//2),yCoord + self.title.get_height() + self.trueTileSize)) # draws play button on surface.
		playButton.coordinates = (xCoord-(playButton.image.get_width()//2),yCoord + self.title.get_height() + self.trueTileSize) # sets the coords of the button, to be used to check for click area.
		continueToGame= False # flag for closing this while loop and moving onto the actual game.
		while not continueToGame:
			for event in pygame.event.get(): # checks all game events, like key presses and mouse clicks.
				if event.type == pygame.QUIT: # if the x in the corner is pressed, the game window completely shuts down.
					pygame.quit()
					sys.exit()
				if event.type == pygame.MOUSEBUTTONDOWN: 
					if event.button == 1:	# 1 is left click
						continueToGame = playButton.checkClicked(event.pos) # returns True or False
			pygame.display.update() # resets the screen, taking into account all .blit() calls that havent yet been displayed.
			# no need for clock.tick() cuz nothing moves in this screen.

class Buttons:
	def __init__(self,name):
		self.trueTileSize = constants.tileSize #32, needed for scaling
		self.imageFile = "Overlays/buttons/"+name+".png"
		self.image = pygame.image.load(self.imageFile).convert_alpha() # creates surface obj
		self.image = pygame.transform.scale(self.image,(self.image.get_width()*0.25,self.image.get_height()*0.25)) # scales buttons down (they're too big raw)
		self.width = self.image.get_width()	# stored so that it does not need to be recalculated always
		self.height = self.image.get_height()
		self.nextScreen = None # for now
		self.coordinates = () # for now. set later 'depending on situation'

	def checkClicked(self,event):
		if self.coordinates[0] <= event[0] <= self.coordinates[0] + self.width: # checks x coord range of click
			if self.coordinates[1] <= event[1] <= self.coordinates[1] + self.height: # checks y coord range of click
				return True # true if in range
		return False # false if click is not on the button


class Tile:
	def __init__(self, ID, img, walkable, function, colour):
		self.ID = ID # unique number for each image type determined by Tiled.
		self.image = img # pygame obj 
		self.walkable = walkable
		self.function = function # function name (str)
		self.colour = colour	# (r,g,b,a)
		self.occupied = False
		self.staffDestination = False # for when staff destinations are random. Only for start?
	
	def displayTileInfo(self, col, row):	# for testing
		print("coordinates: (%d, %d), colour: %s, function: %s" %(col, row,self.colour,self.function))

class Overlay:	# UI things that aren't 'in the map'
	def __init__(self,name,coords,tileSize, scale):
		self.name = name
		self.coords = (coords[0]*tileSize,coords[1]*tileSize) # coords parsed should be in terms of TILE!!
		self.fileName = "Overlays/"+self.name+".png"
		self.image = None #funks.getScaled(self.image,scale)
		self.scale = scale	#some images need to be rescaled differently

	def setImage(self):
		self.image = funks.getScaled(self.fileName,self.scale) # surface needs to be drawn first so self.image is set later using this function.

	def draw(self,gameSurface):
		if not self.image: # if statement so that scaled doesnt happen each frame.
			self.setImage()
		gameSurface.blit(self.image,self.coords) # draws on surface parsed.

class animatedOverlay(Overlay): # things that are in the map
	def __init__(self,name,coords,tileSize,scale):
		super().__init__(name,coords,tileSize,scale)
		self.folder = "Overlays/"+self.name # folder cuz of animation frames.
		self.image = os.listdir(self.folder) # all FILE NAMES
		self.delay = 2000 # default, rate at which frames change in ms
		self.lastAnimationTime = 0
		self.currentImageIndex = 0

	def draw(self,gameSurface, surfaceCoordsDict,timePassed):
		if timePassed - self.lastAnimationTime >= self.delay: # checks if it is time to animate.
			nextImageIndex = (self.currentImageIndex + 1)%len(self.image)
			self.currentImageIndex = nextImageIndex # changes the current image to be drawn
			self.lastAnimationTime = timePassed	
		image = self.folder+"/"+self.image[self.currentImageIndex]
		scaledImage = funks.getScaled(image, self.scale)	
		if self.coords in surfaceCoordsDict: # checks if the image's position is currently being displayed on screen.
			coords = surfaceCoordsDict[self.coords]	
			gameSurface.blit(scaledImage, (coords[0], coords[1]))			

class ProgressBar():
	def __init__(self,scale,colour,coords,tileSize,length,maxMeasure):
		self.coords = (coords[0]*tileSize,coords[1]*tileSize) # coords in terms of TILE, like w the overlays.
		self.rimColour, self.fillColour = colour # for the recolouring using pygame.BLEND_--- channels
		self.scale = scale # for resizing
		self.folder = "Overlays/progressBar"	# separate image blocks are stored in the same file
		self.imageOrder = [] # stores all the blocks making up a single bar object

		self.length = length #tiles
		self.maxMeasure = maxMeasure	#the 'limit' it's measuring: like, 10 mins or something
		self.tileSize = tileSize*2	# stored here so i dont have to keep parsing

		self.fillOffset = 20	# bar doesnt go 32px across so pad needed
		self.maxFillLength = (self.length)*self.tileSize*self.scale # offset from both sides
		self.fill = pygame.image.load(self.folder+"/inside.png").convert_alpha()
		self.fullFill = pygame.transform.scale(self.fill, (self.maxFillLength,self.fill.get_height()))
		self.fullFill.fill((self.fillColour), special_flags=pygame.BLEND_MIN)
	
	def setBar(self):		#creates a bar of the correct size
		# gets image object (scaled) for each bar piece.
		loadedLeft = funks.getScaled(self.folder+"/"+"progressBarLeft.png",self.scale)
		loadedRight = funks.getScaled(self.folder+"/"+"progressBarRight.png",self.scale)
		loadedMid = funks.getScaled(self.folder+"/"+"progressBarMiddle.png",self.scale)

		# recolours bar:
		loadedLeft.fill(self.rimColour,special_flags=pygame.BLEND_MIN)
		loadedRight.fill(self.rimColour,special_flags=pygame.BLEND_MIN)
		loadedMid.fill(self.rimColour,special_flags=pygame.BLEND_MIN)

		# initiates self.imageOrder
		self.imageOrder.append(loadedLeft)
		for i in range(0,self.length-2):
			self.imageOrder.append(loadedMid)
		self.imageOrder.append(loadedRight)
	
	def draw(self, gameSurface):	#displays the bar
		for i in range(0,len(self.imageOrder)):
			x,y = self.coords[0]+(i*self.tileSize), self.coords[1] # adds padding and the previous tile's height
			gameSurface.blit(self.imageOrder[i],(x,y))
		
	def updateProgress(self,gameSurface, currentMeasure):
		# draws the fill by cutting down the whole length's image.
		percentageFill = max(0,min(currentMeasure/self.maxMeasure,1))
		currentWidth = (self.maxFillLength - 40)*percentageFill
		currentFill = pygame.Rect(20,0,currentWidth,self.fullFill.get_height())
		gameSurface.blit(self.fullFill,(self.coords[0]+self.fillOffset,self.coords[1]),currentFill) 
		# makes the progress bar's title
		fontSize = 32
		font = pygame.font.Font(None,fontSize)
		pyText = font.render("p r o g r e s s",True,(145, 168, 207))
		if self.rimColour == constants.healthBarColour[0]:
			pyText = font.render("h e a l t h",True,(224, 139, 141))
		xCoords = self.coords[0] + (self.length*self.tileSize//2) - (pyText.get_width()//2)
		gameSurface.blit(pyText,(xCoords,self.coords[1]+(self.tileSize)//4))

class Game:
	def __init__(self, name, mapSize):
		self.name = name
		self.mapFileName = "MapStuff/mapTiledFiles/" + self.name + '.tmj'
		self.mapSize = mapSize  # terms of tiles [w,h]
		self.tileScaleFactor = max(1,constants.deviceWidthTiles//self.mapSize[0])
		self.trueTileSize = constants.tileSize #for now
		self.tilesDict = {}					# whole map coordinates keyed against tile image type
		self.tileImageDict = {}				# keys tile IDs to tile images
		self.surfaceCoordinatesDict = {}	# relevant whole map coordinates to screen coordinates
		self.playerStartCoordinates = ()
		self.NPCCapacity = 0	#for passengers
		self.trackSpawnedPassengers = 0	#in one moment
		self.NPCStartCoordinates = []		# all NPC spawn points
		self.NPCList = []
		self.freeNPCDestinations = []		#coordinates

	def processTiles(self, tileSets): # gathers data from tmj files
		emptyImage = pygame.Surface((self.trueTileSize,self.trueTileSize), pygame.SRCALPHA)
		self.tileImageDict[0] = emptyImage

		for tileset in tileSets:
			jsonFileName = 'MapStuff'+tileset['source'][2:]
			with open(jsonFileName) as f:	# reads the file
				tileSetData = json.load(f) # this variable stores the entire tileset's info
			currentID = tileset['firstgid']
			columns = tileSetData['columns']
			numIDs = tileSetData['tilecount']
			rows = int(numIDs/columns)
			
			source = 'MapStuff'+tileSetData['image'][2:]
			tileSetImage = funks.getScaled(source, self.tileScaleFactor) # gets the image as a pygame surface object
			# gathers each type of image and adds it to a dictionary.
			for row in range(0,rows):
				y = row*self.trueTileSize
				for col in range(0,columns):
					x = col*self.trueTileSize
					base = pygame.Rect(x,y,self.trueTileSize,self.trueTileSize) #takes a 'picture' of image at xy
					tileImage = tileSetImage.subsurface(base).copy()

					self.tileImageDict[currentID] = tileImage #stores said picture here
					currentID += 1

	def setTiles(self):	# creates tile objects for each image, assigning them to the correct coords for tilesDict
		with open(self.mapFileName) as f:
			mapData = json.load(f) # gets the whole map's data.
		mapLayer = mapData['layers'][0]['data']	# 1st layer is the actual tiles, second layer is the collision tiles
		collisionLayer = mapData['layers'][1]['data']
		tileSets = mapData['tilesets']	
		self.processTiles(tileSets)	# gets the data for each tile in each tilesets in the map

		currentIndex = 0	
		# initiates all other tile'related attributes of the game class.
		for row in range(0, self.mapSize[1]):
			y = row*self.trueTileSize
			for col in range(0,self.mapSize[0]):
				x = col*self.trueTileSize
				currentMapID = mapLayer[currentIndex]
				mapTileImage = self.tileImageDict[currentMapID]
				currentCollisionID = collisionLayer[currentIndex]
				collisionImage = self.tileImageDict[currentCollisionID]

				if currentMapID == 0: colour = constants.black # a fill in cuz a value needs to be taken; 0 means clear tiles
				else: colour = collisionImage.get_at((self.trueTileSize//2,self.trueTileSize//2))[0:3]
				# Gets specifc tiles depending on their functions for attributes.
				if colour == constants.red: self.playerStartCoordinates = (x,y) # finds player start point
				if colour == constants.yellow: self.NPCStartCoordinates.append((x,y))	# finds NPC spawn points 
				if colour in constants.validTileDestinationColours: # finds all possible NPC destinations
					self.freeNPCDestinations.append((x,y))
				# CREATING TILE OBJECT
				tileColourFunction = constants.tileColourFunctions[colour] # getting tile object parameters
				walkable = False if colour in constants.nonWalkableColours else True
				currentMapTile = Tile(currentMapID,mapTileImage,walkable,tileColourFunction,colour)
				self.tilesDict[(x,y)] = currentMapTile	# adds tile to the tilesDict
				currentIndex += 1	# cant have the index reset each loop.

	def makeSurface(self): # creates the main pygame surface/window
		screenWidth = constants.deviceWidth - (5*self.trueTileSize)
		constants.screenWidth = (screenWidth//self.trueTileSize)*self.trueTileSize
		screenHeight = constants.deviceHeight - (5*self.trueTileSize)
		constants.screenHeight = (screenHeight//self.trueTileSize)*self.trueTileSize

		surface = pygame.display.set_mode((constants.screenWidth,constants.screenHeight))
		surface.fill(constants.backgroundColour)
		return surface

	def drawMap(self, surface, player): # creates scrollable map
		surface.fill(constants.backgroundColour)	#it's here too cuz the surface needs to be refreshed and redrawn after each loop soo
		self.surfaceCoordinatesDict = {}		# resets tiles dict for the surface only cuz its getting redrawn consistently.

		screenWidthTiles = constants.screenWidth//self.trueTileSize 
		screenHeightTiles = constants.screenHeight//self.trueTileSize

		# cacluates player position relative to the screen's coords
		xCoordinate = ((surface.get_width()//2)//self.trueTileSize)*self.trueTileSize
		yCoordinate = ((surface.get_height()//2)//self.trueTileSize)*self.trueTileSize
		newPlayerCoords = (xCoordinate, yCoordinate)
		offsetX = ((player.coordinates[0] - newPlayerCoords[0])//self.trueTileSize)*self.trueTileSize
		offsetY = ((player.coordinates[1] - newPlayerCoords[1])//self.trueTileSize)*self.trueTileSize
		# draws all tiles around the player relative to the screen size.
		for row in range(0,screenHeightTiles):
			screenY = row*self.trueTileSize
			mapY = screenY + offsetY   
			for col in range(0,screenWidthTiles):
				screenX = col*self.trueTileSize
				mapX = screenX + offsetX
				if (mapX, mapY) in self.tilesDict:
					self.surfaceCoordinatesDict[(mapX,mapY)] = (screenX,screenY)
					tileImage = self.tilesDict[(mapX,mapY)].image
					surface.blit(tileImage, (screenX, screenY))

	def spawnNPCs(self, crew):
		permitSpawn = funks.random.randint(0,45)	# determines rate of spawn
		left = [(0,21*self.trueTileSize),(0,22*self.trueTileSize)] #left side spawnpoint coords in airport
		if permitSpawn == 20:
			chooseType = 1 if self.trackSpawnedPassengers != self.NPCCapacity else 2 # chooses Passengers first until capacity has been met, and then chooses workers
			start = funks.random.choice(self.NPCStartCoordinates)	# gets the spawn point of the NPC
			startTile = self.tilesDict[start]	# tile of the spawn point

			# checks if any NPCs already have the startTile as their destination
			if not startTile.occupied:
				npc = ''	
				if chooseType == 1:
					npc = NPCPassenger(start,funks.getPatience())
					self.trackSpawnedPassengers += 1
				elif chooseType == 2:
					npc = funks.random.choice(crew)
					if npc not in self.NPCList:
						npc.coordinates = start
					else: npc = ''

				if npc:
					npc.getDestination(self) # gives them a place to go to from the queue
					npc.AStar(self) # creates path to the intended destination

					if not npc.path:	# ensures that a path to the destination is found (more for passengers going to seats)
						side = ''
						if isinstance(self, Airport):
							side = 'left' if start in left else 'right'
						npc.destination,npc.extraRoute = funks.getNearestAisleCoords(self,npc.destination,side)
						npc.AStar(self)
						
					self.NPCList.append(npc) # 'attaches' npc to the game
					self.tilesDict[start].occupied = True

	def resetNPCSpawns(self):
		# resets all attributes relatng to NPCs spawn so that game loads up correctly in the next round.
		self.NPCList = []
		self.trackSpawnedPassengers = 0

class Airport(Game):
	def __init__(self, mapFile, mapSize):
		super().__init__(mapFile, mapSize)
		self.NPCCapacity = 7 # for passengers
	
	def gameLoop(self, player):
		self.setTiles() # initiates all tile-related attributes
		gameSurface = self.makeSurface() # creates surface
		player.coordinates = self.playerStartCoordinates # sets player's spawn point

		player.resetTimes()	# makes sure everything starts fresh
		self.resetNPCSpawns()	# resets data before round starts
		isPlayerMoving = False	# flag for animations
		clock = pygame.time.Clock()	# for clock.tick()
		startTime = pygame.time.get_ticks() #get_ticks() gives time since init called. 
		#                                   var = time when round started (ms).
		# OVERLAYS
		timeboard = animatedOverlay('timeboard',[28,6],self.trueTileSize, 2*self.tileScaleFactor)
		overlays = [timeboard]
		while True:
			currentTime = pygame.time.get_ticks()       # more time stuff
			timePassed = currentTime - startTime # time passed since this game was opened.
			self.drawMap(gameSurface,player) # scrolling map is drawn

			# DRAW OVERLAYS
			for overlay in overlays:
				overlay.draw(gameSurface, self.surfaceCoordinatesDict, timePassed)

			# DRAW PLAYERS
			animationPack = 'walking' if isPlayerMoving else 'still' 
			playerAnimationChange = False
			if timePassed-player.lastAnimationTime >= player.animations[animationPack][0]:
				playerAnimationChange = True
				player.lastAnimationTime = timePassed
			player.drawPerson(gameSurface,self.tileScaleFactor,playerAnimationChange,animationPack)

			# INPUTS
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				
				if event.type == pygame.KEYUP:
					if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_a, pygame.K_s, pygame.K_w, pygame.K_d]:
						isPlayerMoving = False

			keys = pygame.key.get_pressed()
			if timePassed - player.lastMovementTime >= 100: # slows player down
				if keys[pygame.K_LEFT] or keys[pygame.K_a]:
					player.moveLeft(self)
					isPlayerMoving = True
				if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
					player.moveRight(self)
					isPlayerMoving = True
				if keys[pygame.K_UP] or keys[pygame.K_w]:
					player.moveUp(self)
					isPlayerMoving = True
				if keys[pygame.K_DOWN] or keys[pygame.K_s]:
					player.moveDown(self)
					isPlayerMoving = True
				player.lastMovementTime = timePassed

			# NPC STUFF
			self.spawnNPCs(player.crew) #loads NPCs in at random points during the game
			for npc in self.NPCList:
				npc.drawPerson(self,gameSurface,timePassed)	# draws the NPC

				if npc.path:	# Moves NPC
					if timePassed - npc.lastMovementTime >= 150: # slows down NPC movement
						moved = npc.moveNPC(self)
						if moved: npc.lastMovementTime = timePassed	
				elif npc.pathBlocked:	# Deals with strange errors
					npc.AStar(self)
				elif npc.extraRoute:	# mostly for NPCs going to seats or other 'unreachable' destinations
					if self.tilesDict[npc.coordinates].walkable: # for the nearest aisle coord.
						self.tilesDict[npc.coordinates].occupied = False
					if timePassed - npc.lastMovementTime >= 150:
						npc.extraMoveNPC()
						npc.lastMovementTime = timePassed
				# SIT ANIMATION
				if isinstance(npc,NPCPassenger) and npc.coordinates == npc.destination and self.tilesDict[npc.destination].function in constants.seats:
					npc.sit(self)
				
				#draws the info box
				mousePos = pygame.mouse.get_pos() # finds where mouse is hovering
				if npc.coordinates in self.surfaceCoordinatesDict: # npc might not be on screen currently
					npcCoords = self.surfaceCoordinatesDict[npc.coordinates]
					if npcCoords[0] <= mousePos[0] <= npcCoords[0]+self.trueTileSize and npcCoords[1]-self.trueTileSize <= mousePos[1] <= npcCoords[1]+self.trueTileSize:
						npc.drawInfo(mousePos,gameSurface)	# draws info box when mouse hovers over NPC.

			# check if tiles have functions:
			if self.tilesDict[player.coordinates].function == 'roundStartPoint':
				return -1       #breaks the game loop

			# determines the duration of one game loop?
			clock.tick(60)
			# updates display.
			pygame.display.update()

class TaskMenu: # for task menue UI
	def __init__(self, game, gameSurface):
		x = ((gameSurface.get_width()*0.8)//game.trueTileSize)*game.trueTileSize 
		y = ((gameSurface.get_height()*0.6)//game.trueTileSize)*game.trueTileSize
		self.coordinates = (x,y)	# top left coords of the menu rectangle
		self.width = gameSurface.get_width() - x
		self.height = gameSurface.get_height() - y
		self.rectangle = pygame.Rect(x,y,self.width,self.height)	# converts to a rectangle object to be used later potentially.
		self.changeTextDelay = 1000 #ms, 1s
		self.errorStartTime = 0	# last time that error message displays.
		self.errorFinished = True	
		self.texts = [] 
		self.completedDisplaying = False

		titleFont = pygame.font.Font(None,32)
		self.title = titleFont.render("TASKS",True,(9, 27, 38, 0)) # ceates title as pygame text object to be blitted later.

	def changeText(self,errorMessage:bool,failed:bool,currentTime,player):
		font = pygame.font.Font(None,16)	# changes text when task instruction changes/
		if self.errorFinished or errorMessage: # once delay since error displayed is over or an interuption is appearing.
			self.texts = []	
			texts = [] 
			if player.currentTask: # gets texts depending on situation
				texts = [player.currentTask.instruction,player.currentTask.timeLeft(currentTime)]
			if errorMessage:
				texts = [player.currentTask.instruction]
			elif failed: 
				texts = ["FAILED!"]
				self.errorStartTime = currentTime
				self.errorFinished = False
				self.completedDisplaying = True
			for i in range(0,len(texts)):
				pygameText = font.render(texts[i],True,(0,0,0))
				self.texts.append(pygameText)

			if errorMessage: # starts delay timer
				self.errorStartTime = currentTime
				self.errorFinished = False
		
		if not self.errorFinished: # checks if delay timer is over for a new message to then display.
			if currentTime - self.errorStartTime >= self.changeTextDelay:
				self.errorFinished = True
				self.errorStartTime = 0
				self.texts = []
	
	def displayTaskFinished(self, currentTime): # manually rewrites text for the TASK COMPLETED message
		self.errorFinished = False
		self.errorStartTime = currentTime
		font = pygame.font.Font(None,16)
		self.texts = [(font.render("TASK COMPLETE!",True,(0,0,0)))] # gets blitted in the draw; delay counts down from changeText()

	def draw(self,gameSurface): # blits texts onto the tasks menu.
		pygame.draw.rect(gameSurface,(167, 197, 204, 0),(self.coordinates[0],self.coordinates[1],self.width,self.height))
		topCenter = ((self.width//2)+self.coordinates[0]-(self.title.get_width()//2), self.coordinates[1]) # find the x coords for the title to be blitted relative to its own width
		gameSurface.blit(self.title,topCenter)
		for i in range(0,len(self.texts)):
				yCoord = (4*i)+self.coordinates[1]+(16*i)+ 2 if i != 0 else 32+4+self.coordinates[1]
				xCoord = self.coordinates[0] + 3
				gameSurface.blit(self.texts[i],(xCoord,yCoord)) # blits texts onto the surface where the text menu is located.

class Cabin(Game):
	def __init__(self, mapFile, mapSize):
		super().__init__(mapFile, mapSize)
		self.NPCCapacity = 5 # num passengers allowed into the plane.
		self.taskWorkSpace = [(x*self.trueTileSize,y*self.trueTileSize) for x in range(34,39) for y in range(15,17)] # galley coords
		self.duration = 150000 # 2.5 mins, duration of whole game.
		self.minTaskDelay = 5000 #5s 
	
	def displayRewards(self,allRewards,playerRewards,mistakesMade,gameSurface):
		coins,reps = allRewards
		fontSize = 24 # for information texts
		font = pygame.font.Font(None,fontSize)
		titleFont = pygame.font.Font(None,32)
		gameOver = "DESTINATION REACHED!"	# only outcome for Cabin minigame

		playerEarned = "PLAYER EARNED----  COINs: %d,  REPUTATION POINTs: %d" %(playerRewards[0],playerRewards[1])
		coins = "TOTAL COINs: %d" %(coins)
		reps = "TOTAL REPUTATION POINTs: %d" %(reps)
		mistakes = "MISTAKEs MADE: %d" %(mistakesMade)
		texts = [titleFont.render(gameOver,True,(0,0,0)), # all texts as pygame text objects.
				 font.render(playerEarned,True,(0,0,0)),
				 font.render(coins,True,(0,0,0)),
		   		 font.render(reps,True,(0,0,0)),
				 font.render(mistakes,True,(0,0,0))]
		
		yCoord = (constants.screenHeight//2)
		for i in range(len(texts)): # displays all texts on screen. 
			if i != 0: yCoord += texts[i-1].get_height() + (10*i)
			xCoord = (constants.screenWidth//2) - (texts[i].get_width()//2)
			gameSurface.blit(texts[i],(xCoord,yCoord))
		
		pygame.display.update()	# makes sure that display appears on screen before game loop moves on
		pygame.time.wait(5000) # 5s, keeps message on screen for set time before game loop moves on.


	def gameLoop(self, player):
		self.setTiles()  # same initiation process as before
		gameSurface = self.makeSurface()
		player.coordinates = self.playerStartCoordinates
		player.resetTimes()
		self.resetNPCSpawns()
		isPlayerMoving = False
		clock = pygame.time.Clock()
		startTime = pygame.time.get_ticks() #get_ticks() gives time since init called. 
		#                                   var = time when round started (ms)
		# INITIALISING UI FEATURES
		bar = ProgressBar(1*self.tileScaleFactor,constants.timeBarColour,(3,2),self.trueTileSize,10,self.duration)
		bar.setBar() # sets bar pieces before round starts
		taskMenu = TaskMenu(self,gameSurface) 

		activeTasksQueue = [] #to be treated as a queue

		# REWARDS VARIABLES
		workerRewards = [0,0] # coins, reps
		playerEarnedRewards = [0,0] # coins, reps
		playerTasksCompleted = 0
		totalMistakesMade = 0 

		arrived = set() # all NPCs who have arrived in their locations
		roundProgress = 0	# time passed since round starts
		roundStarted = False	# whether or not round has started
		roundStartTime = None	# sotres time at which game starts
		timePassedSinceTaskIssued = 0	# helps with the tasks delaying

		while True:
			currentTime = pygame.time.get_ticks() # gets time now
			timePassed = currentTime - startTime # time passed since this game has started
			keyInputs = [] # all key presses during this gameloop iteration
			clickLocations = [] # screen coords where user clicks during this gameloop iteration
			if roundStarted: roundProgress = currentTime - roundStartTime # needed for processes relative to round's progression

			# DRAWS
			self.drawMap(gameSurface,player)
			# PLAYER
			animationPack = 'walking' if isPlayerMoving else 'still' 
			playerAnimationChange = False
			if timePassed-player.lastAnimationTime >= player.animations[animationPack][0]:
				playerAnimationChange = True
				player.lastAnimationTime = timePassed
			player.drawPerson(gameSurface,self.tileScaleFactor,playerAnimationChange,animationPack)

			# INPUTS
			for event in pygame.event.get(): # all events mentioned only work for single key presses, not holds
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				# movement keys
				if event.type == pygame.KEYUP:
					if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_a, pygame.K_s, pygame.K_w, pygame.K_d]:
						isPlayerMoving = False
				# checks for gameplay-related key inputs
				if event.type == pygame.KEYDOWN:
					keyInputs.append(event.key)
				# finds mouse click locations
				if event.type == pygame.MOUSEBUTTONDOWN:
					if event.button == 1:	#left = 1, middle = 2, right = 3...
						clickLocations.append(event.pos)

			# PLAYER MOVEMENT
			keys = pygame.key.get_pressed()
			if timePassed - player.lastMovementTime >= 100: # 100 works like a cooldown -> increase to slow player down.
				if keys[pygame.K_LEFT] or keys[pygame.K_a]:
					player.moveLeft(self)
					isPlayerMoving = True
				if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
					player.moveRight(self)
					isPlayerMoving = True
				if keys[pygame.K_UP] or keys[pygame.K_w]:
					player.moveUp(self)
					isPlayerMoving = True
				if keys[pygame.K_DOWN] or keys[pygame.K_s]:
					player.moveDown(self)
					isPlayerMoving = True
				player.lastMovementTime = timePassed

			# NPC INTERACTIONS
			self.spawnNPCs(player.crew)
			for npc in self.NPCList:
				npc.drawPerson(self,gameSurface,timePassed)
				# NPC MOVEMENT
				if npc.path:
					if timePassed - npc.lastMovementTime >= 150:
						moved = npc.moveNPC(self)
						if moved: npc.lastMovementTime = timePassed	
				elif npc.pathBlocked:
					npc.AStar(self)
				elif npc.extraRoute:
					if self.tilesDict[npc.coordinates].walkable: # for the nearest aisle coord.
						self.tilesDict[npc.coordinates].occupied = False
					if timePassed - npc.lastMovementTime >= 150:
						npc.extraMoveNPC()
						npc.lastMovementTime = timePassed

				if not roundStarted:
					if npc.coordinates == npc.destination and not npc.extraRoute: #all passengers should have an extraRoute??
						if isinstance(npc,NPCPassenger):
							npc.sit(self)
						arrived.add(npc)

				# ROUND STARTED INTERACTIONS
				if roundStarted:
					npc.getBubble(self)
					if npc.bubble:
						npc.bubble.draw(gameSurface,self.surfaceCoordinatesDict,timePassed)
					# PASSENGERS
					if isinstance(npc,NPCPassenger):
						if not npc.currentTask: # tries to give NPCs a task if they do not have one
							if timePassed - timePassedSinceTaskIssued >= self.minTaskDelay:
								npc.giveTask(self)
								if npc.currentTask: 
									activeTasksQueue.append(npc.currentTask)
									timePassedSinceTaskIssued = timePassed
					# WORKERS
					if isinstance(npc,NPCWorker):
						if npc.currentTask: # visits previous passenger and then gets the task.
							npc.visitPassenger(self,"before")
							if npc.passengerVisited["before"]:
								npc.getDestination(self) 
								npc.currentTask.parentNPC.taskAvailable = False # changes some task object attributes so that game works correctly
								npc.currentTask.parentNPC.thinking = True
								if npc.coordinates == npc.destination:
									taskRewards = npc.performTask(currentTime) # checks if worker has stood in location for long enough
									if taskRewards: # gets rewards
										workerRewards[0] += taskRewards[0]
										workerRewards[1] += taskRewards[1]
										npc.visiting = True

						elif npc.passengerVisited["before"]: # checks if the passenger process was underway but the task was completed, indicating it is now finished
							npc.visitPassenger(self,"after") # goes to the passenger again as per the task sequence
							npc.thinking = False # kills bubble icon
							if npc.passengerVisited["after"]: # resets task data completely for current worker once all stages are complete
								npc.resetTaskData()
								npc.getDestination(self)
						
						elif activeTasksQueue: # gives the npc a task from active tasks queue.
							npc.getTask(activeTasksQueue,self)

				#info box
				mousePos = pygame.mouse.get_pos() # finds where mouse is hovering
				if npc.coordinates in self.surfaceCoordinatesDict: # npc might not be on screen currently
					npcCoords = self.surfaceCoordinatesDict[npc.coordinates]
					if npcCoords[0] <= mousePos[0] <= npcCoords[0]+self.trueTileSize and npcCoords[1]-self.trueTileSize <= mousePos[1] <= npcCoords[1]+self.trueTileSize:
						npc.drawInfo(mousePos,gameSurface)	# draws info box when mouse hovers over NPC.
			
			# checks if round should start and sets the correct variables
			if not roundStarted and len(arrived) == self.NPCCapacity+len(player.crew):
				roundStarted = True
				roundStartTime = pygame.time.get_ticks()
			# BAR DRAWS
			bar.draw(gameSurface)
			if roundStarted: 
				bar.updateProgress(gameSurface,roundProgress)
				taskMenu.draw(gameSurface)

			# PLAYER ROUND STUFF
			if roundStarted:
				# ASSIGN TASK
				if not player.currentTask:
					if activeTasksQueue: # gets a random task from the queue
						task = funks.random.choice(activeTasksQueue)
						player.getTask(task,self)
						activeTasksQueue.remove(task)
			
				else: 	#COMPLETING TASK
					if player.currentTask.passengerVisited and player.currentTask.timeStarted == 0: # starts the task
						player.currentTask.startTask(currentTime) # starts task timer once passenger has been visited.
					
					failed = False
					if player.currentTask.timeStarted != 0: # starts processing the task after it has been started.
						rewards = player.currentTask.checkComplete(currentTime) # checks if task is completed and processes rewards
						if rewards:
							playerEarnedRewards[0] += rewards[0]
							playerEarnedRewards[1] += rewards[1]
							playerTasksCompleted += 1
							player.currentTask.parentNPC.resetTaskData() # removes task from passenger attribute and resets all attrib. relating to it
							totalMistakesMade += player.currentTask.mistakes
							player.currentTask = None
							taskMenu.displayTaskFinished(currentTime)

						elif player.currentTask: # in case (player.currentTask = None) sets to None
							failed = player.currentTask.checkFailed(currentTime) # checks if task was failed and penalises
							if player.currentTask.failed:
								playerEarnedRewards[0] += failed[0]
								playerEarnedRewards[1] += failed[1]
								player.currentTask.parentNPC.resetTaskData() # removes task from passenger attribute and resets all attrib. relating to it
								totalMistakesMade += player.currentTask.mistakes
								player.currentTask = None

					errorMessage = False # checks if an interupt is to be sent to the task menu
					if player.currentTask: # in case (player.currentTask = None) sets to None
						player.currentTask.getInstruction(player,self)
						if isinstance(player.currentTask,keyPressTasks):
							errorMessage = player.currentTask.processTask(keyInputs,player)
						else:
							errorMessage = player.currentTask.processTask(player,self,gameSurface,clickLocations)
					
					taskMenu.changeText(errorMessage,failed,currentTime,player)
			
			#closes game
			if roundProgress >= self.duration: # checks if round has ended, providing rewards and displaying them
				totalRewards = [playerEarnedRewards[0]+workerRewards[0], playerEarnedRewards[1]+workerRewards[1]]
				self.displayRewards(totalRewards,playerEarnedRewards,totalMistakesMade,gameSurface)
				return -1 # kills the loop, returning the game to the airport map.
			# stops it from overworking ig?
			clock.tick(60)
			# idek but needed!
			pygame.display.update()

class Obstruction:
	def __init__(self,columnHeight,blockWidth,topHeight,gapHeight):
		# appart from the coordinates, all measurements here are in terms of tiles, not pxls.
		self.blockWidth = blockWidth # width of the entire column
		self.columnHeight = columnHeight
		self.gapHeight = gapHeight # size of the gap
		self.topHeight = topHeight # height of the top obstruction
		self.bottomHeight = self.columnHeight - (self.gapHeight+self.topHeight) # height of bottom obstruction
		self.coordinates = (constants.screenWidth,0) # top-left coords of the whole pillar.
		self.obstructionSpeed = 250 # speed at which obst approaches player
		self.lastMovedTime = 0 

		self.topPieceFolder = "Overlays/obstructions/cloud"
		self.bottomPieceFolder = "Overlays/obstructions/building"
		self.topPieceTypes = {} # dictionaries of piece name to pyImage
		self.bottomPieceTypes = {}

		for piece in os.listdir(self.topPieceFolder): # gets all piece types and fills up the two dictionaries above
			pieceName = piece[0:-4] # gets the name of the piece
			image = pygame.image.load(self.topPieceFolder+"/"+piece).convert_alpha() # creates pyImage
			self.topPieceTypes[pieceName] = image
			image = pygame.image.load(self.bottomPieceFolder+"/"+piece).convert_alpha()
			self.bottomPieceTypes[pieceName] = image

		self.columnTopPieces = [] # 2D array storing all images forming the entire top block in order
		self.columnBottomPieces = [] # 2D array storing all images forming the entire bottom block in order

	def moveObstruction(self, timePassed): # changes coords according to time and rate so that the block moves up the screen
		if timePassed - self.lastMovedTime >= self.obstructionSpeed:
			self.coordinates = (self.coordinates[0]-16,0)
			self.lastMovedTime = timePassed

	def assemble(self): # sets the values of self.columnTopPieces and self.columnBottomPieces.
		#top
		midBlock = self.blockWidth - 2 # gets the width of the middle part of the block, removing the two outer sides
		for row in range(0,self.topHeight-1):
			rowBlocks = [self.topPieceTypes["leftSide"]]
			rowBlocks.extend([self.topPieceTypes["center"] for i in range(midBlock)]) # avoids needing embedded for loop
			rowBlocks.append(self.topPieceTypes["rightSide"])
			self.columnTopPieces.append(rowBlocks)
		# forms the very last row, which requires the 'top' images.
		rowBlocks = [self.topPieceTypes["topLeft"]]
		rowBlocks.extend([self.topPieceTypes["top"] for i in range(midBlock)])
		rowBlocks.append(self.topPieceTypes["topRight"])
		self.columnTopPieces.append(rowBlocks)

		#bottom
		for row in range(0,self.bottomHeight-1):
			rowBlocks = [self.bottomPieceTypes["leftSide"]]
			rowBlocks.extend([self.bottomPieceTypes["center"] for i in range(midBlock)])
			rowBlocks.append(self.bottomPieceTypes["rightSide"])
			self.columnBottomPieces.append(rowBlocks)
		# forms the very top row, which also requires 'top' images.
		rowBlocks = [self.bottomPieceTypes["topLeft"]]
		rowBlocks.extend([self.bottomPieceTypes["top"] for i in range(midBlock)])
		rowBlocks.append(self.bottomPieceTypes["topRight"])
		self.columnBottomPieces.insert(0,rowBlocks)

	def draw(self,gameSurface,game): # blits all images in the self.columnTopPieces and self.columnBottomPieces onto the gameSurface in order.
		columnHeight = constants.screenHeight//game.trueTileSize
		# TOP
		for row in range(0,self.topHeight):
			for col in range(0,self.blockWidth):
				xCoord = self.coordinates[0] + (col*game.trueTileSize)
				yCoord = self.coordinates[1] + (row*game.trueTileSize) 
				gameSurface.blit(self.columnTopPieces[row][col],(xCoord,yCoord))
		# BOTTOM
		for row in range(0,self.bottomHeight):
			yCoord = (columnHeight - self.bottomHeight + row)*game.trueTileSize
			for col in range(0,self.blockWidth):
				xCoord = self.coordinates[0] + (col*game.trueTileSize)
				gameSurface.blit(self.columnBottomPieces[row][col],(xCoord,yCoord))

class PlayerFlightIcon(Overlay): # for the plane icon in the flight game
	def __init__(self, name, coords, tileSize, scale):
		super().__init__(name,coords,tileSize,scale)
		self.wasColliding = False # flag checking obstruction entry 
		self.speed = 5 # rise and fall of the plane (pxls)
		self.wasInRestrictedZone = False # flag checking obstruction entry 

class Flight: # Flight minigame class
	def __init__(self,prevFactor): # prevFactor is the previous scale factor used by my other two classes.
		self.name = "Flight"
		self.backgroundImages = os.listdir("Clouds")
		self.currentBackground = None # loaded later when screen is created
		self.trueTileSize = constants.tileSize
		self.tileScaleFactor = prevFactor
		self.obstructionSpawnRate = 2000 # 2s
		self.duration = 150000 # 2mins 30s, whole game duration
		self.activeObstructions = [] # all obstructions currently visible.
		self.previousObstruction = None # stores the last obstruction spawned to make sure the next one spawns far enoug away
		self.chances = 5 # num mistakes players can afford to make before game closes

	def resetData(self):# resets all data to default values so there is no intereference when a new round starts
		self.currentBackground = None
		self.obstructionSpawnRate = 2000 # 2s
		self.duration = 150000 # 2mins 30s
		self.activeObstructions = [] 
		self.previousObstruction = None
		self.chances = 5

	def makeSurface(self): # creates the main pygame surface/window
		screenWidth = constants.deviceWidth - (5*self.trueTileSize)
		constants.screenWidth = (screenWidth//self.trueTileSize)*self.trueTileSize
		screenHeight = constants.deviceHeight - (5*self.trueTileSize)
		constants.screenHeight = (screenHeight//self.trueTileSize)*self.trueTileSize
		# imgSize = [576,320]
		surface = pygame.display.set_mode((constants.screenWidth,constants.screenHeight))
		# sets the background image and converts it into a pygame surface scaled to fit the screen window
		self. currentBackground = "Clouds/"+funks.random.choice(self.backgroundImages)
		self.currentBackground = pygame.image.load(self.currentBackground).convert_alpha()
		self.currentBackground = pygame.transform.scale(self.currentBackground,(constants.screenWidth,constants.screenHeight))
		return surface

	def getRewards(self, completed:bool, timePassed, player): # calculates player's rewards depending on the scenario parsed
		if completed:
			coins = (self.chances*10) + 50
			reps = ((self.chances*50) + 100)//2
			return [coins,reps]
		else: # if failed
			coins = (timePassed*2//1000) - (player.level*50)
			reps = (timePassed//500) - (player.level*100)
			return [coins,reps]
	
	def displayRewards(self,rewards,gameSurface, coords): # very similar to cabin minigame
		coins,reps = rewards
		fontSize = 24 # for information texts
		font = pygame.font.Font(None,fontSize)
		coins = "COINs: %d" %(coins)
		reps = "REPUTATION POINTs: %d" %(reps)
		mistakes = "MISTAKEs MADE: %d" %(5 - self.chances)
		texts = [font.render(coins,True,(0,0,0)), # all texts as pygame text objects.
		   		 font.render(reps,True,(0,0,0)),
				 font.render(mistakes,True,(0,0,0))]
		
		xCoord,yCoord = coords
		yCoord += 64 + 4 # cuz the crashed text is roughly 64 px big plus padding
		for i in range(len(texts)): # draws all texts on screen.
			y = yCoord + (4*i) + (fontSize*i)
			gameSurface.blit(texts[i],(xCoord,y))

	def endScreen(self, gameSurface, rewards,completed:bool):
		#gameSurface.fill((15,100,240)), its better without a blank background.
		fontSize = 64 # bigger for the title.
		font = pygame.font.Font(None, fontSize)

		pyText = '' # gets title depending on scenario
		if completed: pyText = font.render("ARRIVED!",True,(0,0,0))
		else: pyText = font.render("CRASHED! GAME OVER", True, (0,0,0))
		xCoord = constants.screenWidth//2 - (pyText.get_width()//2)
		yCoord = constants.screenHeight//2
		gameSurface.blit(pyText,(xCoord,yCoord))
		self.displayRewards(rewards,gameSurface,(xCoord,yCoord)) # blits info texts after title using title coords, much more economical

		pygame.display.update() # refreshes display to ensure that new changes appear before the game loop moves on
		pygame.time.wait(3000) # pauses screen before the game loop is allowed to move on for 3 seconds.

	def startDelay(self,gameSurface):
		fontSize = constants.screenHeight//3 # gets a font size thats large enough, relative to the screen size
		font = pygame.font.Font(None, fontSize)
		for i in range(3,-1,-1):# 3, 2, 1, 0
			text = str(i) # str() data type needed, cant be int
			pyText = font.render(text,True,(0,0,0)) # creates pygame text object so it can be blitted.
			xCoord = (constants.screenWidth//2) - (pyText.get_width()//2)
			gameSurface.blit(pyText,(xCoord,fontSize))
			pygame.display.update() # refreshes the screen
			pygame.time.wait(1000) # holds each number on screen before moving onto the next
			gameSurface.blit(self.currentBackground,(0,0)) # clears the screen so that they don't get drawn on top of each other.

	def spawnObstruction(self): # creates an obstruction object when called and connects it to the game object.
		columnHeight = constants.screenHeight//self.trueTileSize
		columnWidth = funks.random.randint(2,(constants.screenWidth//32)//4)
		gapHeight = funks.random.randint(5,columnHeight//2)
		topSideHeight = funks.random.randint(0,columnHeight-gapHeight)
		obstruction = Obstruction(columnHeight,columnWidth,topSideHeight,gapHeight) # creates obstruction object.
		obstruction.assemble() # called to set the dictionary values.
		self.activeObstructions.append(obstruction) # connects obstruction to game. 
		self.previousObstruction = obstruction # records this obstruction as the last one spawned.

	def gameLoop(self, player):
		gameSurface = self.makeSurface()
		gameSurface.blit(self.currentBackground,(0,0))
		self.spawnObstruction() # allows for one to get added to the list.
		# BAR TRACKERS 
		gameProgressBar = ProgressBar(1*self.tileScaleFactor,
									 constants.timeBarColour,
									 ((constants.screenWidth//self.trueTileSize)- 21,2),
									 self.trueTileSize,
									 10,
									 self.duration) 
		gameProgressBar.setBar()
		healthBar = ProgressBar(1*self.tileScaleFactor,
						  		constants.healthBarColour,
								((constants.screenWidth//self.trueTileSize)- 11,4),
								self.trueTileSize,
								5,
								self.chances) # chances = 5 when this is called so its fine
		healthBar.setBar()

		# PLAYER IMAGE
		playerIcon = PlayerFlightIcon("icons/plane",(constants.screenWidth//96,constants.screenHeight//64),self.trueTileSize,1)
		playerIcon.draw(gameSurface) # just to set the image
		playerIcon.image = pygame.transform.rotate(playerIcon.image,-90) # icon faces up by default, so this turns it to face incoming obstructions

		clock = pygame.time.Clock()
		outOfTheWay = False # flags if block has passed threshold for next spawn countdown to start
		timeOutOfTheWay = 0 # time at which said threshold was passed
		startTime = pygame.time.get_ticks()
		while True:
			currentTime = pygame.time.get_ticks() - 4000 # cuz of startDelay
			timePassed = currentTime - startTime 
			gameSurface.blit(self.currentBackground,(0,0))

			if timePassed == -4000: # at the very beginning of the round, start transition pops up.
				self.startDelay(gameSurface)
			
			upBlocked = False 	# flags to restrict 
			downBlocked = False # player icon movement.

			for event in pygame.event.get():
				if event.type == pygame.QUIT: # closes the game
					pygame.quit()
					sys.exit()

			# BLOCK SPAWN STUFF	
			if self.previousObstruction.coordinates[0] <= constants.screenWidth - (self.previousObstruction.blockWidth*self.trueTileSize)-(2*self.trueTileSize):
				if not outOfTheWay: # ensures that previous obstruction has moved far away enough for another one to spawn in
					timeOutOfTheWay = currentTime
				outOfTheWay = True
			else:
				outOfTheWay = False
			
			if outOfTheWay: # delay for another obstruction to spawn is checked.
				if currentTime - timeOutOfTheWay >= self.obstructionSpawnRate:
					self.spawnObstruction()
					self.obstructionSpawnRate = funks.random.randint(2,5)*1000 	# randomises next spawn time so its not rhythmic	

			# BLOCK FUNCTIONS
			isInRestrictedZone = False
			for block in self.activeObstructions:
				block.draw(gameSurface,self)
				# Checks if player icon is in the x or y range of the obstruction.
				inXRange = block.coordinates[0] <= playerIcon.coords[0] <= block.coordinates[0]+(block.blockWidth*self.trueTileSize)
				inYBlock = block.coordinates[0]-(self.trueTileSize*2) <= playerIcon.coords[0] <= block.coordinates[0]

				if inXRange: # GAP COLLISIONS
					if playerIcon.coords[1] < block.topHeight*self.trueTileSize: # TOP
						upBlocked = True
						isInRestrictedZone = True		
					if playerIcon.coords[1] > (block.columnHeight - block.bottomHeight - 2)*self.trueTileSize: # BOTTOM
						downBlocked = True
						isInRestrictedZone = True
				elif inYBlock: # SIDE COLLISIONS
					if playerIcon.coords[1] < block.topHeight*self.trueTileSize: # TOP
						self.chances = 0
					elif (block.columnHeight-block.bottomHeight)*self.trueTileSize <= playerIcon.coords[1] < block.columnHeight*self.trueTileSize: # BOTTOM
						self.chances = 0 # kills game completely.

				if block.coordinates[0] < -block.blockWidth*self.trueTileSize:
					self.activeObstructions.remove(block) # stops storing obstructions that are no longer visible on screen
				block.moveObstruction(timePassed) # moves obstructions up as they iterate through the for loop.

			#OUT OF BOUNDS, deducts one chance point and stops players from moving out of frame.
			if playerIcon.coords[1]+playerIcon.image.get_height() >= constants.screenHeight:
				downBlocked = True
				isInRestrictedZone = True
			elif playerIcon.coords[1] <= 0:
				upBlocked = True
				isInRestrictedZone = True

			# PLAYER MOVEMENT
			keys = pygame.key.get_pressed()
			if not upBlocked and (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]): # UP
				playerIcon.coords = (playerIcon.coords[0],playerIcon.coords[1] - playerIcon.speed)
			elif not downBlocked and not (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]): # DOWN
				playerIcon.coords = (playerIcon.coords[0],playerIcon.coords[1] + playerIcon.speed - 2)

			# does chance deductions depending on flag values.
			if isInRestrictedZone and not playerIcon.wasInRestrictedZone:
				self.chances -= 1
			playerIcon.wasInRestrictedZone = isInRestrictedZone

			# DRAWS, occur in this order for most logical layering
			playerIcon.draw(gameSurface)
			gameProgressBar.draw(gameSurface)
			gameProgressBar.updateProgress(gameSurface,timePassed)
			healthBar.draw(gameSurface)
			healthBar.updateProgress(gameSurface,self.chances)

			# NO FAIL ENDING
			if timePassed >= self.duration:
				rewards = self.getRewards(True,timePassed, player)
				player.coins += rewards[0]
				player.repPoints += rewards[1]
				self.endScreen(gameSurface,rewards,True)
				return -1
			# FAIL ENDING
			if self.chances == 0:
				rewards = self.getRewards(False,timePassed, player)
				player.coins += rewards[0]
				player.repPoints += rewards[1]
				self.endScreen(gameSurface,rewards,False)
				return-1		
			
			clock.tick(60)
			pygame.display.update()

class Person:
	def __init__(self,name,still,walk): # basic human icon features.
		self.name = name
		self.animations = {'still':still,
						   'walking':walk}
		self.currentAnimation = self.animations['still'][1]
		self.currentTask = ''
		self.lastAnimationTime = 0
		self.lastMovementTime = 0
		
	def resetTimes(self):
		self.lastAnimationTime = 0
		self.lastMovementTime = 0

class Player(Person): # user's class
	def __init__(self, name):
		# for animations.
		still = [500,'Animations/Player/Still/Player 0.png','Animations/Player/Still/Player 1.png']
		walking = [250,'Animations/Player/Walk/Player 0.png','Animations/Player/Walk/Player 1.png']
		super().__init__(name,still,walking)
		self.coordinates = () # stats for gameplay.
		self.level = 0
		self.xp = 0
		self.coins = 250
		self.repPoints = 1000
		self.inventory = []     # name: 'speed', first frame, second frame
		self.crew = [] # the player's workers.
		self.currentTask = None
		
	def levelUp(self):
		neededXP = (self.level*100) + (50*(self.level-3))
		if self.xp >= neededXP:
			self.xp -= neededXP
			self.level += 1

	def getTask(self, task, game): # gives the player a task when called and initialises some of its attributes.
		task.affectTime()
		task.setLocation(game)
		self.currentTask = task

	def drawPerson(self,gameSurface,tileScaleFactor,changeAnimation,animationPack):
		tileSize = tileScaleFactor*constants.tileSize
		if changeAnimation: # animates player with regards to their current actions and time passed.
			if self.currentAnimation == self.animations[animationPack][1]:
				self.currentAnimation = self.animations[animationPack][2]
			else:
				self.currentAnimation = self.animations[animationPack][1]
		scaledPlayerImage = funks.getScaled(self.currentAnimation, tileScaleFactor)
		xCoordinate = ((gameSurface.get_width()//2)//tileSize)*tileSize # always draws player in the middle of the screen
		yCoordinate = (((gameSurface.get_height()//2)//tileSize)*tileSize) - tileSize # raises it by one so draws properly
		gameSurface.blit(scaledPlayerImage, (xCoordinate, yCoordinate))

	# PLAYER MOVEMENT FUNCTIONS
	def moveLeft(self, game):
		nextTile = (self.coordinates[0]-game.trueTileSize,self.coordinates[1])
		if nextTile in game.tilesDict and game.tilesDict[nextTile].walkable:
			self.coordinates = nextTile
	def moveRight(self, game):
		nextTile = (self.coordinates[0]+game.trueTileSize,self.coordinates[1])
		if nextTile in game.tilesDict and game.tilesDict[nextTile].walkable:
			self.coordinates = nextTile
	def moveUp(self, game):
		nextTile = (self.coordinates[0],self.coordinates[1]-game.trueTileSize)
		if nextTile in game.tilesDict and game.tilesDict[nextTile].walkable:
			self.coordinates = nextTile
	def moveDown(self, game):
		nextTile = (self.coordinates[0],self.coordinates[1]+game.trueTileSize)
		if nextTile in game.tilesDict and game.tilesDict[nextTile].walkable:
			self.coordinates = nextTile

	def spawnCrew(self):	# gives the player a set crew, with the number of them depending on player's level
		numStaff = 2 + (self.level//4)
		for i in range(0,numStaff):
			npc = NPCWorker(None,0)
			self.crew.append(npc)

class NPC(Person):
	def __init__(self, coordinates, still, walking):
		super().__init__(funks.getFakeName(),still,walking)
		self.coordinates = coordinates	# coordinate on whole map, not screen
		self.lastCoord = None #remembers prev coord to prevent bopping
		self.pathBlocked = False # flags if a path is actually possible to get to or not.
		self.path = [] # stack of all nodes to traverse through to get to intedned destination.
		self.destination = ()
		self.extraRoute = () # holds extra nodes to walk through that are actually not walkable (for seats destinations)
		self.currentTask = None
		self.infoTitles = []	#contains all the names attributes to be displayed in info box as text
		self.thinking = False # flags thought bubble image animation
		self.bubble = None # will be animatedOverlay("thinkBubble/waiting")

	def getDestination(self, game): # gets the NPC's destination from the game
		if game.freeNPCDestinations:
			self.destination = game.freeNPCDestinations.pop()	#its a coordinate
	
	def isWalking(self, game): # for animation, checks if the NPC is moving or not.
		if self.path:
			nextCoord = self.path[-1]
			if not game.tilesDict[nextCoord].occupied:
				return True
		return False

	def drawPerson(self,game,gameSurface,timePassed): 
		animationPack = 'walking' if self.isWalking(game) else 'still' # checks if player is moving or not to display the right animation
		if timePassed - self.lastAnimationTime >= self.animations[animationPack][0]:
			self.lastAnimationTime = timePassed
			if self.currentAnimation == self.animations[animationPack][1]:
				self.currentAnimation = self.animations[animationPack][2]
			else:
				self.currentAnimation = self.animations[animationPack][1]
		if self.coordinates in game.surfaceCoordinatesDict: # checks if the NPC is actually visible on the surface
			# make image object, rescale image object, recolour image object#
			scaledImage = funks.getScaled(self.currentAnimation, game.tileScaleFactor)
			if self.colour: scaledImage.fill(self.colour, special_flags=pygame.BLEND_MIN)
			gameX, gameY = game.surfaceCoordinatesDict[self.coordinates]
			gameY -= game.trueTileSize # lowers the NPC by 1 block so that the draw is more logical.

			gameSurface.blit(scaledImage, (gameX,gameY))

	def breadthTrav(self, game): # DOES NOT WORK!!!!!!! HAS NOT BEEN IMPLEMENTED
		if not game.tilesDict[self.destination].walkable:
			self.path = []
			return -1

		mapWidth = game.trueTileSize*game.mapSize[0]
		mapHeight = game.trueTileSize*game.mapSize[1]
		queue = funks.qu.Queue()
		start = self.coordinates
		queue.put(start) #start is the current location of NPC
		parents = {start:None}
		visited = set(start)

		step = game.trueTileSize
		directions = [(step, 0),(0,-step),(0,step),(-step,0)]
		found = False
		while not queue.empty() and not found:
			currentX, currentY = queue.get()
			for dirX, dirY in directions:
				newX, newY = dirX + currentX, dirY + currentY
				newCoordinate = (newX, newY)
				
				if newCoordinate == self.destination:
					parents[newCoordinate] = (currentX,currentY)
					self.path = funks.getPath(start, newCoordinate, parents)
					found = True
					return -1
				if 0<=newX<mapWidth and 0<=newY<mapHeight:
					if newCoordinate in game.tilesDict:
						if game.tilesDict[newCoordinate].walkable and not game.tilesDict[newCoordinate].occupied and newCoordinate not in visited:
							queue.put(newCoordinate)
							visited.add(newCoordinate)
							parents[newCoordinate] = (currentX,currentY)
							if newCoordinate == self.destination:
								self.path = funks.getPath(start,newCoordinate,parents)
								found = True
								break

	def AStar(self, game): # Main traversal algorithm.
		# calculates heuristic, g value, and f value according to the A star algo.
		def getNewDists(fScores,gScores,neighbor,current, parent): 
			h = abs(self.destination[0]-neighbor[0])+abs(self.destination[1]-neighbor[1])
			g = gScores[current]+1
			if neighbor not in fScores:
				fScores[neighbor] = h + g
				gScores[neighbor] = g
				parent[neighbor] = current
			else:
				if fScores[neighbor] > h+g:
					fScores[neighbor] = h + g
					gScores[neighbor] = g
					parent[neighbor] = current
				else: return False # means no changes were made
			return True
		
		self.path = [] 	# resets path so that values arent appending to preexisting routes
		self.lastCoord = () # resets the lastCoord incase NPCs need to move to a location behind them
		step = game.trueTileSize # for directions

		# INITIAL PROCESSING
		start = self.coordinates 
		fScores = {start: abs(self.destination[0]-start[0])+abs(self.destination[1]-start[1])}
		gScores = {start:0}
		openList = set()
		closed = set() #stops dups
		parent = {start:None}
		directions = [(step, 0),(0,-step),(0,step),(-step,0)]
		current = start
		openList.add(start)

		while openList:
			lowestDist = float("inf")
			for node in openList: # gets node with lowest f value.
				score = fScores[node]
				if score < lowestDist:
					lowestDist = score
					current = node
				elif score == lowestDist: # if two nodes have the same f value, goes node with lowest h value.
					currentH = abs(self.destination[0]-current[0])+abs(self.destination[1]-current[1])
					nodeH = abs(self.destination[0]-node[0])+abs(self.destination[1]-node[1])
					if nodeH < currentH:
						lowestDist = score
						current = node
			
			if current == self.destination: # checks if the current node is the actual destination to cut the algo short.
				self.path = funks.getPath(self.coordinates,self.destination,parent)
				self.pathBlocked = False
				return -1
			for dirX,dirY in directions: # finds neighboring nodes of the current node, 
				newX,newY = current[0]+dirX,current[1]+dirY
				newCoords = (newX,newY)
				if newCoords in game.tilesDict and newCoords not in closed:# checks if they are actually part of my game map / havent been searched already
					newTile = game.tilesDict[newCoords]
					if newTile.walkable and not newTile.occupied:
						newDists = getNewDists(fScores,gScores,newCoords,current,parent) # calcs distances for new node
						if newDists:
							openList.add(newCoords) # adds to open list.
			
			# if all squares are blocked from the beginning, temp diagonal traversal allowed if possible
			if current == start and len(openList) == 2: # only for the first step, not for all of them
				directions = [(step,-step),(step,step),(-step,step),(-step,-step)] # diagonal steps
				for dirX,dirY in directions:
					newX,newY = current[0]+dirX,current[1]+dirY
				newCoords = (newX,newY)
				if newCoords in game.tilesDict and newCoords not in closed: # same process as before.
					newTile = game.tilesDict[newCoords]
					if newTile.walkable and not newTile.occupied:
						newDists = getNewDists(fScores,gScores,newCoords,current,parent)
						if newDists:
							openList.add(newCoords)
			openList.remove(current)		
			closed.add(current)
		self.pathBlocked = True #  path is not found
		
	def moveNPC(self, game):
		nextCoordinate = self.path[-1]		# peeks. path is a stack
		nextTile = game.tilesDict[nextCoordinate]

	# deals with collisions with other NPCs
		if nextTile.occupied and nextCoordinate != self.coordinates: # because of pause
			self.AStar(game)
			if self.path:
				if funks.random.randint(1,2) == 2: # delays NPCs
					extend = self.coordinates
					for i in range(1,funks.random.randint(2,5)): self.path.append(extend) # 'pauses' the npc randomly to help clear obstructions
			return False
	# stops NPC from backtracking 
		elif nextCoordinate == self.lastCoord:
			if len(self.path) > 1:
				self.path.pop() # simply removes the annoying return from the path
			return False
		
		if nextCoordinate != self.coordinates: # cuz of the pause mechanics!
			self.lastCoord = self.coordinates
		# sets the next coord as the current coord, switching the occupied flags as needed.
		nextCoordinate = self.path.pop() 
		currentTile = game.tilesDict[self.coordinates]
		currentTile.occupied = False
		self.coordinates = nextCoordinate
		game.tilesDict[nextCoordinate].occupied = True
		return True	
	
	def extraMoveNPC(self): # processes the extraRoute attribute of the player if it has been initiated (not all NPCs will have one)
		if self.extraRoute[0] != self.destination: self.destination = self.extraRoute[0]
		self.coordinates = self.extraRoute.pop() # extraRoute is basically a stack as well.

	def getInfo(self): # here as a 'template'. This function is there for my two types of NPC.
		pass

	def drawInfo(self, mouseLocation, gameSurface): # for the white text box UI feature.
			fontSize = 16
			font = pygame.font.Font(None,fontSize)
			texts = self.getInfo() # gets the strings in an array to be processed
			length = len(texts) # for the for loop
			rectHeight = (length*fontSize) + (4*length) #space between each 'item'
			rectWidth = 0 # to be found
			pygameTexts = [] # array of all pygame text objects.
			for i in range(length): # finds width of box depending on size of texts to be added
				text = self.infoTitles[i]+": "+texts[i]
				textPygame = font.render(text,True,(0,0,0))
				pygameTexts.append(textPygame) # pygame texts created and appended to the array
				textW,textH = textPygame.get_size()
				if textW > rectWidth: rectWidth = textW

			rectangle = pygame.Rect(mouseLocation[0], 
						   			mouseLocation[1],
									rectWidth+3, #+3 is padding
									rectHeight) # for the white rectangle background
			pygame.draw.rect(gameSurface,(255,255,255),rectangle)
			
			for i in range(length): # draws the text images on the white box
				yCoord = mouseLocation[1]+(fontSize*i)+(4*i)#4i is padding
				xCoord = mouseLocation[0] + 3 #extra 3 is padding
				gameSurface.blit(pygameTexts[i],(xCoord,yCoord))

	def getBubble(self, game): # changes bubble icon by creating new instance of Overlay object.
		if self.thinking:
			self.bubble = animatedOverlay(
				"thinkBubble/waiting",
				((self.coordinates[0]//32),(self.coordinates[1]//32)-1),
				game.trueTileSize,
				1
			)

class NPCPassenger(NPC): 
	def __init__(self, coordinates, patience):
		# for animations:
		still = [500,'Animations/Passenger/Still/Passenger 0.png','Animations/Passenger/Still/Passenger 1.png']
		walking = [250,'Animations/Passenger/Walk/Passenger 0.png','Animations/Passenger/Walk/Passenger 1.png']
		super().__init__(coordinates,still,walking)
		self.patience = patience # game stat affecting time until task ends
		self.colour = funks.getRandomColour() # gets a random NPC colour
		self.infoTitles = ["name","patience"] #destination is for testing, to be deleted
		self.taskAvailable = False # animates question mark bubble

	def giveTask(self, game):
		if not self.currentTask:	#stops task from changing while still incomplete
			if funks.taskOrNot(): # determines whether or not a task should be given
				task = funks.random.choice([clickTasks(game),keyPressTasks()]) # gets type of task
				task.parentNPC = self # sets some of the task's attributes.
				task.affectTime() # changes time with regards to passenger's patience
				task.setLocation(game) # chosen here because of funks.getNearestAilseCoords
				self.currentTask = task
				self.taskAvailable = True
	
	def resetTaskData(self):
		self.taskAvailable = False
		self.thinking = False
		self.currentTask = None
		self.bubble = None

	def sit(self,game): # changes animation to sitting dependingo on the type of game.
		#sitting animation draws one space too high, this adjusts it.
		newY = self.coordinates[1] + game.trueTileSize
		self.coordinates = (self.coordinates[0],newY)

		root = "Animations/Passenger/Sit" # animation folder name.
		if game.name == "Airport": # determining the file in the folder
			if game.tilesDict[self.destination].function == 'seatBackAirport':
				root += "/airportBack"
			else:
				root += "/airportFront"
		else:
			root += "/airplane"
		frame1 = root+'/0.png'
		frame2 = root+'/1.png'
		self.animations["still"] = [1200,frame1,frame2] # forms current animation pack. Can be replaced since NPC is not gonna get up

	def getInfo(self): #  converts non-string attributes to strings and stores all needed attributes in an array that is returned
		patience = str(self.patience)
		return [self.name,patience]

	def getBubble(self, game): 
		super().getBubble(game)
		if self.taskAvailable:
			self.bubble = animatedOverlay(
				"thinkBubble/questionMark",
				((self.coordinates[0]//32),(self.coordinates[1]//32)-1),
				game.trueTileSize,
				1
			)
			
class NPCWorker(NPC):
	def __init__(self, coordinates, skill):
		self.speed = (skill+1)*500 #need to make them slow so that gameplay logic works out
		still = [self.speed,'Animations/Worker/Still/Worker 0.png','Animations/Worker/Still/Worker 1.png']
		walking = [self.speed//2,'Animations/Worker/Walk/Worker 0.png','Animations/Worker/Walk/Worker 1.png']
		super().__init__(coordinates,still,walking)
		self.skill = skill
		self.colour = None
		self.delay = 0
		self.visiting = True # flags if aStar to passenger has happend
		self.passengerVisited = {"before": False,
						   		 "after": False}
		self.infoTitles = ["name","skill"]
		self.passenger = None

	def getInfo(self):
		skill = str(self.skill)
		return [self.name,skill]
	
	def getTask(self, tasksQueue, game):
		if not self.currentTask:
			self.currentTask = tasksQueue.pop()
			self.delay = self.currentTask.time - (self.skill*10)
			self.passenger = self.currentTask.parentNPC
			self.AStar(game)
	# self.breadthTrav(game), then after reaching the NPC, getDestination() and traverse to task area.

	def visitPassenger(self, game, event):
		if self.visiting:
			self.destination = funks.getNearestAisleCoords(game,self.passenger.coordinates,None)[0]
			self.AStar(game)
			self.visiting = False
		if not self.passengerVisited[event] and self.coordinates == self.destination:
			self.passengerVisited[event] = True
		
	def resetTaskData(self):
		self.passenger.resetTaskData()
		self.passenger = None
		self.visiting = True
		self.passengerVisited["before"] = False
		self.passengerVisited["after"] = False
		self.delay = 0
		self.currentTask = None
		self.bubble = None
		self.thinking = False

	def getDestination(self, game):
		if not self.currentTask:
			coords = ()
			if isinstance(game,Airport):
				coords = [k for k in game.tilesDict if game.tilesDict[k].colour == constants.white]
			else:
				coords = [(x*game.trueTileSize,y*game.trueTileSize) for x in range(27,34) for y in range(13,21) if game.tilesDict[(x*game.trueTileSize,y*game.trueTileSize)].colour == constants.white]
				coords += game.taskWorkSpace
			self.destination = funks.random.choice(coords)
			tile = game.tilesDict[self.destination]
			tile.staffDestination = True
		else:
			if self.destination not in self.currentTask.location:
				availableLocations = [coord for coord in self.currentTask.location if not game.tilesDict[coord].occupied]
				self.destination = funks.random.choice(availableLocations) if availableLocations else self.currentTask.location[0]
				self.AStar(game)
				for i in range(5): self.path.append(self.coordinates) # silly way to make npc 'wait'

	def performTask(self,currentTime):
		self.currentTask.startTask(currentTime)
		self.thinking = True
		if currentTime-self.currentTask.timeStarted >= self.delay:
			self.thinking = False
			self.currentTask.getScore(currentTime)
			rewards = self.currentTask.getRewards()
			self.currentTask = None # breaks that if statement
			return rewards
		return False # if waiting for completion

class Tasks:
	def __init__(self,time,endReq,actionKey):
		self.level = 0 #for now, to change when scalability is formatted.
		self.parentNPC = None	# set later
		self.time = time+(5000*(self.level-1)) #ms
		self.instruction = '' # task's current instruction
		self.endRequirement = endReq	#condition needed to end/complete task
		self.actions = actionKey	#action needed for users to progress task
		self.location = ()	#place at which task completes
		self.progress = 0		# contains progress
		self.timeStarted = 0
		self.score = 0	# used for rewards
		self.mistakes = 0 # used for rewards and displayed as part of total at the end.
		self.passengerVisited = False
		self.failed = False

	def affectTime(self): #  to be determined after parentNPC is found.
		self.time += self.parentNPC.patience*1.5

	def setLocation(self,game): # TASK DESTINATION, not passenger.
		if funks.random.randint(1,2) == 2:
			self.location = game.taskWorkSpace
		else:
			self.location = [funks.getNearestAisleCoords(game,self.parentNPC.coordinates, None)[0]]

	def startTask(self,currentTime): #  sets the start time of the task.
		if self.timeStarted == 0:
			self.timeStarted = currentTime

	def timeLeft(self, currentTime): # finds out how much time is left until task ends
		if not self.timeStarted:
			return "--:--"
		msLeft = self.time - (currentTime - self.timeStarted) # converting to 00:00.0 format
		secondsLeft = msLeft//1000
		minutesLeft = secondsLeft//60
		secondsLeft = str(secondsLeft - (minutesLeft*60))
		if len(secondsLeft) == 1:
			secondsLeft = "0"+secondsLeft
		return str(minutesLeft)+":"+secondsLeft
	
	def checkFailed(self, currentTime): # returns True if failed and False if not
		if currentTime - self.timeStarted >= self.time:
			self.failed = True
			return self.getRewards()
		return False
	
	def checkComplete(self, currentTime): 
		if self.progress >= self.endRequirement:# checks if all presses/clicks have occurred correctly
			self.getScore(currentTime) 
			return self.getRewards(currentTime) # fetches and returns rewards.
		else:
			return False

	def getScore(self, currentTime): 
		timeLeft = currentTime - self.timeStarted
		self.score = self.endRequirement + int(0.5*(self.endRequirement*timeLeft)/1000)
		self.score -= 100*self.mistakes

	def	getRewards(self,currentTime):
		if not self.failed:
			self.getScore(currentTime) # sets score
			coins = (10*(self.level+1)) - 5
			reps = 100*(self.level) + (self.score*5)	# for now, calcs can be changed later
			return [coins,reps]
		else:
			return [0,-50*(5-self.level)]	# you lose more rep points for failing an easy task

class keyPressTasks(Tasks):
	def __init__(self):
		presses = funks.random.randint(3,6) #  determines number of presses to do
		super().__init__(20000, # duration
				   presses,
				   funks.random.choices(constants.allInputKeys, k=presses), # uses random function to choose k amount of keys to press
				   )
		self.instruction = "" 
	
	def getInstruction(self,player,game):
		# Finds the correct instruction depending on scenario
		if not self.passengerVisited or len(self.location) == 1: 
			self.instruction = "Go to passenger, "+ self.parentNPC.name
			if not self.passengerVisited and player.coordinates == funks.getNearestAisleCoords(game,self.parentNPC.coordinates,None)[0]:
				self.passengerVisited = True
		elif len(self.location) > 1:
			self.instruction = "Go to galley!"
		else:
			self.instruction = ""
		
		# instructions for task start and progression
		if player.coordinates in self.location and self.passengerVisited:
			if not self.actions:
				self.instruction = ""
				return False
			currentKeyNumber = self.actions[-1]
			keyWord = ''
			if currentKeyNumber == pygame.K_SPACE: keyWord = "SPACE"
			else:
				index = currentKeyNumber - 97
				keyWord = constants.letters[index]
			self.instruction = "Press the "+keyWord.upper()+" key!   num left: %d" %(self.endRequirement-self.progress)
	
	def processTask(self, inputs, player):
		textChange = False # for errorMessage flag in game loop
		if player.coordinates in self.location and self.passengerVisited:
			for key in inputs: # there should only be one but just in case
				if key not in constants.movementKeys:
					if key == self.actions[-1]:
						self.instruction = "Correct!"
						self.progress += 1
						self.actions.pop() # moves on to next instruction
						textChange = True
						self.time += 1000 # because of pause when interupt displays
					else:
						self.instruction = "Wrong key! Try again!"
						self.mistakes += 1 # penalises
						textChange = True
						self.time += 1000 # because of pause when interupt displays
		return textChange

class clickTasks(Tasks):
	def __init__(self, game):		
		super().__init__(20000, # duration
				   		funks.random.randint(3,5), # number of times images need to be clicked.
						pygame.MOUSEBUTTONDOWN, # there is only one type of key to press; not rlly relevant as inputs are gathered in gameloop anyway
						)
		self.imageDisplayCoordinate = funks.getScreenPosition() # gets a random screen coordinate
		self.imageDisplayCoordinate = (self.imageDisplayCoordinate[0]//game.trueTileSize,self.imageDisplayCoordinate[1]//game.trueTileSize) # for overlay
		self.imagesDisplayed = 0 # counter
		self.images = os.listdir("Overlays/icons") # folder name for icons to be displayed
		self.currentImage = funks.random.choice(self.images)[:-4] # chooses the file, but gets rid of the file extension
		self.currentOverlayObject = '' # to be determined
		self.instruction = "Click the image!"
		#self.location = taskWorkSpace.... can be anywhere in this space

	def getInstruction(self,player,game):
		if not self.passengerVisited or len(self.location) == 1: # same as before.
			self.instruction = "Go to passenger, "+ self.parentNPC.name
			if not self.passengerVisited and player.coordinates == funks.getNearestAisleCoords(game,self.parentNPC.coordinates,None)[0]:
				self.passengerVisited = True
		elif len(self.location) > 1:
			self.instruction = "Go to galley!"
		else:
			self.instruction = ""

		if player.coordinates in self.location and self.passengerVisited:
			self.instruction = "Click the icons that appear!   num left: %d" %(self.endRequirement-self.progress)


	def displayImage(self,game,gameSurface): # creates Overlay object for the image and borrows its draw function.
		self.currentOverlayObject = Overlay("icons/"+self.currentImage,self.imageDisplayCoordinate,game.trueTileSize,1*game.tileScaleFactor)
		self.currentOverlayObject.draw(gameSurface)

	def changeCoords(self,game): # randomises the icon coordinates so that they do not get drawn in the same place.
		self.imageDisplayCoordinate = funks.getScreenPosition()
		self.imageDisplayCoordinate = (self.imageDisplayCoordinate[0]//game.trueTileSize,self.imageDisplayCoordinate[1]//game.trueTileSize)

	def processTask(self,player,game,gameSurface,clicks):
		if player.coordinates in self.location and self.passengerVisited:
			self.displayImage(game,gameSurface) # draws image when player is in the right place
			for click in clicks: # if statements check if click location is on the image
				if self.imageDisplayCoordinate[0]*game.trueTileSize <= click[0] <= (self.imageDisplayCoordinate[0]*game.trueTileSize)+(self.currentOverlayObject.image.get_width()*self.currentOverlayObject.scale):
					if self.imageDisplayCoordinate[1]*game.trueTileSize <= click[1] <= (self.imageDisplayCoordinate[1]*game.trueTileSize)+(self.currentOverlayObject.image.get_height()*self.currentOverlayObject.scale):
						self.progress += 1
						self.currentImage = funks.random.choice(self.images)[:-4]
						self.changeCoords(game)
				else:
					self.instruction = "Clicked the wrong place!"
					self.mistakes += 1
					self.time += 1500
					return True # for errorMessage
