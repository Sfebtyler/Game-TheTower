import pygame
import random
import sys

pygame.font.init()
pygame.init()

start_ticks = pygame.time.get_ticks()
font = pygame.font.SysFont('Comic Sans MS', 30)
active = True
screenx = 800
screeny = 700
x = 0
y = screeny
clock = pygame.time.Clock()
screen = pygame.display.set_mode((screenx, screeny))

# mana coordinates
randx = random.randrange(screenx - 70)
randy = random.randrange(screeny - 70)
# target coordinates
targetrandx = random.randrange(screenx - 70)
targetrandy = random.randrange(screeny - 70)
radius = 30
manacount = 5
colorparam1 = random.randrange(255)
colorparam2 = random.randrange(255)
colorparam3 = random.randrange(255)
direction = ''
shot_x = -10
shot_y = -10
shoot = False
hitcount = 0
gravity = 0
jump = False
groundpos = screeny - 20


class Player(object):
    def createplayer(self):
        player = pygame.draw.rect(screen, (51, 125, 255), pygame.Rect(x, y, 20, 20))
        return player

    def set_gravity(self):
        global gravity
        global y
        global groundpos
        if y == groundpos:
            gravity = 0
        if y != groundpos and not jump:
            gravity += 1
            y += gravity
            if y < screeny - 60:
                gravity += 1
                y += gravity


class Mana(object):
    global randx
    global randy

    def generatemana(self):
        mana = pygame.draw.rect(screen, (212, 175, 55), pygame.Rect(randx, screeny - 20, 10, 10), 10)
        return mana

    def player_mana_collect(self):
        global randx
        global randy
        global manacount

        if Player().createplayer().colliderect(Mana().generatemana()):
            if manacount < 10:
                manacount += 1
                randx = random.randrange(10, screenx - 70)
                randy = random.randrange(10, screeny - 70)


class Target(object):

    def generatetarget(self):
        target = pygame.draw.rect(screen, (212, 0, 0), pygame.Rect(targetrandx, targetrandy, 30, 30), 30)
        return target

    def check_if_hit(self):
        global targetrandx
        global targetrandy
        global hitcount
        global shoot
        if shot.colliderect(Target().generatetarget()):
            targetrandx = random.randrange(screenx - 70)
            targetrandy = random.randrange(screeny - 70)
            shoot = False
            hitcount += 1
            print("target hit")



# Main Loop
while active:
    shot = pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(shot_x, shot_y, 5, 2), 1)
    seconds = (pygame.time.get_ticks() - start_ticks) / 1000
    pressed = pygame.key.get_pressed()

    # Exit Program
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    if pressed[pygame.K_ESCAPE]:
        sys.exit()

    # change background color
    if pressed[pygame.K_BACKSPACE]:
        colorparam1 = random.randrange(255)
        colorparam2 = random.randrange(255)
        colorparam3 = random.randrange(255)

    # Movement
    if pressed[pygame.K_UP]:
        direction = 'up'
    if pressed[pygame.K_DOWN]:
        y += 5
        direction = 'down'
    if pressed[pygame.K_LEFT]:
        x -= 5
        direction = 'left'
    if pressed[pygame.K_RIGHT]:
        x += 5
        direction = 'right'

    # jump
    if pressed[pygame.K_SPACE]:
        if not jump and y == groundpos:
            jump = True
    if jump:
        y -= 5
        if y <= screeny - 60:
            jump = False


    # border
    if x < 0:
        x = 0
    if y < 0:
        y = 0
    if x > screenx - 20:
        x = screenx - 20
    if y > screeny - 20:
        y = screeny - 20

    screen.fill((colorparam1, colorparam2, colorparam3))

    # shoot
    if not shoot:
        if pressed[pygame.K_LSHIFT] and manacount > 0:
            manacount -= 1
            shot_direction = direction
            shot_x = x
            shot_y = y
            shoot = True

    # move shot
    if shoot:
        shot_speed = 10
        if shoot:
            pygame.draw.rect(screen, (255, 255, 255), shot)
        if shot_direction == 'right':
            shot_x += shot_speed
        if shot_direction == 'left':
            shot_x -= shot_speed
        if shot_direction == 'up':
            shot_y -= shot_speed
        if shot_direction == 'down':
            shot_y += shot_speed

        # garbage collection on shot
        if shot_x > screenx or shot_y > screeny or shot_x < 0 or shot_y < 0:
            shot_x = -10
            shot_y = -10
            shoot = False

    Mana().generatemana()
    Player().createplayer()
    Mana().player_mana_collect()
    Target().generatetarget()
    Target().check_if_hit()
    Player().set_gravity()
    textsurface = font.render(str(hitcount), False, (255, 246, 55))
    screen.blit(textsurface, (screenx - 50, 0))

    # mana bar
    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(10, 10, 10 * manacount, 20))
    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(8, 8, 104, 24), 1)

    pygame.display.flip()
    clock.tick(60)
