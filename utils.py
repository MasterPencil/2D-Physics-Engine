import numpy as np
import pygame as pg
from typing import Callable

class Circle():

    # mass, radius, restitution, position, velocity, acceleration, angle, angular velocity, angular acceleration
    def __init__(self, m:float, r:float, e:float, x:pg.Vector2, v:pg.Vector2, a:pg.Vector2, theta:float, omega:float, alpha:float):
        self.m = m
        self.r = r
        self.e = e
        self.x = x
        self.v = v
        self.a = a
        self.theta = theta
        self.omega = omega
        self.alpha = alpha

    # simulate the object
    def tick(self, dt:float, g:pg.Vector2, p:float, world_line_list:list, springs:list):

        ## collision handler

        for line in world_line_list:
            # geometry
            A = line.p1
            B = line.p2
            AB = B - A
            AC = self.x - A
            s = (AC.dot(AB)/AB.magnitude_squared())
            s = max([0,min([1,s])])
            P = A +s*AB
            PC = self.x - P
            overlap = self.r - PC.magnitude()

            if PC.magnitude() > 1e-6: # threshold
                overlap_vec = overlap * PC.normalize()
            else:
                overlap_vec = pg.Vector2(0, 0)

            ## resolve collision
            if 0 < overlap:
                if s == 0:
                    normal = -(self.x - A).normalize()
                elif s == 1:
                    normal = -(self.x - B).normalize()
                elif PC.dot(line.normal()) > 0:
                    normal = line.normal()
                elif PC.dot(line.normal()) < 0:
                    normal = -line.normal()

                self.x += overlap_vec

                ## jitter suppression
                if 1e-1 < self.v.magnitude():
                    v_0 = self.v
                    w_0 = self.omega
                    parallel = normal.rotate(-90)
                    I = 0.5*self.m*self.r**2
                    v_r = v_0 + pg.Vector2(-w_0*self.r,0)
                    j_r = -(1+self.e)*v_r.dot(normal)/(1/self.m)

                    self.v += (j_r/self.m)*normal
                    self.x += self.omega*self.r*normal.rotate(90)/2*dt
                    #self.omega = normal.cross(self.v)/self.r
                    
        ## RK45 integration

        self.a = acceleration(self,g,p,springs,pg.Vector2(0,0))

        kx1 = self.v
        kv1 = self.a

        kx2 = self.v + 0.5*dt*kv1
        kv2 = acceleration(self,g,p,springs,0.5*dt*kx1)

        kx3 = self.v + 0.5*dt*kv2
        kv3 = acceleration(self,g,p,springs,0.5*dt*kx2)

        kx4 = self.v + dt*kv3
        kv4 = acceleration(self,g,p,springs,dt*kx3)

        self.x += (dt/6)*(kx1 + 2*kx2 + 2*kx3 + kx4)
        self.v += (dt/6)*(kv1 + 2*kv2 + 2*kv3 + kv4)

        self.omega += self.alpha*dt
        self.theta += self.omega*dt

    ## display the object and its orientation
    def show(self, screen:pg.Surface, origin:pg.Vector2, camera:pg.Vector2):
        
        pg.draw.circle(screen, (255,255,255), display_position(origin, camera, self.x), self.r, 2)
        angle_marker = self.x + pg.Vector2(self.r, 0).rotate_rad(self.theta)
        pg.draw.line(screen, (255,255,255), display_position(origin, camera, self.x), display_position(origin, camera, angle_marker), 2)

class WorldLine():

    ## point 1, point 2
    def __init__(self, p1:pg.Vector2, p2:pg.Vector2):
        self.p1 = p1
        self.p2 = p2

    ## return the unit vector normal to the line
    def normal(self):
        vec = self.p2 - self.p1
        return vec.rotate(90).normalize()
    
    ## display line
    def show(self, screen:pg.Surface, origin:pg.Vector2, camera:pg.Vector2):

        # display: [origin_x - camera_x + position_x, originy + cameray - positiony]

        pg.draw.line(screen, (255,255,255), display_position(origin, camera, self.p1), display_position(origin, camera, self.p2), 4)

## render objects in the correct location on screen

def display_position(origin:pg.Vector2, camera:pg.Vector2, position:pg.Vector2):

    # [origin_x - camera_x + position_x, origin_y + camera_y - position_y]  

    return pg.Vector2(origin.x - camera.x + position.x,
                      origin.y + camera.y - position.y)

## determine an object's acceleration

# object, gravitational constant, air density, list of springs, tiny step in position
def acceleration(obj1:Circle, g:pg.Vector2, p:float, springs:list, dx:pg.Vector2):

    ## sum up spring forces

    F_s = pg.Vector2(0,0)
    for spring in springs:
        if obj1 == spring[0]:
            obj2 = spring[1]
        elif obj1 == spring[1]:
            obj2 = spring[0]
        else:
            continue                    # obj1 is not part of this spring

        l = spring[2]
        k = spring[3]
        d = obj2.x - obj1.x - dx
        d_mag = d.magnitude()

        if d_mag != 0:
            force_dir = d.normalize()
        else:
            force_dir = pg.Vector2(0, 0) # prevent division by zero

        stretch = d_mag - l              # how much the spring is stretched or compressed

        spring_force = (k * stretch) * force_dir
        F_s += spring_force

    ## quadratic air drag

    c_d = 0.47 # coefficient of drag of a sphere
    v = obj1.v
    if v.magnitude() != 0:
        mag = c_d*obj1.r*p*v.magnitude()**2
        F_d = -mag*obj1.v.normalize()
    else:
        F_d = pg.Vector2(0,0)
    # F = ma
    return g + (F_s + F_d)/obj1.m

## draw a spring

def draw_spring(screen:pg.Surface, cam:pg.Vector2, origin:pg.Vector2, p1:pg.Vector2, p2:pg.Vector2):

    d = p2 - p1
    d_mag = d.magnitude()
    x_draw = np.linspace(0,d_mag,50)
    y_draw = 5*np.sin(50*x_draw/d_mag)
    angle_draw = np.arctan2(d.x,d.y) + np.pi
    matrix = np.array([[-np.sin(angle_draw),np.cos(angle_draw)],
                       [-np.cos(angle_draw),-np.sin(angle_draw)]])
    point_list = np.column_stack((x_draw,y_draw)) @ matrix
    point_list[:,0] += origin.x + p1.x - cam.x
    point_list[:,1] += origin.y - p1.y + cam.y
    pg.draw.lines(screen,(255,255,255),False,point_list,1)