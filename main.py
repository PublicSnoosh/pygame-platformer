import pygame
from pygame.locals import *

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
LEVEL_WIDTH = 2000

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Byte Me - Platformer Demo")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.Surface((32, 48), pygame.SRCALPHA)
        self.rect = self.image.get_rect(x=100, y=400)

        self.vel_x = 0
        self.vel_y = 0

        self.speed = 5
        self.jump_power = -15
        self.gravity = 0.8
        self.max_fall_speed = 12

        self.on_ground = False

        # Animation
        self.frame = 0
        self.animation_timer = 0
        self.animation_speed = 6
        self.facing_right = True

        self.draw_character()

    def draw_character(self):
        # --- squash/stretch character when jumping/landing ---
        scale_y = 48 if self.on_ground else 40

        old_bottom = self.rect.bottom
        self.image = pygame.Surface((32, scale_y), pygame.SRCALPHA)
        self.rect = self.image.get_rect(midbottom=(self.rect.centerx, old_bottom))

        self.image.fill((0, 0, 0, 0))

        # --- Colours ---
        skin = (255, 220, 180)
        shirt = (255, 0, 0)
        trousers = (40, 80, 200)
        hat = (200, 0, 0)
        shoes = (255, 100, 0)
        eye_white = (255, 255, 255)
        eye_blue = (0, 120, 255)

        # --- Head ---
        pygame.draw.rect(self.image, skin, (10, 6, 14, 12))
        pygame.draw.rect(self.image, skin, (22, 10, 4, 4))  # nose

        # --- Eye ---
        pygame.draw.rect(self.image, eye_white, (16, 10, 4, 4))
        pygame.draw.rect(self.image, eye_blue, (17, 11, 2, 2))

        # --- Hat ---
        pygame.draw.rect(self.image, hat, (8, 2, 18, 6))
        pygame.draw.rect(self.image, hat, (22, 6, 6, 3))

        # --- Body ---
        pygame.draw.rect(self.image, shirt, (12, 18, 12, 12))

        # --- Jump animation ---
        if not self.on_ground:
            if self.vel_y < 0:  # going up
                pygame.draw.rect(self.image, skin, (6, 10, 4, 10))
                pygame.draw.rect(self.image, skin, (22, 10, 4, 10))

                pygame.draw.rect(self.image, trousers, (10, 24, 6, 8))
                pygame.draw.rect(self.image, trousers, (18, 24, 6, 8))
            else:  # --- falling ---
                pygame.draw.rect(self.image, skin, (6, 16, 4, 10))
                pygame.draw.rect(self.image, skin, (22, 16, 4, 10))

                pygame.draw.rect(self.image, trousers, (10, 30, 6, 12))
                pygame.draw.rect(self.image, trousers, (18, 30, 6, 12))

        # --- Running animation ---
        else:
            if self.frame == 0:
                pygame.draw.rect(self.image, skin, (8, 18, 4, 10))
                pygame.draw.rect(self.image, skin, (22, 20, 4, 10))

                pygame.draw.rect(self.image, trousers, (12, 30, 5, 12))
                pygame.draw.rect(self.image, trousers, (18, 34, 5, 8))
            else:
                pygame.draw.rect(self.image, skin, (6, 22, 4, 10))
                pygame.draw.rect(self.image, skin, (22, 18, 4, 10))

                pygame.draw.rect(self.image, trousers, (12, 34, 5, 8))
                pygame.draw.rect(self.image, trousers, (18, 30, 5, 12))

        # Shoes
        pygame.draw.rect(self.image, shoes, (11, 40, 6, 4))
        pygame.draw.rect(self.image, shoes, (17, 40, 6, 4))

        # --- Flip sprite depemding on direction faced  ---
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def check_enemy_collisions(self, enemies):
        for enemy in enemies[:]:  
            if self.rect.colliderect(enemy.rect):

                if self.vel_y > 0 and self.rect.bottom - enemy.rect.top < 15:
                    enemy.squash()   
                    self.vel_y = -12
                else:
                    self.respawn()

    def update(self, platforms):
        keys = pygame.key.get_pressed()

        self.vel_x = 0
        if keys[K_LEFT]:
            self.vel_x = -self.speed
        if keys[K_RIGHT]:
            self.vel_x = self.speed

        # --- Facing ---
        if self.vel_x > 0:
            self.facing_right = True
        elif self.vel_x < 0:
            self.facing_right = False

        # --- Jump ---
        if keys[K_SPACE] and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False
        if not keys[K_SPACE] and self.vel_y < 0:
            self.vel_y *= 0.5

        # --- Gravity ---
        self.vel_y += self.gravity
        self.vel_y = min(self.vel_y, self.max_fall_speed)

        # --- Move X ---
        self.rect.x += self.vel_x
        self.handle_horizontal_collisions(platforms)

        # --- Move Y ---
        self.rect.y += self.vel_y
        self.on_ground = False
        self.handle_vertical_collisions(platforms)

        # --- Animation ---
        if self.vel_x != 0:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.frame = (self.frame + 1) % 2
        else:
            self.frame = 0

        self.draw_character()

        if self.rect.top > SCREEN_HEIGHT:
            self.respawn()

    def handle_horizontal_collisions(self, platforms):
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel_x > 0:
                    self.rect.right = p.rect.left
                elif self.vel_x < 0:
                    self.rect.left = p.rect.right

    def handle_vertical_collisions(self, platforms):
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel_y > 0:
                    self.rect.bottom = p.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = p.rect.bottom
                    self.vel_y = 0

    def respawn(self):
        self.rect.x = 100
        self.rect.y = 400
        self.vel_x = 0
        self.vel_y = 0


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(topleft=(x, y))


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, min_x, max_x):
        super().__init__()

        self.x = x
        self.y = y
        self.min_x = min_x
        self.max_x = max_x
        self.speed = 2

        self.image = pygame.Surface((30, 30))
        self.image.fill((0, 0, 255))  # BLUE
        self.rect = self.image.get_rect(topleft=(x, y))

        self.vel_x = self.speed
        self.vel_y = 0
        self.gravity = 0.8

        self.squashed = False
        self.squash_timer = 0
        self.squashed_height = 10  # needed for squash()

    def update(self):
        # Move left/right
        self.rect.x += self.vel_x

        # Reverse direction at boundaries
        if self.rect.x <= self.min_x or self.rect.x >= self.max_x:
            self.vel_x *= -1

        # Apply gravity
        self.apply_gravity()

        if self.squashed:
            self.squash_timer += 1

    def apply_gravity(self):
        self.vel_y += self.gravity
        self.rect.y += self.vel_y

    def squash(self):
        self.squashed = True

        bottom = self.rect.bottom

        self.image = pygame.Surface((30, self.squashed_height))
        self.image.fill((200, 200, 255))

        self.rect = self.image.get_rect(midbottom=(self.rect.centerx, bottom))

player = Player()

platforms = [
    Platform(0, 500, 2000, 100),
    Platform(200, 400, 100, 20),
    Platform(400, 300, 100, 20),
    Platform(600, 200, 100, 20),
]

enemies = [
    Enemy(300, 470, 250, 500),
    Enemy(800, 370, 750, 950),
]

all_sprites = pygame.sprite.Group(player, *platforms, *enemies)

camera_x = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    player.update(platforms)
    player.check_enemy_collisions(enemies)

    for e in enemies[:]:
        e.update()

        if e.squashed and e.squash_timer > 30:  # ~0.5 seconds
            enemies.remove(e)
            all_sprites.remove(e)

    camera_x = max(0, min(player.rect.centerx - SCREEN_WIDTH // 2, LEVEL_WIDTH - SCREEN_WIDTH))

    screen.fill(BLACK)

    for sprite in all_sprites:
        screen.blit(sprite.image, (sprite.rect.x - camera_x, sprite.rect.y))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()