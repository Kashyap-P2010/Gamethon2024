import pygame
import sys
import moviepy.editor as mp
from pygame.locals import *
from PIL import Image

# Initialize Pygame
pygame.init()

# Screen settings
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Mario-style Game")

# Load images
player_image = pygame.image.load("ecoChar.png").convert_alpha()
enemy_image = pygame.image.load("enemyChar.png").convert_alpha()
background_image = pygame.image.load("sky.png").convert_alpha()
game_over_image = pygame.image.load("game_over.jpg").convert_alpha()
try:
    start_screen_image = pygame.image.load("start-screen.png").convert_alpha()
except FileNotFoundError:
    start_screen_image = pygame.Surface((screen_width, screen_height))
    start_screen_image.fill((0, 0, 0))

# Load and set up animated GIF using PIL
coin_gif = Image.open("coin.gif")
coin_frames = []
for frame in range(coin_gif.n_frames):
    coin_gif.seek(frame)
    frame_image = coin_gif.convert("RGBA")
    frame_surface = pygame.image.fromstring(frame_image.tobytes(), frame_image.size, frame_image.mode)
    frame_surface = pygame.transform.scale(frame_surface, (50, 50))
    coin_frames.append(frame_surface)

# Load and set up serum GIF using PIL
serum_gif = Image.open("potion.gif")
serum_frames = []
for frame in range(serum_gif.n_frames):
    serum_gif.seek(frame)
    frame_image = serum_gif.convert("RGBA")
    frame_surface = pygame.image.fromstring(frame_image.tobytes(), frame_image.size, frame_image.mode)
    frame_surface = pygame.transform.scale(frame_surface, (50, 50))
    serum_frames.append(frame_surface)

# Scale images if necessary
player_image = pygame.transform.scale(player_image, (100, 100))
enemy_image = pygame.transform.scale(enemy_image, (100, 100))
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
game_over_image = pygame.transform.scale(game_over_image, (screen_width, screen_height))
start_screen_image = pygame.transform.scale(start_screen_image, (screen_width, screen_height))

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Load sound effects
jump_sound = pygame.mixer.Sound("jumping.wav")
hit_sound = pygame.mixer.Sound("hit.wav")
collect_sound = pygame.mixer.Sound("collect.wav")

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.center = (100, screen_height - 40)  # Adjusted vertical position
        self.vel_y = 0
        self.jump_power = -16
        self.gravity = 1
        self.health = 100
        self.coins = 0
        self.on_ground = False
        self.victory = False
        self.speed = 8  # Increase speed for horizontal movement

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[K_SPACE] and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False
            jump_sound.play()

        if keys[K_a]:  # Move left
            self.rect.x -= self.speed
        if keys[K_d]:  # Move right
            self.rect.x += self.speed

        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        if self.rect.bottom >= screen_height - 40:  # Adjusted to match enemy's initial vertical position
            self.rect.bottom = screen_height - 40
            self.vel_y = 0
            self.on_ground = True

    def check_collision(self, enemy):
        if pygame.sprite.collide_rect(self, enemy):
            if self.rect.bottom <= enemy.rect.top + 10:
                self.vel_y = self.jump_power
                enemy.health -= 50
                hit_sound.play()
                if enemy.health <= 0:
                    enemy.kill()
                    return True
        return False

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, screen_height - 100)  # Default position near bottom of screen
        self.health = 100
        self.speed = 2  # Set speed for enemy movement

    def update(self):
        self.rect.x += self.speed
        if self.rect.left < 0 or self.rect.right > screen_width:
            self.speed = -self.speed  # Reverse direction if hitting screen edge

        if pygame.sprite.collide_rect(self, player):
            if player.rect.bottom > self.rect.top + 10:
                player.health -= 25
                if player.health <= 0:
                    player.kill()

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = coin_frames
        self.image = self.images[0]  # Initialize the image attribute
        self.rect = self.images[0].get_rect()
        self.rect.center = (x, y)
        self.index = 0
        self.counter = 0

    def update(self):
        self.counter += 1
        if self.counter >= 5:
            self.counter = 0
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]

        if pygame.sprite.collide_rect(self, player):
            player.coins += 1
            collect_sound.play()
            self.kill()

class Serum(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = serum_frames
        self.image = self.images[0]  # Initialize the image attribute
        self.rect = self.images[0].get_rect()
        self.rect.center = (x, y)
        self.index = 0
        self.counter = 0

    def update(self):
        self.counter += 1
        if self.counter >= 5:
            self.counter = 0
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]

        if pygame.sprite.collide_rect(self, player):
            player.victory = True
            self.kill()

# Create sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
coins = pygame.sprite.Group()
serums = pygame.sprite.Group()

# Create player and add to sprite group
player = Player()
all_sprites.add(player)

# Create enemies and add to sprite groups
enemy1 = Enemy(400, screen_height - 100)
enemy2 = Enemy(600, screen_height - 100)
all_sprites.add(enemy1, enemy2)
enemies.add(enemy1, enemy2)

# Game loop variables
running = True
game_over = False
game_started = False
clock = pygame.time.Clock()

# Game loop
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN and not game_started:
            game_started = True

    if game_started:
        if not game_over:
            # Update
            all_sprites.update()

            # Check collisions and collect coins
            for enemy in enemies:
                if player.check_collision(enemy):
                    coin = Coin(enemy.rect.centerx, enemy.rect.centery)
                    all_sprites.add(coin)
                    coins.add(coin)

            if player.health <= 0:
                game_over = True

            # Check if all enemies are dead
            if not enemies and not serums:
                serum = Serum(screen_width // 2, screen_height - 100)
                all_sprites.add(serum)
                serums.add(serum)

            if player.victory:
                clip = mp.VideoFileClip("victory.mp4")
                clip.preview()
                pygame.time.wait(int(clip.duration * 1000))
                pygame.quit()
                sys.exit()

            # Draw
            screen.blit(background_image, (0, 0))
            all_sprites.draw(screen)

            # Draw health bars and coin count
            pygame.draw.rect(screen, RED, (player.rect.x, player.rect.y - 10, 100, 5))
            pygame.draw.rect(screen, GREEN, (player.rect.x, player.rect.y - 10, player.health, 5))

            for enemy in enemies:
                pygame.draw.rect(screen, RED, (enemy.rect.x, enemy.rect.y - 10, 100, 5))
                pygame.draw.rect(screen, GREEN, (enemy.rect.x, enemy.rect.y - 10, enemy.health, 5))

            font = pygame.font.SysFont("Arial", 24)
            coin_text = font.render(f"Coins: {player.coins}", True, WHITE)
            screen.blit(coin_text, (10, 10))

        else:
            screen.blit(game_over_image, (0, 0))
            pygame.time.wait(5000)
            pygame.quit()
            sys.exit()
    else:
        screen.blit(start_screen_image, (0, 0))

    pygame.display.flip()
    clock.tick(30)