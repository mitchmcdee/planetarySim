import sys
from math import sin, cos
from random import randint
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
#angle of rotation
xpos= ypos= zpos= xrot= yrot= angle= lastx= lasty = 0

#positions of the cubes
positionz = []
positionx = []

def init():
    global positionz, positionx
    glEnable(GL_DEPTH_TEST) #enable the depth testing
    glEnable(GL_LIGHTING) #enable the lighting
    glEnable(GL_LIGHT0) #enable LIGHT0, our Diffuse Light
    glShadeModel(GL_SMOOTH) #set the shader to smooth shader

    positionx = [randint(0, 10) for x in range(10)]
    positionz = [randint(0, 10) for x in range(10)]

def camera():
    global xrot, yrot, xpos, ypos, zpos
    glRotatef(xrot,1.0,0.0,0.0)  #rotate our camera on teh x-axis (left and right)
    glRotatef(yrot,0.0,1.0,0.0)  #rotate our camera on the y-axis (up and down)
    glTranslated(-xpos,-ypos,-zpos) #translate the screen to the position of our camera

def display():
    global angle
    glClearColor(0.0,0.0,0.0,1.0) #clear the screen to black
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) #clear the color buffer and the depth buffer
    glLoadIdentity()
    camera()
    for x in range(10):
        glPushMatrix()
        glTranslated(-positionx[x] * 10, 0, -positionz[x] * 10) #translate the cube
        glutSolidCube(2) #draw the cube
        glPopMatrix()
    glutSwapBuffers() #swap the buffers
    angle += angle #increase the angle

def reshape(w, h):
    glViewport(0, 0, w, h); #set the viewport to the current window specifications
    glMatrixMode(GL_PROJECTION); #set the matrix to projection

    glLoadIdentity();
    gluPerspective(60, w / h, 1.0, 1000.0)
    #set the perspective (angle of sight, width, height, , depth)
    glMatrixMode(GL_MODELVIEW); #set the matrix back to model

def keyboard (key, x, y):
    global xrot, xpos, ypos, zpos, xrot, yrot, angle, lastx, lasty, positionz, positionx
    if (key=='q'):
        xrot += 1
        if (xrot >360):
            xrot -= 360
    if (key=='z'):
        xrot -= 1;
        if (xrot < -360): xrot += 360
    if (key=='w'):
        yrotrad = (yrot / 180 * 3.141592654)
        xrotrad = (xrot / 180 * 3.141592654)
        xpos += float(sin(yrotrad))
        zpos -= float(cos(yrotrad))
        ypos -= float(sin(xrotrad))
    if (key=='s'):
        yrotrad = (yrot / 180 * 3.141592654)
        xrotrad = (xrot / 180 * 3.141592654)
        xpos -= float(sin(yrotrad))
        zpos += float(cos(yrotrad))
        ypos += float(sin(xrotrad))
    if (key=='d'):
        yrotrad = (yrot / 180 * 3.141592654)
        xpos += float(cos(yrotrad)) * 0.2
        zpos += float(sin(yrotrad)) * 0.2
    if (key=='a'):
        yrotrad = (yrot / 180 * 3.141592654)
        xpos -= float(cos(yrotrad)) * 0.2
        zpos -= float(sin(yrotrad)) * 0.2
    if (key==27):
        sys.exit(0)

def mouseMovement(x, y):
    global lastx, lasty, xrot, yrot
    diffx=x-lastx #check the difference between the current x and the last x position
    diffy=y-lasty #check the difference between the current y and the last y position
    lastx=x #set lastx to the current x position
    lasty=y #set lasty to the current y position
    xrot += float(diffy) #set the xrot to xrot with the addition of the difference in the y position
    yrot += float(diffx) #set the xrot to yrot with the addition of the difference in the x position

glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_DEPTH)
glutInitWindowSize(500, 500)
glutInitWindowPosition (100, 100)
glutCreateWindow("A basic OpenGL Window")
init()
glutDisplayFunc(display)
glutIdleFunc(display)
glutReshapeFunc(reshape)
#glutPassiveMotionFunc(mouseMovement)
#check for mouse movement
glutKeyboardFunc (keyboard)
glutMainLoop()