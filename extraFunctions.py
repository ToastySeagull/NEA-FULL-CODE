import constants
import random
import pygame
from faker import Faker
import queue as qu

fake = Faker()

def getScaled(imageFile, scaleFactor): 
    loadedImage = pygame.image.load(imageFile).convert_alpha() # converts image to a pygame image
    scaledImage = pygame.transform.scale(loadedImage, (loadedImage.get_width()*scaleFactor,loadedImage.get_height()*scaleFactor))# scales image evenly by a given scale factor
    return scaledImage

def chooseGameMode(): # selects minigame that loads in
    num = random.randint(1,2)
    return "cabin" if num == 2 else "flight"

def getFakeName(): # gets NPC names
    return fake.name()

def getPatience(): # selects patience level of passengers
    return random.randrange(600,3000,100)

def getRandomColour(): # finds a colour for NPCs
    num = random.randint(0,len(constants.npcColours)-1)
    return constants.npcColours[num] + (0,)

def getPath(start, end, pathDict): # reorders the path from traversal algos so that they are compatible with stack 'functions'
    current = end
    pathStack = []          #TO BE USED AS A STACK, lifo object is not good cuz cant peek
    pathStack.append(current)
    while current != start:
        prev = pathDict[current]
        pathStack.append(prev)
        current = prev
    pathStack.pop() #npc is already at start so no need for it in path.
    return pathStack

def taskOrNot(): # determines whether passenger should provide task or not
    checker = random.randint(1,30)
    if checker%10 == 0:
        return True
    return False

def getLettersKey(num): # converts pygame letter codes to its letter string
    if num == 32: return "space"
    num = num-97
    return constants.letters[num]

def getNearestAisleCoords(game, npcCoord,side): # finds nearest walkable tile on the same y axis coord.
    directions = [] # the side parameter aims to speed up this process.
    count = 1
    if side == "right" or not side:
        directions = [game.trueTileSize,-game.trueTileSize]
    else:
        directions = [-game.trueTileSize,game.trueTileSize]
    dirIndex = 0
    previous = [npcCoord]
    while dirIndex < 2: # >2 means that both sides of the destination have been checked and no path has been found
        newX,newY = (count*directions[dirIndex])+npcCoord[0],npcCoord[1] 
        newCoord = (newX,newY)
        if newCoord in game.tilesDict:
            count += 1
            previous.append(newCoord)
            if game.tilesDict[newCoord].walkable:
                return [newCoord,previous] # returns the closest walkable tile coordinate and the path from the actual destination to it.
        else:
            dirIndex += 1 # if the current coordinates arent in the tilesDict, the algorithm has progressed too far to one side, so the side switches
            previous = [npcCoord]
            count = 1
    return [npcCoord,[]]


def getScreenPosition():
    x = random.randint(0,constants.screenWidth-64)
    y = random.randint(0,constants.screenHeight-64)
    return (x,y)
    
 
