import numpy as np
import pygame as pg
import utils as eg

def main():

    ## create circles (m, r, e, x, v, a, theta, omega, alpha)

    circle_0 = eg.Circle(5, 30, 0.5, pg.Vector2(-50,0), pg.Vector2(100,100), pg.Vector2(0,0), 0,0,0)
    circle_1 = eg.Circle(5, 30, 0.7, pg.Vector2(50,0), pg.Vector2(100,100), pg.Vector2(0,0), 0,0,0)
    circle_2 = eg.Circle(5, 40, 0.8, pg.Vector2(-25,50), pg.Vector2(100,100), pg.Vector2(0,0), 0,0,0)
    circle_3 = eg.Circle(5, 40, 0.8, pg.Vector2(25,50), pg.Vector2(100,100), pg.Vector2(0,0), 0,0,0)

    circle_list = [circle_0,circle_1,circle_2,circle_3]

    ## create world lines defined by (point1, point2)

    world_line_0 = eg.WorldLine(pg.Vector2(-600,0), pg.Vector2(-100,-200))
    world_line_1 = eg.WorldLine(pg.Vector2(-100,-200), pg.Vector2(100,-200))
    world_line_2 = eg.WorldLine(pg.Vector2(100,-200), pg.Vector2(600,0))
    world_line_7 = eg.WorldLine(pg.Vector2(-600,0), pg.Vector2(-600,-220))
    world_line_8 = eg.WorldLine(pg.Vector2(600,0), pg.Vector2(600,-220))
    world_line_9 = eg.WorldLine(pg.Vector2(-600,-220), pg.Vector2(600,-220))
    world_line_3 = eg.WorldLine(pg.Vector2(-500,100), pg.Vector2(500,100))
    world_line_4 = eg.WorldLine(pg.Vector2(-500,120), pg.Vector2(500,120))
    world_line_5 = eg.WorldLine(pg.Vector2(-500,100), pg.Vector2(-500,120))
    world_line_6 = eg.WorldLine(pg.Vector2(500,100), pg.Vector2(500,120))
    world_line_10 = eg.WorldLine(pg.Vector2(600,0), pg.Vector2(20000,-15000))

    world_line_list = [world_line_0,world_line_1,world_line_2,world_line_3,world_line_4,world_line_5,world_line_6,world_line_7,world_line_8,world_line_9]

    ## spring together objects [ [obj1, obj2 length, spring constant, dampening coefficient], [...], ...]

    springs = [
        [circle_2,circle_3,50,100],
        [circle_0,circle_3,(circle_3.x-circle_0.x).magnitude(),500],
        [circle_1,circle_2,(circle_2.x-circle_1.x).magnitude(),500],
        [circle_0,circle_2,(circle_2.x-circle_0.x).magnitude(),100],
        [circle_1,circle_3,(circle_3.x-circle_1.x).magnitude(),100],
        [circle_0,circle_1,(circle_0.x-circle_1.x).magnitude(),500]
        ]

    ## define constants

    g = pg.Vector2(0,-100) # flat gravity
    p = 0.005 # air density

    ## launch pygame

    # display
    window = pg.Vector2(1366,768)
    screen = pg.display.set_mode(window)
    origin = pg.Vector2(screen.get_width()/2, screen.get_height()/2)
    camera = pg.Vector2(0,0)

    # time and tick speed
    clock = pg.time.Clock()
    t = 0
    dt = 1
    maxfps = 120
    t_ratio = 1 # t_simulation / t_real_life

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        ## caption
        caption = 'FPS: {} / {}, t = {}s'.format(np.round(clock.get_fps(),2),maxfps,np.round(t,2))
        pg.display.set_caption(caption)

        ## clock
        dt = clock.tick(maxfps)*(t_ratio/1000)
        t += dt

        ## keyboard inputs
        keys = pg.key.get_pressed()
        # camera motion
        if keys[pg.K_w]: 
            camera.y += 10
        if keys[pg.K_a]: 
            camera.x += -10
        if keys[pg.K_s]: 
            camera.y += -10
        if keys[pg.K_d]: 
            camera.x += 10
        if keys[pg.K_RIGHT]:
            circle_0.omega -= 0.1
            circle_1.omega -= 0.1
        if keys[pg.K_LEFT]:
            circle_0.omega += 0.1
            circle_1.omega += 0.1

        ## run simulation and render scene

        screen.fill((0,0,0))
        for circle in circle_list:
            # simulate objects
            circle.tick(dt,g,p,world_line_list,springs,)
            # draw objects
            circle.show(screen,origin,camera)

        for line in world_line_list:
            # draw world lines
            line.show(screen,origin,camera)

        # draw springs
        for spring in springs:
            eg.draw_spring(screen,camera,origin,spring[0].x,spring[1].x)

        pg.display.update()

if __name__ == '__main__':
    main()
    pg.quit()