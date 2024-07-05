import pygame
import sys
import random
import moviepy.editor as mp
from pygame.locals import *
from PIL import Image

# Initialize Pygame
pygame.init()

# Screen settings
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Eco Game - Level 3")

# Load images
player_image = pygame.image.load("ecoCharfinal.png").convert_alpha()
background_image = pygame.image.load("final.jpg").convert_alpha()
gas_images = [
    pygame.image.load("CO2.png").convert_alpha(),
    pygame.image.load("NO2.png").convert_alpha(),
    pygame.image.load("H2S.png").convert_alpha(),
    pygame.image.load("O3.png").convert_alpha(),
    pygame.image.load("SO2.png").convert_alpha(),
    pygame.image.load("PM2.png").convert_alpha()
]

# Scale images if necessary
player_image = pygame.transform.scale(player_image, (100, 100))
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
gas_images = [pygame.transform.scale(image, (180, 140)) for image in gas_images]

# Load sound effects
collect_sound = pygame.mixer.Sound("gascollect.wav")

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.center = (screen_width // 2, screen_height // 2)  # Start from center-right
        self.speed = 12  # Speed of the player
        self.gas_collected = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[K_w]:  # Move up
            self.rect.y -= self.speed
        if keys[K_s]:  # Move down
            self.rect.y += self.speed

        # Keep the player within the screen bounds
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height

class Gas(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.rect.x -= 6  # Move gas leftwards to simulate player moving right
        if self.rect.right < 0:  # Remove gas if it goes off the screen
            self.kill()

        if pygame.sprite.collide_rect(self, player):
            player.gas_collected += 1
            collect_sound.play()
            self.kill()

# Create sprite groups
all_sprites = pygame.sprite.Group()
gases = pygame.sprite.Group()

# Create player and add to sprite group
player = Player()
all_sprites.add(player)

# Create gases and add to sprite groups
initial_x = screen_width + 100
for i in range(16):
    gas_image = random.choice(gas_images)
    if i == 0:
        x = initial_x
    else:
        x += random.randint(600, 800)  # Random horizontal spacing between 600 and 800 pixels
    y = random.randint(10, 590)  # Random vertical position between 10 and 590 pixels
    gas = Gas(gas_image, x, y)
    all_sprites.add(gas)
    gases.add(gas)

# Game loop variables
running = True
clock = pygame.time.Clock()
background_x = 0

# Game loop
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Update
    all_sprites.update()

    # Move background
    background_x -= 6  # Adjust background speed
    if background_x <= -screen_width:
        background_x = 0

    # Draw
    screen.blit(background_image, (background_x, 0))
    screen.blit(background_image, (background_x + screen_width, 0))
    all_sprites.draw(screen)

    # Draw gas counter
    font = pygame.font.SysFont("Arial", 24)
    gas_text = font.render(f"Gases Collected: {player.gas_collected} / 16", True, (255, 255, 255))
    screen.blit(gas_text, (10, 10))

    # Check if player collected all gases
    if player.gas_collected >= 16:
        clip = mp.VideoFileClip("finalvictory.mp4")
        clip.preview()
        pygame.quit()
        sys.exit()

    pygame.display.flip()
    clock.tick(30)
