import pygame
import time
import sprite_engine
import random

pygame.init()

# preloading sprites to improve performance
tiles_sprite_sheet = pygame.image.load('sprites/ruin_tiles.png').convert()
tiles_sprite_sheet_5 = pygame.image.load("sprites/225839_hyptosis_tile-art-batch-5.png")

fireball_frames = [
    pygame.transform.scale(pygame.image.load("sprites/Flames/fireball/fireball_0001.png"), (20, 20)).convert(),
    pygame.transform.scale(pygame.image.load("sprites/Flames/fireball/fireball_0002.png"), (20, 20)).convert(),
    pygame.transform.scale(pygame.image.load("sprites/Flames/fireball/fireball_0003.png"), (20, 20)).convert(),
    pygame.transform.scale(pygame.image.load("sprites/Flames/fireball/fireball_0004.png"), (20, 20)).convert(),
    pygame.transform.scale(pygame.image.load("sprites/Flames/fireball/fireball_0005.png"), (20, 20)).convert(),
    pygame.transform.scale(pygame.image.load("sprites/Flames/fireball/fireball_0006.png"), (20, 20)).convert()
]

explosion_frames = [pygame.transform.scale(pygame.image.load("sprites/fireball.png"), (40, 40)),
                       pygame.transform.scale(pygame.image.load("sprites/fireball.png"), (50, 50)),
                       pygame.transform.scale(pygame.image.load("sprites/fireball.png"), (60, 60))]

portal_spritesheet = pygame.image.load("sprites/portal.png").convert()

up = down = left = right = running = False

# custom events
invincibility_timer = pygame.USEREVENT + 1
reset_after_lose = pygame.USEREVENT + 2
explosion_timer = pygame.USEREVENT + 3

# Sprite Groups
all_sprites_list = pygame.sprite.Group()
enemy_list = pygame.sprite.Group()
fireball_list = pygame.sprite.Group()
mana_list = pygame.sprite.Group()
health_list = pygame.sprite.Group()
wall_list = pygame.sprite.Group()
explosion_list = pygame.sprite.Group()


class Player(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.health = 3
        self.image = pygame.Surface([20, 20])
        self.image.fill((51, 125, 255))
        self.rect = self.image.get_rect()
        self.onGround = False
        self.xvel = 0
        self.yvel = 0
        self.rect.x = x
        self.rect.y = y
        self.invincible = False
        self.go_through_plat = False

    def update(self, jump, down, left, right, wall_list, cur_level, screenx, screeny):
        if jump:
            # only jump if on the ground
            if self.onGround:
                self.yvel -= 10
        else:
            pass
        if left:
            self.xvel = -8
        if right:
            self.xvel = 8
        if not self.onGround:
            # only accelerate with gravity if in the air
            self.yvel += 0.6
            # max falling speed
            if self.yvel > 100:
                self.yvel = 100
        if not(left or right):
            self.xvel = 0
        # increment in x direction
        self.rect.left += self.xvel
        # do x-axis collisions
        self.collide(self.xvel, 0, wall_list)
        # increment in y direction
        self.rect.top += self.yvel
        # assuming we're in the air
        self.onGround = False
        # do y-axis collisions
        self.collide(0, self.yvel, wall_list)
        # reset go through plat
        if not down:
            self.go_through_plat = False
        for w in wall_list:
            if down and w.plat:
                self.go_through_plat = True

    def collide(self, xvel, yvel, wall_list):
        for w in wall_list:
            if pygame.sprite.collide_rect(self, w):
                # collide right
                if xvel > 0 and not w.plat:
                    self.rect.right = w.rect.left
                # collide left
                if xvel < 0 and not w.plat:
                    self.rect.left = w.rect.right
                if yvel > 0 and not self.go_through_plat:
                    self.rect.bottom = w.rect.top
                    self.onGround = True
                    self.yvel = 0
                if yvel < 0 and not w.plat:
                    self.rect.top = w.rect.bottom
                if not w.plat:
                    self.go_through_plat = False


class Enemy(pygame.sprite.Sprite):

    def __init__(self, x, y, en_type):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([18, 18])
        self.image.fill((255, 255, 255))
        self.health = 3
        self.yvel = 0
        self.xvel = 0
        self.enemy_type = en_type
        self.direction = 'left'
        self.direction_randomizer = random.randrange(2)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.onGround = False

    def collide(self, xvel, yvel, wall_list, screeny):
        for w in wall_list:
            if pygame.sprite.collide_rect(self, w):
                # collide right
                if xvel > 0 and not w.plat:
                    self.rect.right = w.rect.left
                # collide left
                if xvel < 0 and not w.plat:
                    self.rect.left = w.rect.right
                if yvel > 0:
                    self.rect.bottom = w.rect.top
                    self.onGround = True
                    self.yvel = 0
                if yvel < 0:
                    self.rect.top = w.rect.bottom
        if self.rect.bottom > screeny - 20:
            self.rect.y = screeny - 20
            self.onGround = True
            self.yvel = 0

    def update(self, jump, down, left, right, wall_list, cur_level, screenx, screeny):
        # set enemy direction
        if self.direction_randomizer == 1:
            self.direction = 'left'
        else:
            self.direction = 'right'

        # gravity for non flyer enemies
        if not self.onGround and not self.enemy_type == 'flyer':
            # only accelerate with gravity if in the air
            self.yvel += 0.3
            # max falling speed
            if self.yvel > 100:
                self.yvel = 100

            # increment in y direction
            self.rect.top += self.yvel
            # assuming we're in the air
            self.onGround = False
            # do y-axis collisions
            self.collide(0, self.yvel, wall_list, screeny)

        # standard enemy movement

        # if self.onGround:
        #     if self.direction == "left":
        #         self.xvel = -8
        #     if self.direction == "right":
        #         self.xvel = 8
        #     # increment in x direction
        #     self.rect.left += self.xvel
        #     # do x-axis collisions
        #     self.collide(self.xvel, 0, wall_list, screeny)
        #     # increment in y direction
        #     self.rect.top += self.yvel
        #     # assuming we're in the air
        #     self.onGround = False
        #     # do y-axis collisions
        #     self.collide(0, self.yvel, wall_list, screeny)


class Mana(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        image = pygame.image.load("sprites/health_mana_potion/mana_potion.png")

        self.image = pygame.transform.scale(image, (20, 20))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.onGround = False
        self.yvel = 0

    def collide(self, xvel, yvel, wall_list, screeny):
            for w in wall_list:
                if pygame.sprite.collide_rect(self, w):
                    if yvel > 0:
                        self.rect.bottom = w.rect.top
                        self.onGround = True
                        self.yvel = 0
                    if yvel < 0:
                        self.rect.top = w.rect.bottom
            if self.rect.bottom > screeny - 20:
                print('at the bottom')
                self.rect.y = screeny - 20
                self.onGround = True
                self.yvel = 0

    def update(self, jump, down, left, right, wall_list, cur_level, screenx, screeny):
        if not self.onGround:
            # only accelerate with gravity if in the air
            self.yvel += 0.3
            # max falling speed
            if self.yvel > 100:
                self.yvel = 100

            # increment in y direction
            self.rect.top += self.yvel
            # assuming we're in the air
            self.onGround = False
            # do y-axis collisions
            self.collide(0, self.yvel, wall_list, screeny)


class Health(pygame.sprite.Sprite):

    def __init__(self, x, y, screenx, screeny):
        pygame.sprite.Sprite.__init__(self)
        image = pygame.image.load("sprites/health_mana_potion/health_potion.png")

        self.image = pygame.transform.scale(image, (20, 20))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.onGround = False
        self.yvel = 0

    def collide(self, xvel, yvel, wall_list, screeny):
            for w in wall_list:
                if pygame.sprite.collide_rect(self, w):
                    if yvel > 0:
                        self.rect.bottom = w.rect.top
                        self.onGround = True
                        self.yvel = 0
                    if yvel < 0:
                        self.rect.top = w.rect.bottom
            if self.rect.bottom > screeny - 20:
                print('at the bottom')
                self.rect.y = screeny - 20
                self.onGround = True
                self.yvel = 0

    def update(self, jump, down, left, right, wall_list, cur_level, screenx, screeny):
        if not self.onGround:
            # only accelerate with gravity if in the air
            self.yvel += 0.3
            # max falling speed
            if self.yvel > 100:
                self.yvel = 100

            # increment in y direction
            self.rect.top += self.yvel
            # assuming we're in the air
            self.onGround = False
            # do y-axis collisions
            self.collide(0, self.yvel, wall_list, screeny)


class Portal(pygame.sprite.Sprite):

    def __init__(self, x, y, screenx, screeny):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([screenx / 20, screeny / 20 + screeny / 20])
        self.plat = False
        self.start_time = time.time()

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, jump, down, left, right, wall_list, cur_level, screenx, screeny):
        cur_seconds = time.time()

        if cur_seconds > self.start_time + .25:
            image = sprite_engine.sprite_sheet((110, 180), portal_spritesheet, (18, 61))
            for i in image:
                i.set_colorkey((0, 128, 0))
            self.image = pygame.transform.scale(image[0], (int(screenx / 20), int(screeny / 20 + screeny / 20)))
        if cur_seconds > self.start_time + .5:
            image = sprite_engine.sprite_sheet((110, 180), portal_spritesheet, (150, 61))
            for i in image:
                i.set_colorkey((0, 128, 0))
            self.image = pygame.transform.scale(image[0], (int(screenx / 20), int(screeny / 20 + screeny / 20)))
        if cur_seconds > self.start_time + .75:
            image = sprite_engine.sprite_sheet((110, 180), portal_spritesheet, (310, 24))
            for i in image:
                i.set_colorkey((0, 128, 0))
            self.image = pygame.transform.scale(image[0], (int(screenx / 20), int(screeny / 20 + screeny / 20)))
        if cur_seconds > self.start_time + 1:
            image = sprite_engine.sprite_sheet((110, 180), portal_spritesheet, (466, 19))
            for i in image:
                i.set_colorkey((0, 128, 0))
            self.image = pygame.transform.scale(image[0], (int(screenx / 20), int(screeny / 20 + screeny / 20)))
        if cur_seconds > self.start_time + 1.25:
            image = sprite_engine.sprite_sheet((110, 180), portal_spritesheet, (646, 39))
            for i in image:
                i.set_colorkey((0, 128, 0))
            self.image = pygame.transform.scale(image[0], (int(screenx / 20), int(screeny / 20 + screeny / 20)))
        if cur_seconds > self.start_time + 1.5:
            image = sprite_engine.sprite_sheet((110, 180), portal_spritesheet, (466, 19))
            for i in image:
                i.set_colorkey((0, 128, 0))
            self.image = pygame.transform.scale(image[0], (int(screenx / 20), int(screeny / 20 + screeny / 20)))
        if cur_seconds > self.start_time + 1.75:
            image = sprite_engine.sprite_sheet((110, 180), portal_spritesheet, (310, 24))
            for i in image:
                i.set_colorkey((0, 128, 0))
            self.image = pygame.transform.scale(image[0], (int(screenx / 20), int(screeny / 20 + screeny / 20)))
            self.start_time = cur_seconds - .75


class Background(pygame.sprite.Sprite):
    def __init__(self, x, y, screenx, screeny):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([screenx / 20, screeny / 20])
        self.image.blit(tiles_sprite_sheet, (0, 0), (0, 576, screenx / 20, screeny / 20))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.plat = False


class Platform(pygame.sprite.Sprite):

    def __init__(self, x, y, screenx, screeny):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([screenx / 20, 10])
        self.image.blit(tiles_sprite_sheet, (0, 0), (96, 351, screenx / 20, screeny / 20))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.plat = True


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, screenx, screeny):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([screenx / 20, screeny / 20])
        self.image.blit(tiles_sprite_sheet, (0, 0), (32, 224, screenx / 20, screeny / 20))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.plat = False


class DestWall(pygame.sprite.Sprite):
    def __init__(self, x, y, screenx, screeny):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([screenx / 20, screeny / 20])
        self.image.blit(tiles_sprite_sheet, (0, 0), (95, 256, screenx / 20, screeny / 20))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.plat = False


class Fireball(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.start_time = time.time()
        self.image = pygame.transform.scale(pygame.image.load("sprites/Flames/fireball/fireball_0001.png"), (20, 20))
        self.direction = 'left'
        self.orientation = 180
        self.frames = fireball_frames
        for frame in self.frames:
            frame.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, jump, down, left, right, wall_list, cur_level, screenx, screeny):
        fireball_speed = 10
        cur_seconds = time.time()

        if cur_seconds > self.start_time + .1:
            self.image = self.frames[0]
        if cur_seconds > self.start_time + .2:
            self.image = self.frames[1]
        if cur_seconds > self.start_time + .3:
            self.image = self.frames[2]
        if cur_seconds > self.start_time + .4:
            self.image = self.frames[3]
        if cur_seconds > self.start_time + .5:
            self.image = self.frames[4]
        if cur_seconds > self.start_time + .6:
            self.image = self.frames[5]
            self.start_time = time.time()

        if self.direction == 'left':
            self.orientation = 180
            self.rect.x -= fireball_speed
        if self.direction == 'right':
            self.orientation = 0
            self.rect.x += fireball_speed
        if self.direction == 'up':
            self.orientation = 90
            self.rect.y -= fireball_speed
        if self.direction == 'down':
            self.orientation = -90
            self.rect.y += fireball_speed

        image = pygame.transform.rotate(self.image, self.orientation)
        self.image = image


class Ectoplasmic_bolt(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        image = pygame.transform.scale(pygame.image.load("sprites/fireball.png"), (20, 20))
        self.image = image
        self.direction = 'left'

        self.rect = self.image.get_rect()

    def update(self, jump, down, left, right, wall_list, cur_level, screenx, screeny):
        fireball_speed = 10
        if self.direction == 'left':
            self.rect.x -= fireball_speed
        if self.direction == 'right':
            self.rect.x += fireball_speed
        if self.direction == 'up':
            self.rect.y -= fireball_speed
        if self.direction == 'down':
            self.rect.y += fireball_speed


class Explosion(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        image = pygame.transform.scale(pygame.image.load("sprites/bomb.png"), (20, 20))
        self.image = image
        cur_seconds = time.time()
        self.start_time = cur_seconds

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.onGround = False
        self.yvel = 0
        self.exp_radius1 = (x - 10, y - 10)
        self.exp_radius2 = (x - 15, y - 15)
        self.exp_radius3 = (x - 20, y - 20)
        self.frames = explosion_frames
        for frame in self.frames:
            frame.set_colorkey((0, 0, 0))
        self.boom = False

    def collide(self, xvel, yvel, wall_list, screeny):
        for w in wall_list:
            if pygame.sprite.collide_rect(self, w):
                if yvel > 0:
                    self.rect.bottom = w.rect.top
                    self.onGround = True
                    self.yvel = 0
                if yvel < 0:
                    self.rect.top = w.rect.bottom
        if self.rect.bottom > screeny - 20:
            self.rect.y = screeny - 20
            self.onGround = True
            self.yvel = 0

    def update(self, jump, down, left, right, wall_list, cur_level, screenx, screeny):
        cur_seconds = time.time()

        if not self.onGround and not self.boom:
            # only accelerate with gravity if in the air
            self.yvel += 0.3
            # max falling speed
            if self.yvel > 100:
                self.yvel = 100

            # increment in y direction
            self.rect.top += self.yvel
            # convert to list to enable changes to values
            self.exp_radius1 = list(self.exp_radius1)
            self.exp_radius2 = list(self.exp_radius2)
            self.exp_radius3 = list(self.exp_radius3)
            # change values in list
            self.exp_radius1[1] += self.yvel
            self.exp_radius2[1] += self.yvel
            self.exp_radius3[1] += self.yvel
            # convert back to tuple
            self.exp_radius1 = tuple(self.exp_radius1)
            self.exp_radius2 = tuple(self.exp_radius2)
            self.exp_radius3 = tuple(self.exp_radius3)
            # assuming we're in the air
            self.onGround = False
            # do y-axis collisions
            self.collide(0, self.yvel, wall_list, screeny)

        if cur_seconds >= self.start_time + 3:
            self.boom = True
            self.image = self.frames[0]
            self.rect = self.image.get_rect()
            self.rect.x = self.exp_radius1[0]
            self.rect.y = self.exp_radius1[1]

        if cur_seconds >= self.start_time + 3.1:
            self.image = self.frames[1]
            self.rect = self.image.get_rect()
            self.rect.x = self.exp_radius2[0]
            self.rect.y = self.exp_radius2[1]

        if cur_seconds >= self.start_time + 3.2:
            self.image = self.frames[2]
            self.rect = self.image.get_rect()
            self.rect.x = self.exp_radius3[0]
            self.rect.y = self.exp_radius3[1]

        if cur_seconds >= self.start_time + 3.3:
            self.kill()
