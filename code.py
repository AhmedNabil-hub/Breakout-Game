from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pygame
from sys import exit
import numpy as np
import math


##### initial parameters ####

Xoffset, Yoffset = 3, 3 # increment or decrement in ball position
### Bricks parameters ###
Bricks = [] # List to store all bricks, each element of list is a brick class
brickWidth = 54
brickHeight = 26
brickShiftX= 59
brickShiftY = 32.5
firstPointX = 22 # start point of bricks 
firstPointY = 583 # start point of bricks 
activeBricks = 528 # number of active bricks
### Game state parameters ###
life = 3
score = 0
highestScore = 0
dead = True # if true, the player is dead
resume = False # make it true to make the player play after he is dead
### Timer parameters ###
count = 0 # temp variable to count seconds
### Coloring parameters ###
color = (1,0,0)
w = 1  # temp variable changes gradually to make color of text changes gradually
colorInc = False # if true, value of w increases
### Menu parameters ###
action = ["PLAY", "QUIT"] # actions done when buttons clicked
clicked = False # if true, the left mouse button is clicked
z = -10 # changes z of menu objects to be in or out the frustum

#############################

#### initializing sound ####
pygame.mixer.init()

hittingBrick = pygame.mixer.Sound("hitting brick.wav")
hittingPaddle = pygame.mixer.Sound("hitting-paddle.wav")
hittingWall = pygame.mixer.Sound("hitting-wall.wav")
lose = pygame.mixer.Sound("lose.wav")
death = pygame.mixer.Sound("death.wav")
mouse = pygame.mixer.Sound("Mouse Click.wav")

############################

class Display():
    windowWidth = 750
    windowHeight = 1000
    frustumHeight = [0, windowHeight]
    mouseX = windowWidth / 2
    mouseY = windowHeight / 2
    cameraPosition = [0, frustumHeight[0], 0]  #eyeX, eyeY, eyeZ

    @staticmethod
    def init():
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
        glutInitWindowSize(Display.windowWidth, Display.windowHeight)
        glutCreateWindow(b"Break Out game")
        Display.camera()
        glutDisplayFunc(Render)
        glutIdleFunc(Render)
        glutTimerFunc(100, Timer, 1)
        glutPassiveMotionFunc(mouseMotion)
        glutMouseFunc(mouseClick)
        glutKeyboardFunc(Keyboard)
    
    @staticmethod
    def camera():
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0,Display.windowWidth, Display.frustumHeight[0], Display.frustumHeight[1], -100, 100)
        gluLookAt(Display.cameraPosition[0], Display.cameraPosition[1], Display.cameraPosition[2],
                Display.cameraPosition[0], Display.cameraPosition[1], Display.cameraPosition[2]-1,
                0, 1, 0)
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_DEPTH_TEST)

class Ball():
    radius = 10
    position = [100, 40] # initial position of ball
    boundingBox = [position[0]-radius, position[1]+radius, position[0]+radius, position[1]-radius] # Left, Top, Right, Bottom

class Paddle():
    width, height = 100, 20
    position = [0, 70]
    bottomLeft = [position[0]- width/2, position[1]+Display.frustumHeight[0]+0.5]
    bottomRight = [position[0]+ width/2, position[1]+Display.frustumHeight[0]+0.5]
    topRight = [position[0]+ width/2, position[1]+Display.frustumHeight[0]+height+0.5]
    topLeft =  [position[0]- width/2, position[1]+Display.frustumHeight[0]+height+0.5]

class Brick():
    def __init__(self, bottomLeft):
        self.bottomLeft = bottomLeft
        self.bottomRight = (bottomLeft[0]+brickWidth, bottomLeft[1])
        self.topRight = (bottomLeft[0]+brickWidth, bottomLeft[1]+brickHeight)
        self.topLeft = (bottomLeft[0], bottomLeft[1]+brickHeight)

        self.active = True # if True, brick will be drawn

class Collision():
       
    objList = []  #minX, maxY, maxX, minY # list to store bounding box of bricks
    direction = 0  # 0 --> ForwardRight, 1 --> ForwardLeft, 2 --> BackwardLeft, 3 --> BackwardRight
    
    @staticmethod
    def getDirection():
        if   Xoffset >= 0 and Yoffset >= 0: # going ForwardRight
            Collision.direction = 0 

        elif Xoffset >= 0 and Yoffset <  0: # going BackwardRight
            Collision.direction = 3

        elif  Xoffset <  0 and Yoffset >= 0: # going ForwardLeft
            Collision.direction = 1 

        elif  Xoffset <  0 and Yoffset <  0: # going BackwardLeft
            Collision.direction = 2 
    
    @staticmethod
    def checkTopFace(): # of the ball
        global Xoffset
        global Yoffset
        if  (Ball.boundingBox[1] < Collision.objList[1] and Ball.boundingBox[1] > Collision.objList[3] ) and \
            ((Ball.boundingBox[0] >=  Collision.objList[0] and Ball.boundingBox[0] <= Collision.objList[2]) or \
            (Ball.boundingBox[2] >=  Collision.objList[0] and Ball.boundingBox[2] <=  Collision.objList[2]) or \
            (Ball.boundingBox[0] <  Collision.objList[0] and Ball.boundingBox[2] > Collision.objList[2])):

            Yoffset = -Yoffset
            return True
        else:
            return False

    @staticmethod
    def checkBottomFace(): # of the ball
        global Xoffset
        global Yoffset
        if  (Ball.boundingBox[3] > Collision.objList[3] and Ball.boundingBox[3] < Collision.objList[1]) and \
            ((Ball.boundingBox[0] >=  Collision.objList[0] and Ball.boundingBox[0] <= Collision.objList[2]) or \
            (Ball.boundingBox[2] >=  Collision.objList[0] and Ball.boundingBox[2] <=  Collision.objList[2]) or \
            (Ball.boundingBox[0] <  Collision.objList[0] and Ball.boundingBox[2] > Collision.objList[2])):
            Yoffset = -Yoffset
            return True
        else:
            return False
        
    @staticmethod
    def checkRightFace(): # of the ball
        global Xoffset
        global Yoffset
        if  (Ball.boundingBox[2] > Collision.objList[0] and Ball.boundingBox[2] < Collision.objList[2] ) and \
            ((Ball.boundingBox[3] >=  Collision.objList[3] and Ball.boundingBox[3] <= Collision.objList[1]) or \
            (Ball.boundingBox[1] >=  Collision.objList[3] and Ball.boundingBox[1] <=  Collision.objList[1]) or \
            (Ball.boundingBox[3] <  Collision.objList[3] and Ball.boundingBox[1] > Collision.objList[1])):
            Xoffset = -Xoffset
            return True
        else:
            return False
            
    @staticmethod
    def checkLeftFace(): # of the ball
        global Xoffset
        global Yoffset
        if  (Ball.boundingBox[0] < Collision.objList[2] and Ball.boundingBox[0] > Collision.objList[0] ) and \
            ((Ball.boundingBox[3] >=  Collision.objList[3] and Ball.boundingBox[3] <= Collision.objList[1]) or \
            (Ball.boundingBox[1] >=  Collision.objList[3] and Ball.boundingBox[1] <=  Collision.objList[1]) or \
            (Ball.boundingBox[3] <  Collision.objList[3] and Ball.boundingBox[1] > Collision.objList[1])):
            Xoffset = -Xoffset        
            return True
        else:
            return False
    
    @staticmethod
    def detectBrick(): # detect collision of ball with brick
        Collision.getDirection()

        if   Collision.direction == 0 : # ForwardRight
            if Collision.checkTopFace() or Collision.checkRightFace():
                return True
            else:
                return False

        elif Collision.direction == 1 : #ForwardLeft
            if Collision.checkTopFace() or Collision.checkLeftFace():
                return True
            else:
                return False

        elif Collision.direction == 2 : # BackwardLeft
            if Collision.checkBottomFace() or Collision.checkLeftFace():
                return True
            else:
                return False

        elif Collision.direction == 3 : # BackwardRight
            if Collision.checkBottomFace() or Collision.checkRightFace():
                return True
            else:
                return False
    
    @staticmethod
    def detectWall(): # detect collision of ball with wall
        global Xoffset, Yoffset, dead, life

        if Ball.boundingBox[2] >= Display.windowWidth-30 or  Ball.boundingBox[0] <= 0+30 : # check left and right walls
            Xoffset = -Xoffset  
            pygame.mixer.Sound.play(hittingWall)
        elif Ball.boundingBox[3] <= Display.frustumHeight[0] : # check bottom wall
            Yoffset = -Yoffset
            dead = True
            life -= 1
            if life > 0:
                pygame.mixer.Sound.play(lose)
        elif Ball.boundingBox[1] >= Display.frustumHeight[1]-80: # check top wall
            Yoffset = -Yoffset
            pygame.mixer.Sound.play(hittingWall)

    @staticmethod
    def detectPaddle(): # detect collision of ball with paddle
        Collision.objList = [Paddle.bottomLeft[0], Paddle.topRight[1], Paddle.topRight[0], Paddle.bottomLeft[1]]
        if Collision.checkBottomFace() :
            pygame.mixer.Sound.play(hittingWall)

def resetGame():
    global Xoffset, Yoffset, Bricks, firstPointX, firstPointY, activeBricks,\
           life, score, dead, resume, count, color

    Xoffset = 3
    Yoffset = 3
    Bricks = [] 
    firstPointX = 22 
    firstPointY = 583
    activeBricks = 528 
    life = 3
    score = 0
    dead = True 
    resume = False 
    count = 0 
    color = (1,0,0)
    Display.frustumHeight = [0, Display.windowHeight]
    Paddle.width = 100
    generateLevel()

def generateLevel():
    global Bricks
    
    ### STRAIGHT LINES UP & DOWN DRAWING ###
    XstartPoint = firstPointX
    YstartPoint= firstPointY
    
    for Lines in range (0,44,1):
        for N in range (1,12,1):
            if Lines/4 == N:
             YstartPoint += 4*brickShiftY
        
        for Rows in range (0,12,1):
            Bricks.append(Brick((XstartPoint,YstartPoint)))
            XstartPoint += brickShiftX
        YstartPoint +=  brickShiftY
        XstartPoint = 22

generateLevel()
        
def button(text, bottomLeft, width, height, activeColor, inactiveColor, action):
    global z

    if  (bottomLeft[0]+ width+30 > Display.mouseX and Display.mouseX > bottomLeft[0]-30) and\
        (bottomLeft[1] + height > Display.windowHeight-Display.mouseY and Display.windowHeight-Display.mouseY > bottomLeft[1]):
        glColor4f(activeColor[0], activeColor[1], activeColor[2], activeColor[3])
        if clicked is True:
            if action == "PLAY":
                pygame.mixer.Sound.play(mouse)  
                z = 200
            elif action == "QUIT":
                pygame.mixer.Sound.play(mouse)  
                exit()
    else:
        glColor4f(inactiveColor[0], inactiveColor[1], inactiveColor[2], inactiveColor[3])
    # Drawing button
    glBegin(GL_POLYGON)
    glVertex3f(bottomLeft[0], bottomLeft[1], z)
    glVertex3f(bottomLeft[0]+width, bottomLeft[1], z)
    glVertex3f(bottomLeft[0]+width, bottomLeft[1]+height, z)
    glVertex3f(bottomLeft[0], bottomLeft[1]+height, z)
    glEnd()
    drawCircle(30, 285, bottomLeft[1]+30)
    drawCircle(30, 465, bottomLeft[1]+30)

    glColor(0,0,0)
    drawText(text, bottomLeft[0]+(width/2)-30, bottomLeft[1]+(height/2)-15, 0.35, 0.35, 4)

def drawCircle(r=1, xc=0, yc=0):
    glBegin(GL_POLYGON)
    for theta in np.arange(0, 360, 1):
        x = r * math.cos(theta * math.pi / 180) + xc
        y = r * math.sin(theta * math.pi / 180) + yc
        glVertex3f(x, y, z)
    glEnd()

def changeColor(y): # change color of objects to the frame color they are in its range
    global color
    if y >= Display.frustumHeight[0]+ firstPointY+ 4* brickShiftY and y < Display.frustumHeight[0]+ firstPointY+ 8* brickShiftY:
        color = (.9647,.4314,0)       #   ORANGE
    elif y >= Display.frustumHeight[0]+firstPointY and y <= Display.frustumHeight[0]+firstPointY+ 4* brickShiftY:
        color = (0,1,0)                # GREEN
    elif y >= Display.frustumHeight[0]+ firstPointY- 4* brickShiftY and y <= Display.frustumHeight[0]+ firstPointY:
        color  = (1,1,0)                 #YELLOW
    elif y >=  Display.frustumHeight[0] and y <=  Display.frustumHeight[0]+ 14.738* brickShiftY:
        color = (1,1,1)                    #WHITE
    elif (y >= Display.frustumHeight[0]+firstPointY +8* brickShiftY and y <= Display.frustumHeight[0]+firstPointY + 12* brickShiftY) or (y <= Display.frustumHeight[0]+firstPointY - 15.8* brickShiftY):
        color = (0,0,1)            ## BLUE

def drawQuad(bottomLeft, bottomRight, topRight, topLeft):
    glBegin(GL_QUADS)
    glVertex(bottomLeft[0], bottomLeft[1], 0)
    glVertex(bottomRight[0], bottomRight[1], 0)
    glVertex(topRight[0], topRight[1], 0)
    glVertex(topLeft[0], topLeft[1], 0)
    glEnd()

def drawFrameStrip(firstPoint , num ): # draw frame strips 
    glBegin(GL_LINES) 
    # Left side
    glVertex(firstPoint[0], firstPoint[1]) # firstpoint[0] : x of the line strip of frame on left of the window
    glVertex(firstPoint[0], firstPoint[1]+num*brickShiftY) # firstpoint[1] : y of the line strip of frame of both sides of the window
    # Right side
    glVertex(firstPoint[2], firstPoint[1]) # firstpoint[2] : x of the line strip of frame on right of the window
    glVertex(firstPoint[2], firstPoint[1]+num*brickShiftY)
    glEnd()

def drawFrame():
    glColor3f(.9647,.4314,0)    #   ORANGE
    glLineWidth(80)
    drawFrameStrip([Display.windowWidth-745 ,Display.frustumHeight[0]+firstPointY +4* brickShiftY ,Display.windowWidth - 5], 4)

    glColor3f(0,1,0)     # GREEN
    drawFrameStrip([Display.windowWidth -745 ,Display.frustumHeight[0]+firstPointY  ,Display.windowWidth - 5], 4)

    glColor3f(1,1,0)        #YELLOW
    drawFrameStrip([Display.windowWidth -745 ,Display.frustumHeight[0]+firstPointY -4* brickShiftY ,Display.windowWidth - 5], 4)

    glColor3f(0,0,1)            ## BLUE
    drawFrameStrip([Display.windowWidth -745 ,Display.frustumHeight[0]+firstPointY +8* brickShiftY ,Display.windowWidth - 5], 4)
    drawFrameStrip([Display.windowWidth -745 ,Display.frustumHeight[0]+ firstPointY - 15.8* brickShiftY ,Display.windowWidth - 5], .6)
    drawline(Display.windowWidth, Display.frustumHeight[1]-7)

    glColor3f(1,1,1)        #WHITE
    drawFrameStrip([Display.windowWidth -745 , Display.frustumHeight[0]+0 ,Display.windowWidth - 5], 14.738)

def drawline(first,second):
    glBegin(GL_LINES)
    glVertex(0,second -3)
    glVertex(first , second-3)
    glEnd()
            
def mouseClick(button, state, x, y):
    global clicked

    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            clicked = True
        else:
            clicked = False 

def mouseMotion(x, y):
    Display.mouseX = x 
    Display.mouseY = y

def Keyboard(key, x, y):
    global resume
    if key == b" ": # press space bar to resume when player dies
        resume = True
    if ord(key) == 27 : # press Esc button to exit
        exit()

def drawText(string, posX, posY, scaleX, scaleY, lineWidth):
    glLineWidth(lineWidth)
    glPushMatrix() 
    glLoadIdentity()  
    glTranslate(posX, posY, 0)
    glScale(scaleX, scaleY, 3)
    string = string.encode()  # conversion from Unicode string to byte string
    for c in string:
        glutStrokeCharacter(GLUT_STROKE_ROMAN, c)
    glPopMatrix()
    
def Timer(t):
    global count
    
    if z!= -10: # timer doesn't count when the player is in the menu
        count += 1
        if count == 100: # for 10 seconds
            count = 0

        if 90 <= count < 100: # is true for 10 times to make bricks go down gradually   
            # frustum changes after every 10 seconds  
            Display.frustumHeight[0] += brickShiftY/10 # Translate bottom of frustum  
            Display.frustumHeight[1] += brickShiftY/10 # Translate top of frustum
            if Paddle.width >= 50:
                Paddle.width -= 3/10
    
    Display.camera() # update camera
    Render()
        
    glutTimerFunc(100, Timer, 1)

def Render():
    global Xoffset, Yoffset, activeBricks, dead, life,\
           score, resume, color, highestScore, colorInc, w

    glClearColor(0,0,0,0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    drawFrame()

    if z != 200: # render menu only 
        button("Play", (285,(Display.frustumHeight[0]+Display.frustumHeight[1])/2),180,60, (1,1,0,0.5), (0.2745,0.5089,0.7588,0.5), "PLAY")
        button("Quit", (285,(Display.frustumHeight[0]+Display.frustumHeight[1])/3),180,60, (1,1,1,0.5), (0.28,0.5,0.7,0.5), "QUIT")
        glColor(.9647,.4314,0)
        drawText("Breakout", Display.windowWidth-525, Display.windowHeight-250, 0.6, 0.6, 6.5)

    else: # render game without menu

        #### conditions to change text color ####
        if colorInc :
            if w < 1:
                w += 0.03
            else:
                colorInc = False
        else:
            if w > 0:
                w -= 0.03
            else:
                colorInc = True
        
        if dead is True :
            Ball.position[0] = Paddle.position[0] # update ball position to stick on paddle
            Ball.position[1] = Display.frustumHeight[0]+ Paddle.position[1]+ Paddle.height+ Ball.radius+ 2
            Xoffset, Yoffset = 0, 0 # stop the ball until resume
            
            if resume :
                dead = False
                resume = False
                Xoffset = 3
                Yoffset = 3

        if activeBricks > 0 and life > 0 :
            # draw game states on screen
            glColor(w, w, w)  # to make text apper and disapper with time
            drawText( str(score), Display.windowWidth/3-20, Display.frustumHeight[0]+20, 0.3, 0.3, 3)
            glColor(1,1,1)
            drawText( str(life), Display.windowWidth*2/3-20, Display.frustumHeight[0]+20, 0.3, 0.3, 3)

            # Draw paddle
            glColor3f(0,0,1)            ## BLUE
            glPushMatrix()
            glLoadIdentity()
            if not (Display.mouseX < Paddle.width/2 or Display.mouseX > Display.windowWidth-Paddle.width/2): # to make paddle between left and right borders of window
                Paddle.position[0] = Display.mouseX # updating paddle position
                Paddle.bottomLeft = [Paddle.position[0]- Paddle.width/2, Paddle.position[1]+Display.frustumHeight[0]]
                Paddle.bottomRight = [Paddle.position[0]+ Paddle.width/2, Paddle.position[1]+Display.frustumHeight[0]]
                Paddle.topRight = [Paddle.position[0]+ Paddle.width/2, Paddle.position[1]+Display.frustumHeight[0]+Paddle.height]
                Paddle.topLeft =  [Paddle.position[0]- Paddle.width/2, Paddle.position[1]+Display.frustumHeight[0]+Paddle.height]
            drawQuad(Paddle.bottomLeft, Paddle.bottomRight, Paddle.topRight, Paddle.topLeft)
            glPopMatrix()

            # Draw ball
            changeColor(Ball.position[1])
            glColor(color[0], color[1], color[2],0)
            glPushMatrix()
            glLoadIdentity()
            glTranslate(Ball.position[0], Ball.position[1],0)
            glutSolidSphere(Ball.radius, 50, 50)
            glPopMatrix()
        
        # Draw bricks
            for i in range(len(Bricks)):
                if Bricks[i].active is True:
                    if Bricks[i].bottomLeft[1] <= Paddle.topLeft[1] + 2*Ball.radius + 1: # player dies when bricks go down 
                        life = 0
                        break
                    
                    changeColor(Bricks[i].bottomLeft[1])
                    glColor3f(color[0], color[1], color[2])
                    drawQuad(Bricks[i].bottomLeft, Bricks[i].bottomRight, Bricks[i].topRight, Bricks[i].topLeft)
                
                if not dead: # doen't check collision when player is dead # saves computations
                    Collision.objList = [Bricks[i].bottomLeft[0], Bricks[i].topRight[1], Bricks[i].topRight[0], Bricks[i].bottomLeft[1]] # updating objlist to check collision
                    if Bricks[i].active is True and Collision.detectBrick() : # if true, this brick will not be drawn
                        Bricks[i].active = False
                        activeBricks -= 1
                        score += 1
                        pygame.mixer.Sound.play(hittingBrick)

            if not dead: # doen't check collision when player is dead # saves computations
                Collision.detectWall()
                Collision.detectPaddle()
                Ball.position[0] += Xoffset # updating ball position
                Ball.position[1] += Yoffset
                Ball.boundingBox = [Ball.position[0]-Ball.radius, Ball.position[1]+Ball.radius, Ball.position[0]+Ball.radius, Ball.position[1]-Ball.radius] # Left, Top, Right, Bottom

            if life == 0 :
                highestScore = max(highestScore,score)
                pygame.mixer.Sound.play(death)   # Lose 
                
        if life == 0  :
            glColor(0.5, 0.5, w) 
            drawText("Press Space bar to try again", 80, (Display.frustumHeight[0]+Display.frustumHeight[1])/2, 0.3, 0.3, 3)
            drawText("Press Esc to quit", 210, (Display.frustumHeight[0]+Display.frustumHeight[1])/2-80, 0.3, 0.3, 2.5)
            drawText("HIGH SCORE: "+str(highestScore), 220, Display.frustumHeight[0]+20, 0.3, 0.3, 3)
        
            if resume is True:
                resetGame()
        
    glutSwapBuffers()

def main():
    Display.init()
    pygame.init()
    glutMainLoop()

main()
    
