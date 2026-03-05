import pygame
import classes
import extraFunctions as funks

pygame.init()

# CREATING ALL CLASS OBJECTS
airport = classes.Airport("Airport", [40,25])
cabin = classes.Cabin("Airplane", [65,66])
flight = classes.Flight(airport.tileScaleFactor)
player = classes.Player("Taco")
player.spawnCrew()

# START SCREEN
start = classes.startScreen()
start.loop() # loop for start screen. Once button clicked, it moves onto the central game loop.

# CENTRAL GAME LOOP
while True:
    airport.gameLoop(player) # starts at airport map
    if funks.chooseGameMode() == "flight": # Chooses game mode
        flight.gameLoop(player)
        flight.resetData()
    else:
        cabin.gameLoop(player)
    # once the minigame ends, loop recycles to the airport map...
        