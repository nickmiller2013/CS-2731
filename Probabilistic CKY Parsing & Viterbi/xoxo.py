import os
#def addToMatrix(matrix, xoro):

import re
import numpy as np

#def getInput(matrix, input):







def playGame():
    theMap = np.zeros((3,3))
    theMap[1][1] = 1
    print theMap

play = "Yes"
k = 1
while play == "Yes":
    playGame()
    print play
    play = str(input("Would you like to play a game Again?? (Yes or No): "))
