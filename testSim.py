import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

verticies = (
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, -1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, -1, 1),
    (-1, 1, 1)
    )

edges = (
    (0,1),
    (0,3),
    (0,4),
    (2,1),
    (2,3),
    (2,7),
    (6,3),
    (6,4),
    (6,7),
    (5,1),
    (5,4),
    (5,7)
    )


def Cube():
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(verticies[vertex])
    glEnd()

rotateToggle = 0
keyDown = []

def NewInput():
    global rotateToggle
    global keyDown

    for event in pygame.event.get():
        print(event)

        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        if event.type == pygame.KEYDOWN:
            keyDown.append(event.key)

        if event.type == pygame.KEYUP:
            keyDown.remove(event.key)

        if event.type == pygame.MOUSEMOTION and rotateToggle:
            relx, rely = event.rel
            if relx != 0:
                glRotatef(relx/10.0,0.0,1.0,0.0)

            if rely != 0:
                glRotatef(rely/10.0,1.0,0.0,0.0)

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                rotateToggle = 0

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                rotateToggle = 1

            if event.button == 4:
                #glTranslatef(0,0,1.0)
                glScalef(1.1,1.1,1.1)

            if event.button == 5:
                #glTranslatef(0,0,-1.0)
                glScalef(0.9,0.9,0.9)

    #move out into action method?
    for key in keyDown:
        pygame.time.delay(10)
        if key == pygame.K_RIGHT:
            glTranslatef(-1,0,0)
        if key == pygame.K_LEFT:
            glTranslatef(1,0,0)
        if key == pygame.K_DOWN:
            glTranslatef(0,1,0)
        if key == pygame.K_UP:
            glTranslatef(0,-1,0)


def resetDisplay():
 
    glClearColor (0.0,0.0,0.0,1.0)
    glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
 
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity()
    glOrtho(0.0, 800.0, 600.0, 0.0, 0.0, 1.0)
 
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture)
 
    glBegin (GL_QUADS);
    glTexCoord2d(0.0,0.0); glVertex2d(0.0,0.0);
    glTexCoord2d(1.0,0.0); glVertex2d(1024.0,0.0);
    glTexCoord2d(1.0,1.0); glVertex2d(1024.0,512.0);
    glTexCoord2d(0.0,1.0); glVertex2d(0.0,512.0);
    glEnd();


def main():
    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)

    glTranslatef(0,0, -10)

    while True:
        
        resetDisplay()

        NewInput()
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        Cube()
        glTranslatef(0,0, -10)
        Cube()
        glTranslatef(0,0, -10)
        Cube()
        glTranslatef(0,0, 20)
        pygame.display.flip()
        pygame.time.wait(10)

main()