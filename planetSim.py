import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

from PIL import Image
import numpy
import random
import os
os.chdir('/Users/mcdee/Uni/COSC3000/Planet Simulator/')

#Global variables
speedZoomToggle = 0
rotateToggle = 0
keyDown = []

#Global constants
BACKGROUND_SPHERE_RADIUS = 100000
NUM_BODIES = 200
MAX_BODY_RADIUS = 300
NEAR_CLIP_DISTANCE = 0.01
FAR_CLIP_DISTANCE = 1000000
RENDER_DISTANCE = 10000
FIELD_OF_VIEW = 45
NUM_RENDER_LINES = 80

def NewInput():
    global rotateToggle, keyDown, speedZoomToggle

    for event in pygame.event.get():
        print(event)

        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LSHIFT:
                speedZoomToggle = 1
            else:
                keyDown.append(event.key)

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LSHIFT:
                speedZoomToggle = 0
            else:
                keyDown.remove(event.key)

        if event.type == pygame.MOUSEMOTION and rotateToggle:
            relx, rely = event.rel
            if relx != 0:
                glRotatef(relx/5.0,0.0,1.0,0.0)

            if rely != 0:
                glRotatef(rely/5.0,1.0,0.0,0.0)

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                rotateToggle = 0

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                rotateToggle = 1

            if event.button == 4:
                if speedZoomToggle:
                    glTranslatef(0,0,200.0)
                else:
                    glTranslatef(0,0,20.0)
                #glPushMatrix()
                #glLoadIdentity()
                #glScalef(1.1,1.1,1.1)
                #glPopMatrix()

            if event.button == 5:
                if speedZoomToggle:
                    glTranslatef(0,0,-200.0)
                else:
                    glTranslatef(0,0,-20.0)
                #glScalef(0.9,0.9,0.9)

    #move out into action method?
    for key in keyDown:
        pygame.time.delay(10)
        if key == pygame.K_RIGHT:
            glTranslatef(-20,0,0)
        if key == pygame.K_LEFT:
            glTranslatef(20,0,0)
        if key == pygame.K_DOWN:
            glTranslatef(0,20,0)
        if key == pygame.K_UP:
            glTranslatef(0,-20,0)
        

def TextureFromImage(filename):
    img = Image.open(filename)
    img_data = numpy.array(list(img.getdata()), numpy.uint8)

    texture = glGenTextures(1)
    glPixelStorei(GL_UNPACK_ALIGNMENT,1)
    glBindTexture(GL_TEXTURE_2D, texture)

    # Texture parameters are part of the texture object, so you need to 
    # specify them only once for a given texture object.
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.size[0], img.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    return texture

def Sphere(placement):
    global NUM_RENDER_LINES
    """Draws a centered sphere with radius s in given color."""

    x_pos = placement[0]
    y_pos = placement[1]
    z_pos = placement[2]
    texture = placement[3]
    radius = placement[4]

    glTranslatef(x_pos, y_pos, z_pos)

    quad = gluNewQuadric()
    gluQuadricNormals(quad, GLU_SMOOTH)
    gluQuadricTexture(quad, GL_TRUE)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture)
    gluSphere(quad, radius, NUM_RENDER_LINES, NUM_RENDER_LINES)
    glDisable(GL_TEXTURE_2D)

    glTranslatef(-x_pos, -y_pos, -z_pos)

def biasRandom(massDist):
    randRoll = random.random() # in [0,1)
    sum = 0
    result = 1
    for mass in massDist:
        sum += mass
        if randRoll < sum:
            return result
        result+=1

#TODO(mitch): Add in ability to have absolute placement?
def set_placement(texture, render_distance, absolute = False):
    global MAX_BODY_RADIUS
    new_placement = []
    
    new_placement.append(random.randrange(-(render_distance / 2),(render_distance / 2)))
    new_placement.append(random.randrange(-(render_distance / 2),(render_distance / 2)))
    new_placement.append(random.randrange(-(render_distance / 2),(render_distance / 2)))
    new_placement.append(texture)
    #inverse transform sampling to the 10th root.
    new_placement.append(MAX_BODY_RADIUS * (1 - (1 - random.random())**(1.0/10.0)))

    return new_placement


def resetDisplay(texture):
 
    glClearColor (0.0,0.0,0.0,1.0)
    glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
 
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity()
    glOrtho(0.0, 800.0, 600.0, 0.0, 0.0, 1.0)
 
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture)
 
    glColor3f(1.0,1.0,1.0)
    glBegin (GL_QUADS)
    glTexCoord2d(0.0,0.0); glVertex2d(0.0,0.0)
    glTexCoord2d(1.0,0.0); glVertex2d(800.0,0.0)
    glTexCoord2d(1.0,1.0); glVertex2d(800.0,600.0)
    glTexCoord2d(0.0,1.0); glVertex2d(0.0,600.0)
    glEnd()

    glDisable(GL_TEXTURE_2D)
    glEnable(GL_DEPTH_TEST)
    glDepthMask(GL_TRUE)

    glMatrixMode(GL_MODELVIEW)
    glOrtho(0.0, 800.0, 600.0, 0.0, 0.0, 1.0)


def main():
    global RENDER_DISTANCE, FIELD_OF_VIEW, NEAR_CLIP_DISTANCE, FAR_CLIP_DISTANCE, \
            NUM_BODIES, BACKGROUND_SPHERE_RADIUS

    #TODO(mitch): make init method?

    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_ALWAYS)
    
    glMatrixMode(GL_PROJECTION)
    gluPerspective(FIELD_OF_VIEW, (display[0]/display[1]), NEAR_CLIP_DISTANCE, FAR_CLIP_DISTANCE)
    
    #Starting view position
    #glTranslatef(0,0, RENDER_DISTANCE / 2)

    game_speed = 0.1
    x_move = 0
    y_move = 0
    sphere_list = []
    bodies = []

    background = TextureFromImage(os.path.join("images","bg.png"))

    bodies.append(TextureFromImage(os.path.join("images","planet1.png")))
    bodies.append(TextureFromImage(os.path.join("images","planet2.png")))
    bodies.append(TextureFromImage(os.path.join("images","planet3.png")))
    bodies.append(TextureFromImage(os.path.join("images","planet4.png")))
    bodies.append(TextureFromImage(os.path.join("images","planet5.png")))
    bodies.append(TextureFromImage(os.path.join("images","planet6.png")))
    bodies.append(TextureFromImage(os.path.join("images","planet7.png")))
    bodies.append(TextureFromImage(os.path.join("images","planet8.png")))
    bodies.append(TextureFromImage(os.path.join("images","planet9.png")))


    #generate spheres TODO(mitch): add in random chance for moon, add in clusters?
    for x in range(NUM_BODIES):
        sphere_list.append(set_placement(bodies[random.randrange(0,len(bodies))], RENDER_DISTANCE))
    
    #Sort spheres in order of their z-distance TODO(mitch): change to distance from cam?
    sphere_list.sort(key=lambda x: x[2])

    while True:
        #resetDisplay(background)

        #Clear display
        glClearColor(0.0,0.0,0.0,1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
        
        #Get and react to user input
        NewInput()

        #Draw background
        Sphere([0, 0, 0, background, BACKGROUND_SPHERE_RADIUS])

        #Move spheres
        glTranslatef(x_move,y_move,game_speed)

        #Draw all spheres
        for each_sphere in sphere_list:
            Sphere(each_sphere)

        #Flip display buffer
        pygame.display.flip()


main()
pygame.quit()
quit()