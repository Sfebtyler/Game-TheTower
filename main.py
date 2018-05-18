import pygame
import random
import sys
import levels

# screen size
screenx = 600
screeny = 600

pygame.font.init()
pygame.init()

screen = pygame.display.set_mode((screenx, screeny))
import sprite_classes

# current level
cur_level = 0

# current spell
spell_list = ('fireball', 'explosion')
set_spell = 0
cur_spell = spell_list[set_spell]

font = pygame.font.SysFont('Comic Sans MS', 30)
active = True

# clock speed
fps = 60

# character start pos
x = 80
y = screeny - 80

clock = pygame.time.Clock()

# spritesheets
fireball_sprite_sheet = pygame.image.load('sprites/fireball.png').convert()

# mana coordinates
randx = random.randrange(screenx - 70)
# target coordinates
manacount = 10
colorparam1 = random.randrange(255)
colorparam2 = random.randrange(255)
colorparam3 = random.randrange(255)
direction = 'right'
shot_active = False
hitcount = 0
jump = False

win = False
lose = False
start_level = True
portal_active = False
portal = ''

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
dest_wall_list = pygame.sprite.Group()
portal_list = pygame.sprite.Group()
explosion_list = pygame.sprite.Group()
bg_list = pygame.sprite.Group()

up = down = left = right = running = False


# Parse level from string in levels.set_level() W = wall P = platform T = Wall Topper M = Mana
def draw_level(level):
    global rendered_mana_count
    global portal

    # clean up level
    for x in wall_list:
        wall_list.remove(x)
    for x in mana_list:
        mana_list.remove(x)
    for x in enemy_list:
        enemy_list.remove(x)
    for x in fireball_list:
        fireball_list.remove(x)
    for x in bg_list:
        bg_list.remove(x)
    for x in all_sprites_list:
        all_sprites_list.remove(x)

    all_sprites_list.add(player)

    levx = 0
    levy = 0
    for row in levels.set_level(level):
        for col in row:
            bg = sprite_classes.Background(levx, levy, screenx, screeny)
            bg_list.add(bg)
            if col == "W":
                wall = sprite_classes.Wall(levx, levy, screenx, screeny)
                wall_list.add(wall)
                all_sprites_list.add(wall)
            if col == "D":
                dest_wall = sprite_classes.DestWall(levx, levy, screenx, screeny)
                dest_wall_list.add(dest_wall)
                wall_list.add(dest_wall)
                all_sprites_list.add(dest_wall)
            if col == "P":
                platform = sprite_classes.Platform(levx, levy, screenx, screeny)
                wall_list.add(platform)
                all_sprites_list.add(platform)
            if col == "M":
                mana = sprite_classes.Mana(levx + 7, levy + 4)
                mana_list.add(mana)
                all_sprites_list.add(mana)
            if col == "H":
                health = sprite_classes.Health(levx + 7, levy + 4, screenx, screeny)
                health_list.add(health)
                all_sprites_list.add(health)
            if col == "1":
                enemy = sprite_classes.Enemy(levx + 9, levy + 6, 'standard')
                enemy_list.add(enemy)
                all_sprites_list.add(enemy)
            if col == "2":
                enemy = sprite_classes.Enemy(levx + 9, levy + 6, 'flyer')
                enemy_list.add(enemy)
                all_sprites_list.add(enemy)
            if col == "O":
                portal = sprite_classes.Portal(levx, levy, screenx, screeny)
            levx += screenx / 20
        levy += screeny / 20
        levx = 0

# Create Player
player = sprite_classes.Player(x, y)


# Main Loop
while active:
    if lose:
        pygame.time.wait(1000)
    pygame.display.set_caption("The Tower")
    pressed = pygame.key.get_pressed()

    if start_level:
        start_level = False
        cur_level += 1
        draw_level(cur_level)
        hitcount = 0

    # border
    if player.rect.x < 0:
        player.rect.x = 0
    if player.rect.x > screenx - 20:
        player.rect.x = screenx - 20
    if player.rect.y < 0:
        player.rect.y = 0
    if player.rect.y > screeny - 21:
        player.onGround = True
        player.yvel = 0
        player.rect.y = screeny - 20

    # Exit Program
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        # invincibility timer when hit by enemy
        if event.type == invincibility_timer:
            player.invincible = False

        # reset game after losing
        if event.type == reset_after_lose:
            if lose is True:
                lose = False
                player.rect.x = x
                player.rect.y = y
                player.health = 3
                manacount = 10
                start_level = True
                cur_level = 0

        if event.type == pygame.KEYDOWN:

            # jump
            if event.key == pygame.K_SPACE:
                if not jump:
                    jump = True

            # change spell
            if event.key == pygame.K_x:
                if set_spell + 2 > len(spell_list):
                    set_spell = 0
                    cur_spell = spell_list[set_spell]
                else:
                    set_spell += 1
                    cur_spell = spell_list[set_spell]

            # shoot fireball
            if event.key == pygame.K_LSHIFT and cur_spell == 'fireball':
                fireball = sprite_classes.Fireball(player.rect.x, player.rect.y)
                fireball.direction = direction

                fireball_list.add(fireball)
                all_sprites_list.add(fireball)

            if event.key == pygame.K_LSHIFT and cur_spell == 'explosion':
                if manacount > 1:
                    manacount -= 2
                    explosion = sprite_classes.Explosion(player.rect.x, player.rect.y)

                    explosion_list.add(explosion)
                    all_sprites_list.add(explosion)

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
    if pressed[pygame.K_SPACE]:
        jump = True
    if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
        jump = False
    if pressed[pygame.K_DOWN]:
        down = True
        direction = 'down'
    if event.type == pygame.KEYUP and event.key == pygame.K_DOWN:
        down = False
    if pressed[pygame.K_LEFT]:
        left = True
        direction = 'left'
        jump_direction = 'left'
    if event.type == pygame.KEYUP and event.key == pygame.K_LEFT:
        left = False
    if pressed[pygame.K_RIGHT]:
        right = True
        direction = 'right'
        jump_direction = 'right'
    if event.type == pygame.KEYUP and event.key == pygame.K_RIGHT:
        right = False
    if not pressed[pygame.K_RIGHT] and not pressed[pygame.K_LEFT]:
        jump_direction = ''
    # resolves multi press movement bug
    if not pressed[pygame.K_RIGHT] and not pressed[pygame.K_LEFT] and not pressed[pygame.K_SPACE]:
        jump = False
        left = False
        right = False

    # select level using number keys
    if event.type == pygame.KEYUP and event.key == pygame.K_1:
        start_level = True
        cur_level = 0
    if event.type == pygame.KEYUP and event.key == pygame.K_2:
        start_level = True
        cur_level = 1
    if event.type == pygame.KEYUP and event.key == pygame.K_3:
        start_level = True
        cur_level = 2
    if event.type == pygame.KEYUP and event.key == pygame.K_4:
        start_level = True
        cur_level = 3
    if event.type == pygame.KEYUP and event.key == pygame.K_5:
        start_level = True
        cur_level = 4
    if event.type == pygame.KEYUP and event.key == pygame.K_6:
        start_level = True
        cur_level = 5
    if event.type == pygame.KEYUP and event.key == pygame.K_7:
        start_level = True
        cur_level = 6

    screen.fill((0, 0, 0))

    # Health loss if hit by enemy
    for e in enemy_list:
        if pygame.sprite.collide_rect(player, e):
            if player.health > 0:
                if not player.invincible:
                    player.health -= 1
                    player.invincible = True
                    pygame.time.set_timer(invincibility_timer, 1500)

    # health and mana collection
    for health in health_list:
        health_collected_list = pygame.sprite.spritecollide(player, health_list, True)

        for health_collected in health_collected_list:
            health_list.remove(health_collected)
            all_sprites_list.remove(health_collected)
            if player.health < 3:
                player.health += 1

    for mana in mana_list:
        mana_collected_list = pygame.sprite.spritecollide(player, mana_list, True)

        for mana_collected in mana_collected_list:
            mana_list.remove(mana_collected)
            all_sprites_list.remove(mana_collected)
            if manacount < 10:
                manacount += 1
            if manacount > 10:
                manacount = 10

    # Fireball logic
    if len(fireball_list) > 0:
        shot_active = True

    if len(fireball_list) < 1:
        shot_active = False

    if len(explosion_list) > 0:
        shot_active = True

    if len(explosion_list) < 1:
        shot_active = False

    for explosion in explosion_list:
        wall_hit_list = pygame.sprite.spritecollide(explosion, dest_wall_list, True)

        # Health loss if hit by explosion
        if pygame.sprite.collide_rect(player, explosion) and explosion.boom:
            if player.health > 0:
                if not player.invincible:
                    player.health -= 3
                    player.invincible = True
                    pygame.time.set_timer(invincibility_timer, 1500)

        # blow up enemy
        for e in explosion_list:
            if e.boom:
                enemy_hit_list = pygame.sprite.spritecollide(explosion, enemy_list, True)

                for enemy in enemy_hit_list:
                    hitcount += 1
                    enemy_list.remove(enemy)
                    all_sprites_list.remove(enemy)

        # blow up destructible walls
        for wall in wall_hit_list:
            dest_wall_list.remove(wall)
            wall_list.remove(wall)
            all_sprites_list.remove(wall)

    for fireball in fireball_list:

        enemy_hit_list = pygame.sprite.spritecollide(fireball, enemy_list, True)
        for enemy in enemy_list:
            fireball_hit_list = pygame.sprite.spritecollide(enemy, fireball_list, True)

            for fireballx in fireball_hit_list:
                fireball_list.remove(fireballx)
                all_sprites_list.remove(fireballx)
            if fireball.rect.x <= -10:
                fireball_list.remove(fireball)
                all_sprites_list.remove(fireball)
            if fireball.rect.y <= -10:
                fireball_list.remove(fireball)
                all_sprites_list.remove(fireball)
            if fireball.rect.x >= screenx:
                fireball_list.remove(fireball)
                all_sprites_list.remove(fireball)
            if fireball.rect.y >= screeny:
                fireball_list.remove(fireball)
                all_sprites_list.remove(fireball)

        for wall in wall_list:
            if not wall.plat:
                wall_fireball_collision_list = pygame.sprite.spritecollide(wall, fireball_list, True)

                for fire in wall_fireball_collision_list:
                    fireball_list.remove(fire)
                    all_sprites_list.remove(fire)

        for enemy in enemy_hit_list:
            enemy_list.remove(enemy)
            all_sprites_list.remove(enemy)
            hitcount += 1

    # draw background tiles
    bg_list.draw(screen)

    # victory screen
    if win:
        win = False
        hitcount = 0

    # current spell displayed
    if cur_spell == "fireball":
        current_spell_displayed = pygame.transform.scale(pygame.image.load("sprites/fireball.png"), (30, 30)).convert()
    if cur_spell == "explosion":
        current_spell_displayed = pygame.transform.scale(pygame.image.load("sprites/bomb.png"), (30, 30)).convert()
    screen.blit(current_spell_displayed, (112, 12))
    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(110, 10, 34, 34), 1)

    # portal summon condition
    if hitcount >= 6:
        levx = 0
        levy = 0
        if not portal_active:
            portal_list.add(portal)
            all_sprites_list.add(portal)
            portal_active = True
        for p in portal_list:
            if pygame.sprite.collide_rect(p, player):
                win = True
                portal_list.remove(p)
                portal_active = False
                start_level = True
                explosion_list.empty()
                fireball_list.empty()
            if win is False:
                portal_list.remove(p)
                portal_active = False

    # lose conditions
    if player.health < 1 and win is False:
        textsurface = font.render("YOU LOSE!", True, (255, 0, 0))
        screen.blit(textsurface, (screenx / 2 - 80, screeny / 2))
        pygame.time.set_timer(reset_after_lose, 1000)
        lose = True

    all_sprites_list.update(jump, down, left, right, wall_list, cur_level, screenx, screeny)
    all_sprites_list.draw(screen)

    # mana bar
    pygame.draw.rect(screen, (0, 200, 0), pygame.Rect(8, 35, 90 / 10 * manacount, 20))
    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(8, 33, 94, 24), 1)

    # health bar
    pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(10, 10, 90 / 3 * player.health, 20))
    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(8, 8, 94, 24), 1)

    # Scoring
    textsurface = font.render('Kills: ' + str(hitcount), False, (255, 246, 55))
    screen.blit(textsurface, (screenx - 100, 0))

    pygame.display.flip()
    clock.tick(fps)
