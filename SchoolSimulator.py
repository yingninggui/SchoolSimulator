#
#ICS3U1-03, Mr.Cope
#

#
#

#
#

#import needs 
import pygame
from pygame.locals import *
import pickle
import random

#intialize display 
pygame.init()
screenX = 1024
screenY = 768
screen = pygame.display.set_mode((screenX,screenY)) #screen resolution 
clock = pygame.time.Clock()
pygame.mixer.init()


#============================================================#  
#Classes
#============================================================#

class player:

    def __init__(self, name, money, level, score, profession, studentMaxNum, teacherMaxNum):

        self.name = name    #initializes a player with values given
        self.money = money
        self.oldMoney = money
        self.level = level
        self.profession = profession
        self.studentMaxNum = studentMaxNum
        self.teacherMaxNum = teacherMaxNum
        
        self.score = 0      #initial constants
        self.dayNum = 1
        self.speedMulti = 1
        self.moneyMulti = 1
        self.gradeAdd = 0
        self.happinessAdd = 0
        self.clickMulti = 0.1
        self.buildMulti = 1
        self.timeAdd = 0

    def newDay(self):                       #end of each day

        self.dayNum += 1                    #progress
        profit = self.money - self.oldMoney #calculates net profit / net loss
        self.oldMoney = self.money
        return profit

    def recheck(self, gameBoard):           #because each facility has a special statistic unique to its type (aka money multiplier),
                                            #the "net multiplier" for the player must be recounted
        self.studentMaxNum = 5              #reset values
        self.moneyMulti = 1                 #reset moneyMulti
        self.speedMulti = 1                 #reset speedMulti
        self.gradeAdd = 0                   #reset gradeAdd
        self.happinessAdd = 0               #reset happinessAdd
        self.clickMulti = 0.1               #reset clickMulti
        self.buildMulti = 1                 #reset buildMulti
        self.timeAdd = 0                    #reset timeAdd
        for x in range(0, gameBoard.columns):                               #gets individual facility names for entire school
            for y in range(0, gameBoard.rows):
                facName = gameBoard.facArray[x][y].name
                if facName == "cafeteria":                                  #if the facility is a certain type, its special statistic
                    self.studentMaxNum += gameBoard.facArray[x][y].special  #is used to recalculate its "net multiplier"
                if facName == "gym":
                    self.speedMulti *= gameBoard.facArray[x][y].special
                if facName == "math":
                    self.moneyMulti *= gameBoard.facArray[x][y].special
                if facName == "computer science":
                    self.clickMulti *= gameBoard.facArray[x][y].special
                if facName == "physics":
                    self.buildMulti *= gameBoard.facArray[x][y].special
                if facName == "art":
                    self.happinessAdd += gameBoard.facArray[x][y].special
                if facName == "chemistry":
                    self.gradeAdd += gameBoard.facArray[x][y].special
                if facName == "english":
                    self.timeAdd += gameBoard.facArray[x][y].special
                    
                

class facility:

    def __init__(self, name, cost, happinessLevel, grade, maxStudents, special, earningSpeed):
        
        self.name = name                    #initializes player with values given
        self.cost = cost
        self.happinessLevel = happinessLevel
        self.grade = grade
        self.maxStudents = maxStudents
        self.earningSpeed = earningSpeed
        self.special = special
        self.upgradeCost = int(self.cost / 10)

        self.level = 0                      #initial constants
        self.cStudents = 0


    def levelUp(self):                      #if upgraded, update facility's stats
        
        self.level += 1
        self.earningSpeed *= 1.05
        self.upgradeCost *= 1.8
        if self.level == 10:                #level 10 special bonus!
            self.earningSpeed *= 2

        if self.name == "cafeteria":        #facility's special statistic progresses at different rates
            self.special += 1
        if self.name == "gym":
            self.special *= 1.01
        if self.name == "math":
            self.special *= 1.01
        if self.name == "computer science":
            self.special *= 1.02
        if self.name == "physics":
            self.special *= 1.01
        if self.name == "art":
            self.special += 0.01
        if self.name == "chemistry":
            self.special += 0.01
        if self.name == "english":
            self.special += 25
        
class gameBoard:

    def __init__(self, columns, rows, x, y, zoom):
        
        self.columns = columns          #initialize the school (game board) with the values given
        self.rows = rows
        self.x = x
        self.y = y
        self.zoom = zoom
        
        self.dx = 0                     #constants
        self. dy = 0
        self.totalFacilities = 0
        self.totalHappiness = 0
        self.averageGrade = 0
        self.costConstant = 1
        self.facArray = []              #array that contains all the facilities based on x and y location
        self.studentList = []
        empty = facility("empty", 0, 0, 0, 0, 0, 0)
        for i in range(0, columns):     #this creates the school with empty facilities
            self.facArray += [[empty]*rows]


    def update(self):   #remakes the school surface ready for bliting
        """
        remakes the school surface ready for bliting
        every value is proportional to zoom, to allow for simple resizing
        """
        
        boardSurface = pygame.Surface((self.columns*self.zoom, self.rows*self.zoom))                                            #creates the entire school board
        pygame.draw.rect(boardSurface, (255, 255, 255), (0, 0, self.columns*self.zoom, self.rows*self.zoom), 0)                 #draws interior
        pygame.draw.rect(boardSurface, (128, 0, 128), (0, 0, self.columns*self.zoom, self.rows*self.zoom), int(self.zoom*0.4))  #draws exterior/border
        pygame.draw.rect(boardSurface, (0, 0, 0), (0, int(self.zoom*0.8), int(self.zoom*0.2), int(self.zoom*0.4)), 0)           #draws door
        for x in range(0, self.columns):
            for y in range(0, self.rows):                                                                                       #draws each individual facility
                facSurface = pygame.image.load("images\\classroom.png").convert_alpha()                                                 #orange background for facility
                facility = pygame.image.load("images\\%s.png" %self.facArray[x][y].name).convert_alpha()                                #facility's icon
                xPos = int((facSurface.get_width() - facility.get_width())/2)                                                   #centre the icon
                yPos = int((facSurface.get_height() - facility.get_height())/2)                                                 #center the icon continued
                facSurface.blit(facility, (xPos, yPos))                                                                         #blit the icon onto the facility
                facSurface = pygame.transform.scale(facSurface, (int(self.zoom*0.8), int(self.zoom*0.8)))                       #resize the facility to put on school
                boardSurface.blit(facSurface, (int((x+0.1)*self.zoom), int((y+0.1)*self.zoom)))                                 #facility is blit onto the school surface
        self.surface = boardSurface                                         #store the new surface
        self.length = boardSurface.get_width()                              #length of surface for centering and input-receiving reasons

        
    def addFac(self, x, y, facilityType, player):   #if the player chooses to build a facility, the school is updated

        if self.facArray[x][y].name == "empty":     #classroom is only built if the spot is empty
            self.totalFacilities += 1
            self.facArray[x][y] = facility(facilityType.name, facilityType.cost, facilityType.happinessLevel, facilityType.grade, facilityType.maxStudents, facilityType.special, facilityType.earningSpeed)
            self.update()                   #remake the school surface
    
                                            #built facility will change happiness and grade stats
        totalHappiness = 0                  #total happiness is reset
        totalGrade = 0                      #total grade is reset
        for x in range(0, self.columns):    
            for y in range(0, self.rows):                               #access each inidivual facility
                totalHappiness += self.facArray[x][y].happinessLevel    #adds to totals
                totalGrade += self.facArray[x][y].grade
        if totalHappiness < 0:              #prevents happiness from becoming negative
            totalHappiness = 0
        if totalHappiness > 1:
            totalHappiness = 1              #prevents happiness from becoming greater than 1
        if self.totalFacilities != 0:       #grade is only calculated if there is at least 1 facility to prevent divison by 0
            averageGrade = totalGrade/self.totalFacilities
        else:
            averageGrade = 0
        self.totalHappiness = totalHappiness + player.happinessAdd
        self.averageGrade = averageGrade + player.gradeAdd
        


    def deleteFac(self, x, y, facility, player):    #deletes a facility and returns the player some money

        player.money += self.facArray[x][y].cost*0.7
        self.facArray[x][y] = facility
        self.update()
        self.totalFacilities -= 1
                

    def expand(self, extraX, extraY, zoom):         #expands the school with more rooms

        newArray = []                               #new array to contain facilities
        empty = facility("empty", 0, 0, 0, 0, 0, 0)
        for i in range(0, self.columns + extraX):   #initializes the new array with empty facilities
            newArray += [[empty]*(self.rows + extraY)]
        for x in range(0, self.columns):            #takes the old facilities and puts them into the new school
            for y in range(0, self.rows):
                newArray[x][y] = self.facArray[x][y]
        self.facArray = newArray                    #new facility array is stored
        self.columns += extraX                      #num of columns updated
        self.rows += extraY                         #num of rows updated
        self.zoom = zoom                            #resize school
        self.update()                               #remake school surface
        self.centre(1024)                           #centre the surface

            
    def earnGuap(self, player):                     #function for earning the player money and score for each passing second

        for x in range(0, self.columns):
            for y in range(0, self.rows):
                eps = int(self.facArray[x][y].earningSpeed*self.facArray[x][y].cStudents*(self.totalHappiness + 0.1)*(self.averageGrade + 0.1)*player.moneyMulti)   #access each individual facility and
                player.money += eps                                                                                                                                 #calculates money and score earned
                player.score += eps                                                                                                                                 #based off the the given algorithm
                
    def clickGuap(self, player):                    #function for earning the player money and score for clicking the money button

        for x in range(0, self.columns):
            for y in range(0, self.rows):
                eps = int(self.facArray[x][y].earningSpeed*self.facArray[x][y].cStudents*(self.totalHappiness + 0.1)*(self.averageGrade + 0.1)*player.moneyMulti*player.clickMulti)
                player.money += eps
                player.score += eps
    def centre(self, screenX):                      #centres the gameBoard

        self.x = int((screenX-self.length)/2)

    def check(self, mouseX, mouseY):                #takes the mouse position and returns the facility location the mouse is currently on

        relativeX = (mouseX - self.x)//self.zoom    #x and y coordinate, relative to the gameboard
        relativeY = (mouseY - self.y)//self.zoom
        return relativeX, relativeY

    def addStudents(self, x, y):                    #display student bar of certain facility

        cFacility = self.facArray[x][y]
        studentsNum = button(int(self.zoom*0.5*cFacility.cStudents/cFacility.maxStudents), int(self.zoom*0.1), 0, (0, 255, 0), self.zoom*(x+0.26) + self.x, self.zoom*(y+0.2) + self.y)
        return studentsNum
                

class student:

    def __init__(self, zoom, xNum, yNum, gameBoard, speedMulti):    #initialize a student with given values

        self.zoom = zoom
        self.xNum = xNum
        self.yNum = yNum
        self.x = gameBoard.zoom* 0.2 + gameBoard.x
        self.y = gameBoard.zoom*0.9 + gameBoard.y
        self.dx = 0                                                 #change in x position
        self.dy = 0                                                 #change in y position
        self.speed = random.randint(70, 130)/100*speedMulti         #students are generated with varying speeds
        self.surface = pygame.Surface((self.zoom/10, self.zoom/10))
        self.surface.fill((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        self.arrival = False
        self.counted = False

    def move(self, rows):               #student moves a certain amount based off of speed
        if self.yNum == 0:              #if classroom is the first row, perform the following movements
            if self.dx <= self.zoom*(self.xNum+0.2):
                self.dx += self.speed
            elif self.dy >= self.zoom*(-0.19):
                self.dy -= self.speed
            else:
                self.arrival = True
        
        else:                           #if classroom is not the first row, perform the following movements
            if self.dx <= self.zoom*0.8 and self.dy <= self.zoom*(self.yNum-1):
                self.dx += self.speed
                
            elif self.dy <= self.zoom*(self.yNum-1):
                self.dy += self.speed
                
            elif self.xNum != 0:
                if self.dx <= self.zoom*(self.xNum+0.2):
                    self.dx += self.speed
                elif self.dy <= self.zoom*(self.yNum-0.7):
                    self.dy += self.speed
                else:
                    self.arrival = True                  

            elif self.xNum == 0:        #special case where classroom is at bottom left corner
                if self.dx >= self.zoom*(self.xNum+0.2):
                    self.dx -= self.speed
                elif self.dy <= self.zoom*(self.yNum-0.7):
                    self.dy += self.speed
                else:
                    self.arrival = True    


class button:

    def __init__(self, length, width, border, colour, x, y):    #initiate a button with given values
        self.length = length
        self.width = width
        self.border = border
        self.colour = colour
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.rect = Rect(self.x, self.y, self.length, self.width)
        self.surface = pygame.Surface((self.length, self.width))
        pygame.draw.rect(self.surface, self.colour, (0, 0, self.length, self.width), border)
        
    def check(self, mouseX, mouseY):                            #checks if button has been clicked, returns boolean

        if (mouseX > self.rect.topleft[0]) and (mouseY > self.rect.topleft[1]) and (mouseX < self.rect.bottomright[0]) and (mouseY < self.rect.bottomright[1]):
            return True
        else:
            return False
        
    def centre(self, screenX):                                  #centres button 
        
        self.x = int((screenX-self.length)/2)
        self.rect = Rect(self.x, self.y, self.length, self.width)

    def update(self):                                           #creates the button rectangle and surface for bliting
        self.rect = Rect(self.x, self.y, self.length, self.width)
        self.surface = pygame.Surface((self.length, self.width))
        pygame.draw.rect(self.surface, self.colour, (0, 0, self.length, self.width), self.border)

    def addText(self, text):                                    #adds text to the button
        x = int((self.length-text.length)/2)                    #text us automatically centred in the button
        y = int((self.width-text.width)/2)                      #and blit onto the button's surface
        self.surface.blit(text.surface, (x,y))
        
class text:

    def __init__(self, text, font, size, colour, x, y):     #creates a button with the given values
        self.text = text
        self.font = font
        self.size = size
        self.colour = colour
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        my_font = pygame.font.Font("%s" %font, size)    #renders the font and creates the surface
        self.surface = my_font.render("%s" %text, False, (colour)).convert_alpha()
        self.length = self.surface.get_width()

    def centre(self, screenX):                          #centres the text in a field of screenX
        self.x = int((screenX-self.length)/2)

    def update(self):                                   #recreates the text surface (useful when text values change)
        my_font = pygame.font.Font("%s" %self.font, self.size)
        self.surface = my_font.render("%s" %self.text, False, (self.colour)).convert_alpha()
        self.length = self.surface.get_width()
        self.width = self.surface.get_height()

class image:
                     
    def __init__(self, name, x, y):                     #creates ain image with the given values
        self.name = name
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.surface = pygame.image.load("images\\%s" %name).convert_alpha()
        self.length = self.surface.get_width()

    def centre(self, screenX):                          #centres the image in a field of screenX
        self.x = int((screenX-self.length)/2)

class display:                                          #display is the combination of different objects like images, buttons, and text

    def __init__(self, objectList, bList):      #each object is accessible using a list
        self.objectList = objectList
        self.bList = bList

    def initiate(self):                         #blits the display onto the screen aka switches the screen
        for items in self.objectList:
            screen.blit(items.surface, (items.x + items.dx, items.y + items.dy))

def save(obj, name):                    #saves any object into given file name

    pickle_out = open("%s" %name, "wb") #start a pickle file, must write in binary
    pickle.dump(obj, pickle_out)        #pickles p1 object into save1 file
    pickle_out.close()                  #close the file

def load(name):

    pickle_in = open("%s" %name, "rb")  #open save1
    obj = pickle.load(pickle_in)        #unpickle save1 into p2
    pickle_in.close()
    return obj


def initiate(objectList):               #for bliting a list of objects
    for items in objectList:
        screen.blit(items.surface, (items.x + items.dx, items.y + items.dy))

def scroll(objectList, obj):            #for scrolling a specific object (only used for background)
        objectList[obj].dy -= 1
        if objectList[obj].dy <= -64:   #fake scrolling, resets after scrolling 64 pixels
            objectList[obj].dy = 0


"""
=============================================================
CONFIG
=============================================================
"""
            
#============================================================#  
#Facilities: self, name, cost, happinessLevel, grade, maxStudents, special, earningSpeed
#============================================================#
empty = facility("empty", 0, 0, 0, 0, 0, 0)
physicsFac = facility("physics", 15000, 0.05, 0.80, 3, 1.05, 300)
chemistryFac = facility("chemistry", 20000, 0, 0.85, 3, 0.02, 200)
cafFac = facility("cafeteria", 10000, 0, 0.5, 8, 10, 20)
englishFac = facility("english", 10000, -0.1, 0.75, 3, 100, 250)
mathFac = facility("math", 18000, -0.4, 0.90, 4, 1.05, 300)
comsciFac = facility("computer science", 30000, +0.1, 0.75, 3, 1.1, 430)
artFac = facility("art", 10000, 0.2, 0.65, 4, 0.02, 25)
gymFac = facility("gym", 8000, +0.4, 0.45, 5, 1.05, 100)

facTypes = [physicsFac, chemistryFac, englishFac, gymFac, mathFac, comsciFac, cafFac, artFac]

#============================================================#   
#Loading Screen
#============================================================#
#Buttons
loadingButton = button(1024, 768, 0, (0,0,0), 0, 0)

#Images
background = image("home bg.png", 0, 0)
logo = image("logo.bmp", 0, 180)
logo.centre(1024)

#Text
title = text("SCHOOL SIMULATOR", "DTM-Sans.otf", 65, (255, 255, 255), 0, 50)
title.centre(1024)
text1 = text("WELCOME, PLAYER", "DTM-Sans.otf", 35, (255, 255, 255), 0, 450)
text1.centre(1024)
text2 = text("Press any key to continue", "DTM-Sans.otf", 35, (255, 255, 255), 0, 500)
text2.centre(1024)

loadingObj = [background, logo, title, text1, text2]

#============================================================#
#Menu Screen
#============================================================#
#Buttons
newGameButton = button(300, 45, 10, (255,255,255), 0, 200)
newGameButton.centre(1024)
oldGameButton = button(300, 45, 10, (255,255,255), 0, 260)
oldGameButton.centre(1024)
helpButton = button(300, 45, 10, (255,255,255), 0, 320)
helpButton.centre(1024)
settingsButton = button(300, 45, 10, (255,255,255), 0, 380)
settingsButton.centre(1024)
creditsButton = button(300, 45, 10, (255,255,255), 0, 440)
creditsButton.centre(1024)
quitButton = button(300, 45, 10, (255,255,255), 0, 500)
quitButton.centre(1024)

#Images
background = image("home bg.png", 0, 0)
menuBox = button(450, 500, 30, (255,255,255), 0, 100)
menuBox.centre(1024)

#Text
title = text("MENU OPTIONS", "DTM-Sans.otf", 45, (255, 255, 255), 0, 130)
title.centre(1024)
text1 = text("- NEW GAME -", "DTM-Sans.otf", 35, (255, 255, 255), 0, 200)
text1.centre(1024)
text2 = text("- LOAD PREVIOUS GAME -", "DTM-Sans.otf", 35, (255, 255, 255), 0, 260)
text2.centre(1024)
text3 = text("- HELP -", "DTM-Sans.otf", 35, (255, 255, 255), 0, 320)
text3.centre(1024)
text4 = text("- SETTINGS -", "DTM-Sans.otf", 35, (255, 255, 255), 0, 380)
text4.centre(1024)
text5 = text("- CREDITS -", "DTM-Sans.otf", 35, (255, 255, 255), 0, 440)
text5.centre(1024)
text6 = text("- QUIT -", "DTM-Sans.otf", 35, (255, 255, 255), 0, 500)
text6.centre(1024)


menuObj = [background, menuBox, title, text1, text2, text3, text4, text5, text6]
menuButtons = [newGameButton, oldGameButton, helpButton, settingsButton, creditsButton, quitButton]

#============================================================#
#New Game Screen
#============================================================#
#Buttons
writingButton = button(400, 50, 10, (255,255,255), 400, 434)
backButton = button(100, 30, 10, (255,255,255), 397, 518)
nextButton = button(100, 30, 10, (255,255,255), 522, 518)

#Images
background = image("home bg.png", 0, 0)
foreground = image("CharacterCreation.png", 0, 0)

#Text
name = text("", "DTM-Sans.otf", 35, (255, 255, 255), 424, 440)
noNameText = text("Invalid name!", "DTM-Sans.otf", 35, (255, 255, 255), 0, 640)
noNameText.centre(1024)

newGameObj = [background, foreground, name]
newGameButtons = [writingButton, backButton, nextButton]

#============================================================#
#jobs
#============================================================#
#buttons  self, length, width, border, colour, x, y):
mathButton = button(90, 100, 10, (255,255,255), 247, 267)
physicsButton = button(90, 100, 10, (255,255,255), 391, 262)
chemistButton = button(90, 100, 10, (255,255,255), 541, 267)
programmerButton = button(90, 100, 10, (255,255,255), 686, 265)
writerButton = button(90, 100, 10, (255,255,255), 247, 405)
biologistButton = button(90, 100, 10, (255,255,255), 380, 400)
athleteButton = button(90, 100, 10, (255,255,255), 530, 400)
artistButton = button(90, 100, 10, (255,255,255), 686, 400)
backButton = button(100, 30, 0, (0, 0, 0), 397, 532)
backButtonText = text("< BACK", "DTM-Sans.otf", 35, (255, 255, 255), 0, 500)
backButtonText.update()
backButton.addText(backButtonText)
nextButton = button(100, 30, 0, (0, 0, 0), 522, 532)
nextButtonText = text("NEXT >", "DTM-Sans.otf", 35, (255, 255, 255), 0, 500)
nextButtonText.update()
nextButton.addText(nextButtonText)
selection = button(0, 0, 0, (0, 0, 0), 0, 0)
border = button(650, 450, 20, (255, 255, 255), 0, 150)
border.centre(1024)

#images
background = image("home bg.png", 0, 0)
math = image("math.png", 225, 250)
physics = image("physics.png", 372, 250)
chemistry = image("chemistry.png", 519, 250)
compsci = image("computer science.png", 666, 245)
english = image("english.png", 230, 400)
biology = image("biology.png", 377, 400)
gym = image("gym.png", 524, 390)
art = image("art.png", 671, 375)

#text
title = text("CHOOSE YOUR PROFESSION", "DTM-Sans.otf", 45, (255, 255, 255), 0, 170)
title.centre(1024)


jobsObj = [background, border, title, selection, nextButton, backButton, math, physics, chemistry, compsci, english, biology, gym, art]
jobsButtons = [mathButton, physicsButton, chemistButton, programmerButton, writerButton, biologistButton, athleteButton, artistButton, backButton, nextButton]



#============================================================#
#Tutorial
#============================================================#
#Buttons
backButton = button(100, 50, 10, (255,255,255), 397, 518)
nextButton = button(100, 50, 10, (255,255,255), 522, 518)

#Images
background = image("home bg.png", 0, 0)
foreground1 = image("Tutorial 0.png", 0, 160)
foreground1.centre(1024)
foreground2 = image("Tutorial 1.png", 0, 160)
foreground2.centre(1024)
foreground3 = image("Tutorial 2.png", 0, 160)
foreground3.centre(1024)
foreground4 = image("Tutorial 3.png", 0, 160)
foreground4.centre(1024)
foreground5 = image("Tutorial 4.png", 0, 160)
foreground5.centre(1024)
foreground6 = image("Tutorial 5.png", 0, 160)
foreground6.centre(1024)
foreground7 = image("Tutorial 6.png", 0, 160)
foreground7.centre(1024)
foreground8 = image("Tutorial 7.png", 0, 160)
foreground8.centre(1024)


tutorial1Obj = [background, foreground1]
tutorial2Obj = [background, foreground2]
tutorial3Obj = [background, foreground3]
tutorial4Obj = [background, foreground4]
tutorial5Obj = [background, foreground5]
tutorial6Obj = [background, foreground6]
tutorial7Obj = [background, foreground7]
tutorial8Obj = [background, foreground8]
tutorialButtons = [backButton, nextButton]

#============================================================#
#Load
#============================================================#
#images

background = image("home bg.png", 0, 0)
foreground = image("menubox.png", 0, 0)

#text

title = text("LOAD", "DTM-Sans.otf", 45, (255, 255, 255), 0, 130)
title.centre(1024)
text1 = text("Default Loaded", "DTM-Sans.otf", 25, (255, 255, 255), 0, 230)
text1.centre(1024)

loadObj = [background, foreground, title, text1]

#============================================================#
#settings
#============================================================#
#buttons
offButton = button(100, 40, 10, (255,255,255), 450, 230)
offButtonText = text("OFF", "DTM-Sans.otf", 35, (255, 255, 255), 0, 0)
offButtonText.update()
offButton.addText(offButtonText)
onButton = button(100, 40, 10, (255,255,255), 550, 230)
onButtonText = text("ON", "DTM-Sans.otf", 35, (255, 255, 255), 0, 130)
onButtonText.update()
onButton.addText(onButtonText)
backButton = button(100, 50, 0, (0, 0, 0), 397, 400)
backButton.centre(1024)
backButtonText = text("<back>", "DTM-Sans.otf", 35, (255, 255, 255), 0, 100)
backButtonText.update()
backButton.addText(backButtonText)

#images

background = image("home bg.png", 0, 0)
foreground = image("menubox.png", 0, 0)

#text

title = text("SETTINGS", "DTM-Sans.otf", 45, (255, 255, 255), 0, 130)
title.centre(1024)
music = text("Music:", "DTM-Sans.otf", 35, (255, 255, 255), 350, 230)

settingsObj = [background, foreground, title, music, onButton, offButton, backButton]
settingsButtons = [offButton, onButton, backButton]

#============================================================#
#credits
#============================================================#
#images

background = image("home bg.png", 0, 0)
foreground = image("menubox.png", 0, 0)

#text

title = text("CREDITS", "DTM-Sans.otf", 45, (255, 255, 255), 0, 130)
title.centre(1024)
text1 = text("Henry - Ghost", "DTM-Sans.otf", 45, (255, 255, 255), 0, 230)
text1.centre(1024)
text2 = text("Yingning - GUI", "DTM-Sans.otf", 45, (255, 255, 255), 0, 330)
text2.centre(1024)

creditsObj = [background, foreground, title, text1, text2]


def loading(objectList):        #loading screen
    keep_going = True
    while keep_going:
        mouseX, mouseY = pygame.mouse.get_pos()
        clock.tick(30)
        for ev in pygame.event.get():
            if ev.type == QUIT:
              pygame.display.quit()
              exit()
            elif ev.type == MOUSEBUTTONDOWN or ev.type == KEYDOWN: #check for clicking
                keep_going = False
        scroll(objectList, 0)
        initiate(objectList)
        pygame.display.flip()

def menu(objectList, bList):    #main menu
    keep_going = True
    while keep_going:
        mouseX, mouseY = pygame.mouse.get_pos()
        clock.tick(30)
        for ev in pygame.event.get():
            if ev.type == QUIT:
              pygame.display.quit()
            elif ev.type == MOUSEBUTTONDOWN or ev.type == KEYDOWN: #check for clicking
                counter = 0
                for buttons in bList:
                    clicked = buttons.check(mouseX, mouseY)
                    if clicked:
                        keep_going = False
                        return counter
                    else:
                        counter += 1
                counter = 0

        scroll(objectList, 0)       #scrolling background
        initiate(objectList)
        pygame.display.flip()

def newGame(objectList, bList, noNameText):     #new game, first screen
    keep_going = True                           #initialize variables
    writing = False
    shift = False
    moveOn = False
    noName = False
    noNameCounter = 0
    while keep_going:
        clock.tick(60)         # Update the clock for pacing purposes
                        # Read about it here: http://www.pygame.org/docs/ref/time.html#pygame.time.Clock.tick
        mouseX, mouseY = pygame.mouse.get_pos()
        for ev in pygame.event.get():
            if ev.type == QUIT:      # This is the close widget in the window bar
                pygame.display.quit()
                exit()
            elif ev.type == MOUSEBUTTONDOWN:
                writing = False
                if ev.dict['button'] == 1:
                    writing = False
                    counter = 0
                    for buttons in bList:   #checks if mouse is on a button 
                        clicked = buttons.check(mouseX, mouseY)
                        if clicked:
                            if counter == 0:    #writing button
                                writing = True
                            elif counter == 1:  #back button
                                keep_going = False
                                moveOn = False
                            elif counter == 2:  #next button
                                if objectList[2].text != "":    #will not progress unless some name is given
                                    moveOn = True
                                    keep_going = False
                                
                        counter += 1

            elif ev.type == KEYDOWN:
                #writing
                if writing == True:
                    if ev.key == K_BACKSPACE:   #special case where backspace is pressed
                        objectList[2].text = objectList[2].text[0:-1]   #last character is deleted
                        objectList[2].update()
                    elif ev.key == K_RSHIFT or ev.key == K_LSHIFT:  #special case where shift is pressed
                        shift = True                                #next character is capitalized
                    else:
                        if shift == True:
                            shift = False
                            ev.key -= 32
                        if len(objectList[2].text) <= 17:
                            objectList[2].text += chr(ev.key)       #takes event key and converts to letter
                            objectList[2].update()


        scroll(objectList, 0)   #scrolling background
        initiate(objectList)
        pygame.display.flip()
                

    return moveOn, objectList[2].text

def jobs(name, objectList, bList):      #new game second screen, determining player's job
    keep_going = True
    job = ""
    box = button(0, 0, 0, (0, 0, 0), 0, 0)  #box for indicating player's selection
    while keep_going:
        clock.tick(60)

        mouseX, mouseY = pygame.mouse.get_pos()
        for ev in pygame.event.get():
            if ev.type == QUIT:
                pygame.display.quit()
                exit()
            elif ev.type == MOUSEBUTTONDOWN:
                if ev.dict['button'] == 1:
                    counter = 0
                    for buttons in bList:   #checks if mouse is on a button
                        clicked = buttons.check(mouseX, mouseY)
                        if clicked:
                            if counter == 0:
                                job = "Mathematician"
                                box = mathButton
                            elif counter == 1:
                                job = "Physicist"
                                box = physicsButton
                            elif counter == 2:
                                job = "Chemist"
                                box = chemistButton
                            elif counter == 3:
                                job = "Programmer"
                                box = programmerButton
                            elif counter == 4:
                                job = "Writer"
                                box = writerButton
                            elif counter == 5:
                                job = "Biologist"
                                box = biologistButton
                            elif counter == 6:
                                job = "Athlete"
                                box = athleteButton
                            elif counter == 7:
                                job = "Artist"
                                box = artistButton
                            elif counter == 8:
                                keep_going = False
                                moveOn = False
                            elif counter == 9 and job != "":    #will not continue unless a job is selected
                                moveOn = True
                                keep_going = False
                        counter += 1
        scroll(objectList, 0)   #scroll background
        updatedList = objectList
        updatedList[3] = box    #add the box around the selected job
        initiate(updatedList)
        pygame.display.flip()
    return moveOn, job          #player's job choice is returned

def tutorial(objectList, bList):
    keep_going = True
    while keep_going:
        mouseX, mouseY = pygame.mouse.get_pos()
        clock.tick(30)
        for ev in pygame.event.get():
            if ev.type == QUIT:
              pygame.display.quit()
            elif ev.type == MOUSEBUTTONDOWN or ev.type == KEYDOWN: #check for clicking
                counter = 0
                for buttons in bList:   #checks if mouse is on button
                    clicked = buttons.check(mouseX, mouseY)
                    if clicked:
                        keep_going = False
                        if counter == 0:    #back button
                            return -1       #will move back a screen
                        if counter == 1:    #next button
                            return 1        #will move forward a screen
                    counter += 1

        scroll(objectList, 0)       #scroll background
        initiate(objectList)
        pygame.display.flip()
        
def loadGame(objectList):
    keep_going = True
    while keep_going:
        for ev in pygame.event.get():
            if ev.type == QUIT:      # This is the close widget in the window bar
                pygame.display.quit()
                exit()
            elif ev.type == MOUSEBUTTONDOWN:
                keep_going = False          #return to menu when button is pressed
        scroll(objectList, 0)
        initiate(objectList)
        pygame.display.flip()
        
def settings(objectList, bList):
    keep_going = True
    while keep_going:
        mouseX, mouseY = pygame.mouse.get_pos()
        for ev in pygame.event.get():
            if ev.type == QUIT:      # This is the close widget in the window bar
                pygame.display.quit()
                exit()
            elif ev.type == MOUSEBUTTONDOWN:
                if ev.dict['button'] == 1:
                    counter = 0
                    for buttons in bList:   #checks if mouse is on a button
                        clicked = buttons.check(mouseX, mouseY)
                        if clicked:
                            if counter == 0:        #stop music button
                                pygame.mixer.music.set_volume(0)
                            if counter == 1:        #play music button
                                pygame.mixer.music.set_volume(1)
                            if counter == 2:        #back button
                                keep_going = False      
                        counter += 1
        scroll(objectList, 0)       #scroll background
        initiate(objectList)
        pygame.display.flip()

def credit(objectList):
    keep_going = True
    while keep_going:
        for ev in pygame.event.get():
            if ev.type == QUIT:      # This is the close widget in the window bar
                pygame.display.quit()
                exit()
            elif ev.type == MOUSEBUTTONDOWN:
                keep_going = False      #returns to menu if button is pressed
        scroll(objectList, 0)           #scroll background
        initiate(objectList)
        pygame.display.flip()





#============================================================#
#ACTUAL GAME
#============================================================#

"""
==============================================================
CONFIG
==============================================================
"""

#============================================================#
#MAIN
#============================================================#
        
#Buttons
upgrade = button(0, 0, 10, (255,255,255), 0, 150)
newLocation = button(160, 40, 10, (255,255,255), 623, 20)
newLocationText = text("EXPAND", "DTM-Sans.otf", 20, (255, 255, 255), 0, 0)
newLocationText.update()
newLocation.addText(newLocationText)
newLocCost = text("$100000", "DTM-Sans.otf", 20, (255, 255, 255), 630, 72)

makeMoney = button(160, 40, 10, (255,255,255), 0, 700)
makeMoneyText = text("MONIES", "DTM-Sans.otf", 20, (255, 255, 255), 0, 0)
makeMoneyText.update()
makeMoney.addText(makeMoneyText)
makeMoney.centre(1024)

stats = button(160, 40, 10, (255,255,255), 853, 125)
statsText = text("Stats", "DTM-Sans.otf", 20, (255, 255, 255), 0, 0)
statsText.update()
stats.addText(statsText)

build = button(160, 40, 10, (255,255,255), 0, 727)
buildText = text("STORE", "DTM-Sans.otf", 20, (255, 255, 255), 0, 727)
buildText.update()
build.addText(buildText)

quitButton = button(160, 40, 10, (255,255,255), 900, 727)
quitText = text("QUIT", "DTM-Sans.otf", 20, (255, 255, 255), 0, 0)
quitText.update()
quitButton.addText(quitText)

#Images
background = image("TheGameBoard.png", 0, 0)

header = image("HeaderBar.png", 0,0)
store = image("StoreButton.png", 0, 727)
happiness = button(0, 21, 0, (255, 252, 4), 73, 29)
grade = button(0, 21, 0, (255, 0, 0), 73, 71)

#game board / school
thegb = gameBoard(1, 1, 1, 1, 1)
thegb.update()

#Text
    #money balance
moneyText = text("0", "DTM-Sans.otf", 35, (255, 255, 255), 870, 17)

    #points 
pointsText = text("0", "DTM-Sans.otf", 35, (255, 255, 255), 870, 62)

    #time
time = text("7:00", "DTM-Sans.otf", 35, (255, 255, 255), 0, 62)
time.centre(1024)
    #days passed
days = text("day 1", "DTM-Sans.otf", 35, (255, 255, 255), 0, 18)
days.centre(1024)
    #students
studentsTitle = text("Students", "DTM-Sans.otf", 35, (255, 255, 255), 283, 18)
students = text("0/0", "DTM-Sans.otf", 35, (255, 255, 255), 290, 60)

mouseX = 0
mouseY = 0
xLoc = text("%s" %mouseX, "DTM-Sans.otf", 18, (255, 255, 255), 10000, 10)
yLoc = text("%s" %mouseY, "DTM-Sans.otf", 18, (255, 255, 255), 10000, 200)

mainObj = [background, header, store, makeMoney, thegb, build, moneyText, xLoc, yLoc, happiness, grade, time, pointsText, days, studentsTitle, students, newLocation, stats, newLocCost, quitButton]
mainButtons = [build, upgrade, newLocation, makeMoney, stats, quitButton]
main = display(mainObj, mainButtons)

#============================================================#
#ISF text
#============================================================#
isfText = text("Insufficient Funds...", "DTM-Sans.otf", 35, (0, 0, 0), 0, 500)
isfText.centre(1024)
ISFtext = display([isfText], mainButtons)

#============================================================#
#STORE
#============================================================#

#Buttons

    #physics 
physicsFacBuild = button(196, 78, 10, (13, 107, 79), 57, 353)
physicsFacText = text("$15000", "DTM-Sans.otf", 35, (255, 255, 255), 121, 378)
physicsFacText.update()

    #chem 
chemistryFacBuild = button(196, 78, 10, (13, 107, 79), 294, 353)
chemistryFacText = text("$20000", "DTM-Sans.otf", 35, (255, 255, 255), 352, 378)
chemistryFacText.update()

    #english 
englishFacBuild = button(196, 78, 10, (13, 107, 79), 530, 353)
englishFacText = text("$10000", "DTM-Sans.otf", 35, (255, 255, 255), 599, 378)
englishFacText.update()

    #gym 
gymFacBuild = button(196, 78, 10, (13, 107, 79), 767, 353)
gymFacText = text("$8000", "DTM-Sans.otf", 35, (255, 255, 255), 837, 378)
gymFacText.update()

    #math 
mathFacBuild = button(196, 78, 10, (13, 107, 79), 57, 474)
mathFacText = text("$18000", "DTM-Sans.otf", 35, (255, 255, 255), 121, 489)
mathFacText.update()

    #comsci
comsciFacBuild = button(196, 78, 10, (13, 107, 79), 294, 474)
comsciFacText = text("$30000", "DTM-Sans.otf", 35, (255, 255, 255), 363, 489)
comsciFacText.update()

    #caf
cafFacBuild = button(196, 78, 10, (13, 107, 79), 530, 474)
cafFacText = text("$10000", "DTM-Sans.otf", 35, (255, 255, 255), 599, 489)
cafFacText.update()

    #art 

artFacBuild = button(196, 78, 10, (13, 107, 79), 767, 474)
artFacText = text("$10000", "DTM-Sans.otf", 35, (255, 255, 255), 837, 489)
artFacText.update()

    #quit
quitButton = button(130, 80, 10, (0, 0, 0), 0, 560)
quitButton.centre(1024)
quitButton.update()

#images
storeBox = image("StoreBox.png", 0, 0)
storeBox.centre(1024)


storeObj = [storeBox, physicsFacText, chemistryFacText, englishFacText, gymFacText, mathFacText, comsciFacText, cafFacText, artFacText]
storeButtons = [physicsFacBuild, chemistryFacBuild, englishFacBuild, gymFacBuild, mathFacBuild, comsciFacBuild, cafFacBuild, artFacBuild, quitButton]

store = display(storeObj, storeButtons)


#============================================================#
#BUILDING
#============================================================#
buildingText = text("SELECT A LOCATION", "DTM-Sans.otf", 18, (255, 255, 255), 0, 700)
buildingText.centre(1024)

buildingObj = [buildingText]
buildingButtons = []

building = display(buildingObj, buildingButtons)

#============================================================#
#UPGRADE MENU
#============================================================#

#buttons

upgrade = button(185, 115, 35, (13, 107, 79), 427, 540)
upgradeText = text("UPGRADE", "DTM-Sans.otf", 18, (255, 255, 255), 449, 608)
upgradeText.update()

sell = button(185, 115, 35, (13, 107, 79), 618, 540)
sellText = text("SELL", "DTM-Sans.otf", 18, (255, 255, 255), 639, 608)
sellText.update()

back = button(110, 42, 35, (13, 107, 79), 699, 234)
backText = text("BACK", "DTM-Sans.otf", 18, (255, 255, 255), 0, 0)
backText.update()

#image
upgradeMenu = image("UpgradeMenu.png", 0, 200)
upgradeMenu.centre(1024)

facIcon = image("empty.png", 0, 300)
facIcon.centre(232)
facIcon.x += 228

#text
level = text("LEVEL", "DTM-Sans.otf", 30, (255, 255, 255), 395, 597) 
cost = text("COST", "DTM-Sans.otf", 30, (255, 255, 255), 475, 612) #on the upgrade button
grade = text("GRADE", "DTM-Sans.otf", 30, (255, 255, 255), 587, 277)
happiness = text("HAPPINESS", "DTM-Sans.otf", 30, (255, 255, 255), 658, 340)
capacity = text("CAPACITY", "DTM-Sans.otf", 30, (255, 255, 255), 638, 405)
earningSpeed = text("EPS", "DTM-Sans.otf", 30, (255, 255, 255), 719, 462)

upgradeObj = [upgradeMenu, upgradeText, sellText, facIcon, level, grade, happiness, capacity, earningSpeed]
upgradeButtons = [upgrade, sell, back]

upgradeMenu = display(upgradeObj, upgradeButtons)



#============================================================#
#DAILY REPORT
#============================================================#

#buttons
nextButton = button(196, 78, 10, (13, 107, 79), 521, 644)
nextButtonText = text("NEXT", "DTM-Sans.otf", 18, (255, 255, 255), 0, 0)
nextButtonText.update()
nextButton.addText(nextButtonText)



#images
dailyReportPopUp = image("DailyReport.png", 0, 200)
dailyReportPopUp.centre(1024)

#text
moneySpent = text("$not changed", "DTM-Sans.otf", 28, (255, 0, 0), 558, 422)
moneyEarned = text("$not changed", "DTM-Sans.otf", 28, (0, 255, 0), 563, 493)
netProfit = text("$not changed", "DTM-Sans.otf", 28, (0, 0, 0), 529, 568)
    
reportObj = [dailyReportPopUp, nextButton, moneySpent, moneyEarned, netProfit]
reportButtons = [nextButton]
dailyReport = display(reportObj, reportButtons)

#============================================================#
#MOVING STUDENTS
#============================================================#

movingStudents = display([], mainButtons)

#============================================================#
#STORE ITEM
#============================================================#


#buttons   self, length, width, border, colour, x, y):
buy = button(196, 90, 10, (13, 107, 79), 557, 554)
buyText = text("BUY", "DTM-Sans.otf", 18, (255, 255, 255), 0, 0)
buyText.update()
buy.addText(buyText)

back = button(110, 42, 5, (13, 107, 79), 705, 227)
backText = text("BACK", "DTM-Sans.otf", 18, (255, 255, 255), 0, 0)
backText.update()
back.addText(backText)

#image
storePopUp = image("StatsPopUp_Store.png", 0, 200)
storePopUp.centre(1024)
facIcon = image("empty.png", 0, 300)
facIcon.centre(232)
facIcon.x += 228

#text
name = text("NAME", "DTM-Sans.otf", 30, (255, 255, 255), 244, 260)
cost = text("COST", "DTM-Sans.otf", 30, (255, 255, 255), 565, 270)
grade = text("GRADE", "DTM-Sans.otf", 30, (255, 255, 255), 578, 320)
happiness = text("HAPPINESS", "DTM-Sans.otf", 30, (255, 255, 255), 650, 370)
capacity = text("CAPACITY", "DTM-Sans.otf", 30, (255, 255, 255), 632, 420)
earningSpeed = text("EPS", "DTM-Sans.otf", 30, (255, 255, 255), 706, 470)

storeItemObj = [storePopUp, facIcon, name, cost, happiness, grade, capacity, earningSpeed]
storeItemButtons = [buy, back]
storeItem = display(storeItemObj, storeItemButtons)


#============================================================#
#STATS
#============================================================#

#image
statsBox = image("StatsBox.png", 0, 200)
statsBox.centre(1024)


#buttons
back = button(110, 42, 5, (13, 107, 79), 699, 236)
backText = text("BACK", "DTM-Sans.otf", 18, (255, 255, 255), 0, 0)
backText.update()
back.addText(backText)

moneyMulti = text("MONEY MULTIPLIER", "DTM-Sans.otf", 30, (0, 0, 0), 413, 273)
speedMulti = text("SPEED MULTIPLIER", "DTM-Sans.otf", 30, (0, 0, 0), 413, 339)
happinessMulti = text("HAPPINESS MULTIPLIER", "DTM-Sans.otf", 30, (0, 0, 0), 497, 405)
gradeMulti = text("GRADE MULTIPLIER", "DTM-Sans.otf", 30, (0, 0, 0), 410, 474)
clickMulti = text("CLICK MULTIPLIER", "DTM-Sans.otf", 30, (0, 0, 0), 410, 537)


statsObj = [statsBox, speedMulti, moneyMulti, happinessMulti, gradeMulti, clickMulti]
statsButtons = [back]
stats = display(statsObj, statsButtons)


#allows for passing of all screens into game
screenList = [main, ISFtext, store, upgradeMenu, dailyReport, movingStudents, building, storeItem, stats]

def game(displayList, player, gameBoard, facTypes):
    player.recheck(gameBoard)
    keep_going = True
    moneyTick = 0
    pointsTick = 0 
    displayList[0].bList[1].length = gameBoard.length
    displayList[0].bList[1].width = gameBoard.zoom*gameBoard.rows
    displayList[0].bList[1].centre(1024)
    displayList[0].bList[1].y = gameBoard.y
    displayList[0].bList[1].update()
    building = False
    upgrading = False
    insufficientFunds = False
    pause = False
    assign = True
    ISFcounter = 0
    cDisp = 0
    dayCounter = 0
    arrivalCounter = 0
    moneySpent = 0
    displayList[0].objectList[6].text = player.money
    displayList[0].objectList[6].update()
    buildingFac = englishFac
    while keep_going:
        mouseX, mouseY = pygame.mouse.get_pos()
        for ev in pygame.event.get():
            if ev.type == QUIT:      # This is the close widget in the window bar
                pygame.display.quit()
                save(player, "save1")
                save(gameBoard, "save1GameBoard")
                exit()
            elif ev.type == MOUSEBUTTONDOWN:
                if ev.dict['button'] == 1:
                    counter = 0
                    xPosBoard, yPosBoard = gameBoard.check(mouseX, mouseY)
                    if building:
                        cDisp = 5
                        pause = False
                        building = False
                        if xPosBoard < gameBoard.columns and xPosBoard >= 0 and yPosBoard < gameBoard.rows and yPosBoard >= 0:
                            if player.money >= buildingFac.cost*gameBoard.costConstant/player.buildMulti:
                                player.money -= int(buildingFac.cost*gameBoard.costConstant/player.buildMulti)
                                moneySpent += int(buildingFac.cost*gameBoard.costConstant/player.buildMulti)
                                gameBoard.costConstant *= 1.2
                                for pointer in range( 1, 9):
                                    displayList[2].objectList[pointer].text = int(facTypes[pointer-1].cost*gameBoard.costConstant)
                                    displayList[2].objectList[pointer].update()
                                gameBoard.addFac(xPosBoard, yPosBoard, buildingFac, player)
                                player.recheck(gameBoard)
                            else:
                                insufficientFunds = True
                    
                    else:
                                
                        for buttons in displayList[cDisp].bList:
                            clicked = buttons.check(mouseX, mouseY)
                            if clicked:
                                if cDisp == 0 or cDisp == 5:
                                    if counter == 0:
                                        buildingPopup = True
                                        cDisp = 2
                                        pause = True
                                    elif counter == 1:
                                        if gameBoard.facArray[xPosBoard][yPosBoard].name != "empty":
                                            currentX = xPosBoard
                                            currentY = yPosBoard
                                            upgradingPopup = True
                                            cDisp = 3
                                            currentFac = gameBoard.facArray[currentX][currentY]                         #sphagetti code.
                                            screenList[3].objectList[1].text = int(currentFac.upgradeCost/player.buildMulti)
                                            screenList[3].objectList[1].update()
                                            screenList[3].objectList[2].text = int(currentFac.cost*0.7)
                                            screenList[3].objectList[2].update()
                                            screenList[3].objectList[3] = image("%s.png"%currentFac.name, 0, 310)
                                            screenList[3].objectList[3].centre(231)
                                            screenList[3].objectList[3].x += 225
                                            screenList[3].objectList[4].text = currentFac.level
                                            screenList[3].objectList[4].update()
                                            screenList[3].objectList[4].centre(231)
                                            screenList[3].objectList[4].x += 225
                                            screenList[3].objectList[4].update()
                                            screenList[3].objectList[5].text = currentFac.happinessLevel
                                            screenList[3].objectList[5].update()
                                            screenList[3].objectList[6].text = currentFac.grade
                                            screenList[3].objectList[6].update()
                                            screenList[3].objectList[7].text = currentFac.maxStudents
                                            screenList[3].objectList[7].update()
                                            screenList[3].objectList[8].text = "$" + str(int(currentFac.earningSpeed*player.moneyMulti)) + "/s"
                                            screenList[3].objectList[8].update()
                                            pause = True
                                    elif counter == 2:
                                        pause = False
                                        cDisp = 0
                                        if gameBoard.columns == 2:
                                            if player.money >= 100000:
                                                player.money -= 100000
                                                moneySpent += 100000
                                                gameBoard.expand(2, 2, 150)
                                                displayList[0].objectList[18].text = "5,000,000"
                                                displayList[0].objectList[18].update()
                                            else:
                                                insufficientFunds = True
                                        elif gameBoard.columns == 4:
                                            if player.money >= 5000000:
                                                player.money -= 5000000
                                                moneySpent += 5000000
                                                gameBoard.expand(3, 2, 100)
                                                displayList[0].objectList[18].text = "100,000,000"
                                                displayList[0].objectList[18].update()
                                            else:
                                                insufficientFunds = True
                                        elif gameBoard.columns == 7:
                                            if player.money >= 100000000:
                                                player.money -= 100000000
                                                moneySpent += 100000000
                                                gameBoard.expand(2, 2, 75)
                                                displayList[0].objectList[18].text = player.money
                                                displayList[0].objectList[18].update()
                                            else:
                                                insufficientFunds = True
                                        displayList[0].bList[1].length = gameBoard.length
                                        displayList[0].bList[1].width = gameBoard.zoom*gameBoard.rows
                                        displayList[0].bList[1].centre(1024)
                                        displayList[0].bList[1].y = gameBoard.y
                                        displayList[0].bList[1].update()

                                    elif counter == 3:
                                        gameBoard.earnGuap(player)

                                    elif counter == 4:
                                        cDisp = 8
                                        pause = True
                                        screenList[8].objectList[1].text = player.speedMulti
                                        screenList[8].objectList[1].update()
                                        screenList[8].objectList[2].text = player.moneyMulti
                                        screenList[8].objectList[2].update()
                                        screenList[8].objectList[3].text = player.happinessAdd
                                        screenList[8].objectList[3].update()
                                        screenList[8].objectList[4].text = player.gradeAdd
                                        screenList[8].objectList[4].update()
                                        screenList[8].objectList[5].text = player.clickMulti
                                        screenList[8].objectList[5].update()

                                    elif counter == 5:
                                        keep_going = False
                                        save(player, "save1")
                                        save(gameBoard, "save1GameBoard")

                                elif cDisp == 2:
                                    cDisp = 5
                                    if counter < 8:
                                        cDisp = 7
                                        openedFac = facTypes[counter]
                                        screenList[7].objectList[1] = image("%s.png"%facTypes[counter].name, 0, 310)
                                        screenList[7].objectList[1].centre(231)
                                        screenList[7].objectList[1].x += 225
                                        screenList[7].objectList[2].text = openedFac.name
                                        screenList[7].objectList[2].update()
                                        screenList[7].objectList[2].centre(231)
                                        screenList[7].objectList[2].x += 225
                                        screenList[7].objectList[2].update()
                                        screenList[7].objectList[3].text = int(openedFac.cost/player.buildMulti)
                                        screenList[7].objectList[3].update()
                                        screenList[7].objectList[4].text = openedFac.happinessLevel
                                        screenList[7].objectList[4].update()
                                        screenList[7].objectList[5].text = openedFac.grade
                                        screenList[7].objectList[5].update()
                                        screenList[7].objectList[6].text = openedFac.maxStudents
                                        screenList[7].objectList[6].update()
                                        screenList[7].objectList[7].text = "$" + str(openedFac.earningSpeed) + "/s"
                                        screenList[7].objectList[7].update()
                                        
                                    if counter == 8:
                                        pause = False

                                elif cDisp == 3:
                                    pause = False
                                    cDisp = 5
                                    if counter == 0:
                                        if player.money >= gameBoard.facArray[currentX][currentY].upgradeCost/player.buildMulti:
                                            player.money -= int(gameBoard.facArray[currentX][currentY].upgradeCost/player.buildMulti)
                                            moneySpent += int(gameBoard.facArray[currentX][currentY].upgradeCost)
                                            gameBoard.facArray[currentX][currentY].levelUp()
                                            player.recheck(gameBoard)
                                            currentFac = gameBoard.facArray[currentX][currentY]
                                            screenList[3].objectList[1].text = int(currentFac.upgradeCost/player.buildMulti)
                                            screenList[3].objectList[1].update()
                                            screenList[3].objectList[2].text = int(currentFac.cost*0.7)
                                            screenList[3].objectList[2].update()
                                            screenList[3].objectList[3] = image("%s.png"%currentFac.name, 0, 310)
                                            screenList[3].objectList[3].centre(231)
                                            screenList[3].objectList[3].x += 225
                                            screenList[3].objectList[4].text = currentFac.level
                                            screenList[3].objectList[4].update()
                                            screenList[3].objectList[4].centre(231)
                                            screenList[3].objectList[4].x += 225
                                            screenList[3].objectList[4].update()
                                            screenList[3].objectList[5].text = str(int(currentFac.happinessLevel*100)) + "%"
                                            screenList[3].objectList[5].update()
                                            screenList[3].objectList[6].text = currentFac.grade
                                            screenList[3].objectList[6].update()
                                            screenList[3].objectList[7].text = currentFac.maxStudents
                                            screenList[3].objectList[7].update()
                                            screenList[3].objectList[8].text = "$" + str(int(currentFac.earningSpeed*player.moneyMulti)) + "/s"
                                            screenList[3].objectList[8].update()
                                            cDisp = 3
                                            pause = True
                                        else:
                                            insufficientFunds = True

                                    elif counter == 1:
                                        gameBoard.deleteFac(currentX, currentY, empty, player)
                                        gameBoard.costConstant = gameBoard.costConstant/1.2

                                    elif counter == 2:
                                        pass
                                        
                                elif cDisp == 4:
                                    cDisp = 5
                                    if counter == 0:
                                        pause = False

                                elif cDisp == 7:
                                    cDisp = 5
                                    if counter == 0:
                                        building = True
                                        buildingFac = openedFac
                                        cDisp = 6
                                    elif counter == 1:
                                        pause = False

                                elif cDisp == 8:
                                    cDisp = 5
                                    pause = False

                            counter += 1
                            
#moving students
        if assign == True:
            assign = False
            move = True
            gameBoard.studentList = []
            availabilityList = []
            totalAvailability = 0
            displayList[5].objectList = []
            for x in range(0, gameBoard.columns):
                for y in range(0, gameBoard.rows):
                    gameBoard.facArray[x][y].cStudents = 0
                    if gameBoard.facArray[x][y].name != "empty":
                        availabilityList += [[x, y, gameBoard.facArray[x][y].maxStudents]]
                        totalAvailability += gameBoard.facArray[x][y].maxStudents

            
            
            for pointer in range(0, min(player.studentMaxNum, totalAvailability)):
                availability = 0
                while availability == 0:
                    randInt = random.randint(0, len(availabilityList)-1)
                    x, y, availability = availabilityList[randInt]
                availabilityList[randInt][2] -= 1
                gameBoard.studentList += [student(gameBoard.zoom, x, y, gameBoard, player.speedMulti)]
                displayList[5].objectList += [gameBoard.studentList[pointer]] + []

        if pause != True:
            dayCounter += 1
            moneyTick += 1

            if move == True:
                cDisp = 5
                for pointer in range(0, len(gameBoard.studentList)):
                    students = gameBoard.studentList[pointer]
                    if students.arrival == False:
                        students.move(gameBoard.rows)
                    else:
                        if students.counted == False:
                            if gameBoard.facArray[students.xNum][students.yNum].name != "empty":
                                gameBoard.facArray[students.xNum][students.yNum].cStudents += 1
                                displayList[5].objectList[pointer] = gameBoard.addStudents(students.xNum, students.yNum)
                                students.counted = True
                                arrivalCounter += 1
                        
                if arrivalCounter == len(gameBoard.studentList):
                    arrivalCounter = 0
                    move = False
                            
    
        if moneyTick >= 60:
            gameBoard.earnGuap(player)
            moneyTick = 0

        if insufficientFunds == True:
            cDisp = 1
            ISFcounter += 1
            if ISFcounter >= 120:
                cDisp = 5
                insufficientFunds = False
                ISFcounter = 0
            
        elif dayCounter >= (1260 + player.timeAdd):
            #update daily summary values
            netProfit = player.newDay()
            displayList[4].objectList[2].text = "$" + str(moneySpent)
            displayList[4].objectList[2].update()
            displayList[4].objectList[3].text = "$" + str(int(netProfit + moneySpent))
            displayList[4].objectList[3].update()
            displayList[4].objectList[4].text = "$" + str(netProfit)
            displayList[4].objectList[4].update()
            dayCounter = 0
            arrivalCounter = 0
            moneySpent = 0
            cDisp = 4
            pause = True
            assign = True


        #Stats Bar
        displayList[0].objectList[6].text = player.money
        displayList[0].objectList[6].update()
        displayList[0].objectList[7].text = mouseX
        displayList[0].objectList[7].update()
        displayList[0].objectList[8].text = mouseY
        displayList[0].objectList[8].update()
        displayList[0].objectList[9].length = 149*gameBoard.totalHappiness
        displayList[0].objectList[9].update()
        displayList[0].objectList[10].length = 149*gameBoard.averageGrade
        displayList[0].objectList[10].update()
        timeCounter = int(dayCounter/3)
        displayList[0].objectList[11].text = "{0:2}:{1:2}".format(str(timeCounter//60 + 8), str(timeCounter%60))
        displayList[0].objectList[11].update()
        displayList[0].objectList[12].text = str(player.score)
        displayList[0].objectList[12].update()
        displayList[0].objectList[13].text = "day " + str(player.dayNum)
        displayList[0].objectList[13].update()
        displayList[0].objectList[15].text = str(min(player.studentMaxNum, totalAvailability)) + "/" + str(player.studentMaxNum)
        displayList[0].objectList[15].update()

        #Daily Report

        initiate(displayList[0].objectList)                        
        initiate(displayList[cDisp].objectList)
        pygame.display.flip()

            
        

#main
pygame.mixer.music.load("sounds\\ambient.wav")
pygame.mixer.music.set_volume(1) #to adjust the volume
pygame.mixer.music.play(-1) #to play the loaded song, -1 means repeat
loading(loadingObj)
keep_going = True
while keep_going:
    choice = menu(menuObj, menuButtons)
    if choice == 0:
        moveOn, name = newGame(newGameObj, newGameButtons, noNameText)
        if moveOn:
            moveOn, job = jobs(name, jobsObj, jobsButtons)
            if moveOn:
                p1 = player(name, 20000, 100, 100, job, 100, 1) #initializes the player
                counter = 0
                tutorial1Obj += [text("%s"%p1.name, "DTM-Sans.otf", 35, (255, 255, 255), 470, 193)]         #tutorial 1 requires player name
                tutorial1Obj += [text("%s"%p1.profession, "DTM-Sans.otf", 35, (255, 255, 255), 400, 252)]   #and player profession
                while counter <= 7:         #tutorial/help
                    if counter == -1:
                        counter = 0
                    if counter == 0:    #first screen
                        counter += tutorial(tutorial1Obj, tutorialButtons)
                    elif counter == 1:  #second screen
                        counter += tutorial(tutorial2Obj, tutorialButtons)
                    elif counter == 2:  #third screen
                        counter += tutorial(tutorial3Obj, tutorialButtons)
                    elif counter == 3:  #fourth screen
                        counter += tutorial(tutorial4Obj, tutorialButtons)
                    elif counter == 4:  #fifth screen
                        counter += tutorial(tutorial5Obj, tutorialButtons)
                    elif counter == 5:  #sixth screen
                        counter += tutorial(tutorial6Obj, tutorialButtons)
                    elif counter == 6:  #seventh screen
                        counter += tutorial(tutorial7Obj, tutorialButtons)
                    elif counter == 7:  #eigth screen
                        counter += tutorial(tutorial8Obj, tutorialButtons)
                        
                thegb = gameBoard(2, 1, 0, 200, 300)    #initialize first school
                thegb.update()
                thegb.centre(1024)
                thegb.update()
                main.objectList[4] = thegb
                game(screenList, p1, thegb, facTypes) #have fun!
            else:
                pass
        else:
            pass
    if choice == 1: #opens a previous save
        p1 = load("save1")
        thegb1 = load("save1GameBoard")
        thegb1.update()
        main.objectList[4] = thegb1
        game(screenList, p1, thegb1, facTypes)

    if choice == 2: #replays tutorial
        counter = 0
        while counter <= 6:
            if counter == -1:
                counter = 10
            if counter == 0:
                counter += tutorial(tutorial2Obj, tutorialButtons)
            elif counter == 1:
                counter += tutorial(tutorial3Obj, tutorialButtons)
            elif counter == 2:
                counter += tutorial(tutorial4Obj, tutorialButtons)
            elif counter == 3:
                counter += tutorial(tutorial5Obj, tutorialButtons)
            elif counter == 4:
                counter += tutorial(tutorial6Obj, tutorialButtons)
            elif counter == 5:
                counter += tutorial(tutorial7Obj, tutorialButtons)
            elif counter == 6:
                counter += tutorial(tutorial8Obj, tutorialButtons)

    if choice == 3: #settings for sound
        settings(settingsObj, settingsButtons)
    if choice == 4: #credits!
        credit(creditsObj)
    if choice == 5: #quit game
        keep_going = False
pygame.display.quit()
pygame.mixer.music.stop()
