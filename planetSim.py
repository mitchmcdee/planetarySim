import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

from PIL import Image
import numpy
import random
import os
os.chdir('/Users/mcdee/Uni/COSC3000/Planet Simulator/')

rotateToggle = 0
keyDown = []

def OldInput():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                x_move = direction_speed
            if event.key == pygame.K_RIGHT:
                x_move = -1*direction_speed

            if event.key == pygame.K_UP:
                y_move = -1*direction_speed
            if event.key == pygame.K_DOWN:
                y_move = direction_speed


        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                x_move = 0

            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                y_move = 0

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                rotateToggle = 1

            if event.button == 4:
                glTranslatef(0,0,10.0)
                #glScalef(1.1,1.1,1.1)

            if event.button == 5:
                glTranslatef(0,0,-10.0)
                #glScalef(0.9,0.9,0.9)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                glTranslatef(0,0,1.0)

            if event.button == 5:
                glTranslatef(0,0,-1.0)

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
                glTranslatef(0,0,20.0)
                #glScalef(1.1,1.1,1.1)

            if event.button == 5:
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
        

def TexFromPNG(filename):
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

class Sphere(object):
    def __init__(self, placement):
        """Draws a centered sphere with radius s in given color."""

        self.x_pos = placement[0]
        self.y_pos = placement[1]
        self.z_pos = placement[2]

        glTranslatef(self.x_pos, self.y_pos, self.z_pos)

        quad = gluNewQuadric()
        gluQuadricNormals(quad, GLU_SMOOTH)
        gluQuadricTexture(quad,GL_TRUE)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, placement[3])
        gluSphere(quad,placement[4],100,100)
        glDisable(GL_TEXTURE_2D)

        glTranslatef(-self.x_pos, -self.y_pos, -self.z_pos)
    
    def getKey(self):
        return self.z_pos



def set_placement(texture, max_distance, min_distance = -20, camera_x = 0, camera_y = 0):

    camera_x = -1*int(camera_x)
    camera_y = -1*int(camera_y)

    new_placement = [0,0,0,0,0]
    
    new_placement[0] = random.randrange(camera_x-150,camera_x+150)
    new_placement[1] = random.randrange(camera_y-150,camera_y+150)
    new_placement[2] = random.randrange(-1*max_distance,min_distance)
    new_placement[3] = texture
    new_placement[4] = random.randrange(0,30)

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
    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)

    max_distance = 5000
    
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0]/display[1]), 0.1, 5000000)
    glTranslatef(0,0, -40)

    x_move = 0
    y_move = 0

    cur_x = 0
    cur_y = 0

    game_speed = 0.1
    direction_speed = 2

    background = TexFromPNG(os.path.join("images","bg.png"))

    bodies = []
    bodies.append(TexFromPNG(os.path.join("images","planet1.png")))
    bodies.append(TexFromPNG(os.path.join("images","planet2.png")))
    bodies.append(TexFromPNG(os.path.join("images","planet3.png")))
    bodies.append(TexFromPNG(os.path.join("images","planet4.png")))
    bodies.append(TexFromPNG(os.path.join("images","planet5.png")))
    bodies.append(TexFromPNG(os.path.join("images","planet6.png")))
    bodies.append(TexFromPNG(os.path.join("images","planet7.png")))
    bodies.append(TexFromPNG(os.path.join("images","planet8.png")))
    bodies.append(TexFromPNG(os.path.join("images","planet9.png")))

    sphere_list = []

    for x in range(100):
        sphere_list.append(set_placement(bodies[random.randrange(0,len(bodies))],max_distance))
    
    sphere_list.sort(key=lambda x: x[2])

    while True:
        #resetDisplay(background)

        glClearColor (0.0,0.0,0.0,1.0)
        glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
        
        NewInput()
                
        x = glGetDoublev(GL_MODELVIEW_MATRIX)
        
        camera_x = x[3][0]
        camera_y = x[3][1]
        camera_z = x[3][2]

        
        cur_x += x_move
        cur_y += y_move

        glTranslatef(x_move,y_move,game_speed)


        for each_sphere in sphere_list:
            Sphere(each_sphere)

        for i,each_sphere in enumerate(sphere_list):
            if camera_z <= each_sphere[2]:
                new_max = int(-1*(camera_z-(max_distance*2)))
                #sphere_list.append(set_placement(bodies[random.randrange(0,len(bodies))],new_max,int(camera_z-max_distance), cur_x, cur_y))
                sphere_list[i] = set_placement(bodies[random.randrange(0,len(bodies))],new_max,int(camera_z-max_distance), cur_x, cur_y)   
        
        sphere_list.sort(key=lambda x: x[2])

        pygame.display.flip()


main()
pygame.quit()
quit()