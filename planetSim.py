import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

from PIL import Image
from math import *
import numpy
import random
import os
os.chdir('/Users/mcdee/Uni/COSC3000/Planet Simulator/')

##########################################################################
# Global constants, DON'T CHANGE THESE UNLESS YOU KNOW WHAT YOU'RE DOING #
##########################################################################

BACKGROUND_SPHERE_RADIUS = 100000
WINDOW_RES = (1440, 900) #window resolution of the window
NEAR_CLIP_DISTANCE = 0.01 #near clipping distance
FAR_CLIP_DISTANCE = 100000 #far clipping distance
NUM_RENDER_LINES = 100 #number of render lines per sphere (both slice and stack)
FIELD_OF_VIEW = 45 #field of view for the viewing camera

##################################################
# Global constants, CHANGE THESE ALL YOU LIKE :) #
##################################################

RENDER_DISTANCE = 400 #length and width of the 2D square that celestial bodies will generate in
SIZE_FACTOR = 1.0 / 3.0 #size bias factor (lower number, less large radius planets)
MASS_FACTOR = 1.0 / 5.0 #mass bias factor (lower number, less large mass planets)
MAX_BODY_RADIUS = 3 #maximum radius of celestial bodies
MAX_BODY_MASS = 400 #maximum mass of celestial bodies
NUM_BODIES = 60 #number of celestial bodies (advised limit: 200)




#Global variables, DO NOT TOUCH
backgroundToggle = 0
speedZoomToggle = 0
rotateToggle = 0
keyDown = []
bodies = []
sphere_list = []
t, dt = 0., .0005 #3 is good

# The density of the planets - used to calculate their mass
# from their volume (i.e. via their radius)
DENSITY = 0.01 #0.001

# The gravity coefficient
GRAVITYSTRENGTH = 2.e8 #1.e2 is good

class State:
    """Class representing position and velocity."""
    def __init__(self, x, y, vx, vy):
        self._x, self._y, self._vx, self._vy = x, y, vx, vy

    def __repr__(self):
        return 'x:{x} y:{y} vx:{vx} vy:{vy}'.format(
            x=self._x, y=self._y, vx=self._vx, vy=self._vy)


class Derivative:
    """Class representing velocity and acceleration."""
    def __init__(self, dx, dy, dvx, dvy):
        self._dx, self._dy, self._dvx, self._dvy = dx, dy, dvx, dvy

    def __repr__(self):
        return 'dx:{dx} dy:{dy} dvx:{dvx} dvy:{dvy}'.format(
            dx=self._dx, dy=self._dy, dvx=self._dvx, dvy=self._dvy)

def GetInput(sphere_list, blackhole):
    global rotateToggle, keyDown, speedZoomToggle, dt, backgroundToggle

    for event in pygame.event.get():
        #print(event)

        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_t:
                backgroundToggle = not backgroundToggle
            elif event.key == pygame.K_q:
                pygame.quit()
                quit()
            elif event.key == pygame.K_LSHIFT:
                speedZoomToggle = 1
            else:
                keyDown.append(event.key)

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_t:
                continue
            elif event.key == pygame.K_LSHIFT:
                speedZoomToggle = 0
            else:
                keyDown.remove(event.key)

        if event.type == pygame.MOUSEMOTION and rotateToggle:
            relx, rely = event.rel
            if relx != 0:
                glRotatef(relx/5.0, 0.0, 1.0, 0.0)

            if rely != 0:
                glRotatef(rely/5.0, 1.0, 0.0, 0.0)

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                rotateToggle = 0

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                rotateToggle = 1

            if event.button == 4:
                if speedZoomToggle:
                    glTranslatef(0, 0, 20.0)
                else:
                    glTranslatef(0, 0, 2.0)

            if event.button == 5:
                if speedZoomToggle:
                    glTranslatef(0, 0, -20.0)
                else:
                    glTranslatef(0, 0, -2.0)

    #move out into action method? or move back in ^^ ?
    for key in keyDown:
        pygame.time.delay(10)
        if key == pygame.K_RIGHT:
            glTranslatef(-2, 0, 0)
        if key == pygame.K_LEFT:
            glTranslatef(2, 0, 0)
        if key == pygame.K_DOWN:
            glTranslatef(0, 2, 0)
        if key == pygame.K_UP:
            glTranslatef(0, -2, 0)
        if key == pygame.K_w:
            if (dt == 0):
                pygame.time.delay(1000)
            elif (dt >= -0.001):
                dt += 0.0001
            else:
                dt += 0.001
        if key == pygame.K_s:
            if (dt == 0):
                pygame.time.delay(1000)
            elif (dt <= 0.001):
                dt -= 0.0001
            else:
                dt -= 0.001
        if key == pygame.K_m:
            sphere_list.append(Sphere())


        

def TextureFromImage(filename):
    img = Image.open(filename)
    img_data = numpy.array(list(img.getdata()), numpy.uint8)

    texture = glGenTextures(1)
    glPixelStorei(GL_UNPACK_ALIGNMENT,1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR_MIPMAP_NEAREST) #trilinear filtering
    gluBuild2DMipmaps(GL_TEXTURE_2D,3, img.size[0], img.size[1], GL_RGB, GL_UNSIGNED_BYTE, img_data
    )
    return texture



class Sphere():
    def __init__(self, texture = None, x_pos = None, \
            z_pos = None, radius = None, mass = None):

        global bodies, RENDER_DISTANCE, SIZE_FACTOR, MASS_FACTOR, \
                MAX_BODY_RADIUS

        if (texture == None):
            texture = bodies[random.randrange(0,len(bodies))]

        if (x_pos == None):
            x_pos = random.randrange(-(RENDER_DISTANCE / 2), \
            (RENDER_DISTANCE / 2))

        if (z_pos == None):
            z_pos = random.randrange(-(RENDER_DISTANCE / 2), \
            (RENDER_DISTANCE / 2))

        if (radius == None):
            radius = MAX_BODY_RADIUS * \
            (1 - (1 - max(random.random(), 0.3))**(SIZE_FACTOR))

        if (mass == None):
            mass = MAX_BODY_MASS * \
            (1 - (1 - max(random.random(), 0.3))**(MASS_FACTOR))

        self._r = radius;
        self._st = State(
               float(x_pos),
               float(z_pos),
               float(-0.01 + random.randint(0, 1)/100.), #velocity x
               float(-0.01 + random.randint(0, 1)/100.)) #velocity y

        self._text = texture
        self.setMassFromRadius()
        self._merged = False

    def __repr__(self):
        return repr(self._st)

    def acceleration(self, state, unused_t):
        """Calculate acceleration caused by other planets on this one."""
        ax = 0.0
        ay = 0.0
        for p in sphere_list:
            if p is self or p._merged:
                continue  # ignore ourselves and merged planets
            dx = p._st._x - state._x
            dy = p._st._y - state._y
            dsq = dx*dx + dy*dy  # distance squared
            dr = sqrt(dsq)  # distance
            force = GRAVITYSTRENGTH*self._m*p._m/dsq if dsq>1e-10 else 0.
            # Accumulate acceleration...
            ax += force*dx/dr
            ay += force*dy/dr
        return (ax, ay)

    def initialDerivative(self, state, t):
        """Part of Runge-Kutta method."""
        ax, ay = self.acceleration(state, t)
        return Derivative(state._vx, state._vy, ax, ay)

    def nextDerivative(self, initialState, derivative, t, dt):
        """Part of Runge-Kutta method."""
        state = State(0., 0., 0., 0.)
        state._x = initialState._x + derivative._dx*dt
        state._y = initialState._y + derivative._dy*dt
        state._vx = initialState._vx + derivative._dvx*dt
        state._vy = initialState._vy + derivative._dvy*dt
        ax, ay = self.acceleration(state, t+dt)
        return Derivative(state._vx, state._vy, ax, ay)

    def updatePlanet(self, t, dt):
        """Runge-Kutta 4th order solution to update planet's pos/vel."""
        a = self.initialDerivative(self._st, t)
        b = self.nextDerivative(self._st, a, t, dt*0.5)
        c = self.nextDerivative(self._st, b, t, dt*0.5)
        d = self.nextDerivative(self._st, c, t, dt)
        dxdt = 1.0/6.0 * (a._dx + 2.0*(b._dx + c._dx) + d._dx)
        dydt = 1.0/6.0 * (a._dy + 2.0*(b._dy + c._dy) + d._dy)
        dvxdt = 1.0/6.0 * (a._dvx + 2.0*(b._dvx + c._dvx) + d._dvx)
        dvydt = 1.0/6.0 * (a._dvy + 2.0*(b._dvy + c._dvy) + d._dvy)
        self._st._x += dxdt*dt
        self._st._y += dydt*dt
        self._st._vx += dvxdt*dt
        self._st._vy += dvydt*dt
        if abs(self._st._x) > 500 or abs(self._st._y) > 500:
            self._merged = True

    def drawSphere(self):
        glTranslatef(self._st._x, 0, self._st._y)

        quad = gluNewQuadric()
        gluQuadricNormals(quad, GLU_SMOOTH)
        gluQuadricTexture(quad, GL_TRUE)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self._text)
        gluSphere(quad, self._r, NUM_RENDER_LINES, NUM_RENDER_LINES)
        glDisable(GL_TEXTURE_2D)

        glTranslatef(-self._st._x, 0, -self._st._y)

    def setMassFromRadius(self):
        """From _r, set _m: The volume is (4/3)*Pi*(r^3)..."""
        self._m = DENSITY*4.*pi*(self._r**3.)/3.

    def setRadiusFromMass(self):
        """Reversing the setMassFromRadius formula, to calculate radius from
        mass (used after merging of two planets - mass is added, and new
        radius is calculated from this)"""
        self._r = (3.*self._m/(DENSITY*4.*pi))**(0.3333)


def initialise():
    global bodies, RENDER_DISTANCE, FIELD_OF_VIEW, NEAR_CLIP_DISTANCE, \
            FAR_CLIP_DISTANCE, WINDOW_RES

    pygame.init()
    pygame.display.set_mode(WINDOW_RES, DOUBLEBUF|OPENGL|NOFRAME);
    
    glMatrixMode(GL_PROJECTION)
    gluPerspective(FIELD_OF_VIEW, (WINDOW_RES[0] / WINDOW_RES[1]), \
            NEAR_CLIP_DISTANCE, FAR_CLIP_DISTANCE)

    #loop through textures folder and grab all body textures.
    for file in os.listdir("textures"):
        if file.startswith("body") and file.endswith(".png"):
            bodies.append(TextureFromImage(os.path.join("textures",file)))

def planetsTouch(p1, p2):
    dx = p1._st._x - p2._st._x
    dy = p1._st._y - p2._st._y
    dsq = dx*dx + dy*dy
    dr = sqrt(dsq)
    return dr<=(p1._r + p2._r)


def main():
    global NUM_BODIES, BACKGROUND_SPHERE_RADIUS

    initialise()
    
    backgroundSphere = Sphere(TextureFromImage(os.path.join("textures", \
            "bg.png")), 0, 0, 100000, 0)

    #generate spheres
    for x in range(NUM_BODIES):
        sphere_list.append(Sphere())

    blackhole = Sphere(TextureFromImage(os.path.join("textures", \
            "bhole.png")), 0, 0, MAX_BODY_RADIUS, MAX_BODY_MASS)
    blackhole._st._x, blackhole._st._y = 0, 0
    blackhole._st._vx = blackhole._st._vy = 0.
    blackhole._m *= 0.8
    blackhole.setRadiusFromMass()
    sphere_list.append(blackhole)

    for p in sphere_list:
        if p is blackhole:
            continue
        if planetsTouch(p, blackhole):
            p._merged = True  # ignore planets inside the blackhole
    
    #Sort spheres in order of their z-distance for accurate overlaying
    sphere_list.sort(key=lambda sphere: sphere._st._y)

    #start position
    glTranslatef(0, -5, -50)

    while True:
        #Clear display
        glClearColor(.2, .2, .2, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        
        #Get and react to user input
        GetInput(sphere_list, blackhole)

        #Toggle background
        if not backgroundToggle:
            backgroundSphere.drawSphere()

        for p1 in sphere_list:
            if p1._merged:
                continue
            for p2 in sphere_list:
                if p1 is p2 or p2._merged:
                    continue
                if planetsTouch(p1, p2):
                    if p1._m < p2._m:
                        p1, p2 = p2, p1  # p1 is the biggest one (mass-wise)
                    p2._merged = True
                    p1._m += p2._m  # maintain the mass (just add them)
                    p1.setRadiusFromMass()  # new mass --> new radius
                    if p1 is blackhole:
                        continue  # No-one can move the blackhole :-)
                    newvx = (p1._st._vx*p1._m+p2._st._vx*p2._m)/(p1._m+p2._m)
                    newvy = (p1._st._vy*p1._m+p2._st._vy*p2._m)/(p1._m+p2._m)
                    p1._st._vx, p1._st._vy = newvx, newvy

        #Draw all spheres
        for p in sphere_list:
            if not p._merged:
                p.drawSphere()
                if p is not blackhole:
                    p.updatePlanet(t, dt)
            else:
                sphere_list.remove(p)
                sphere_list.append(Sphere())


        #Sort spheres in order of their z-distance for accurate overlaying
        sphere_list.sort(key=lambda sphere: sphere._st._y)

        #Flip display buffer
        pygame.display.flip()


main()
pygame.quit()
quit()