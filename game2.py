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
pygame.display.set_caption("Underwater Trash Collector")

# Load and scale images
player_image = pygame.image.load("ecoChar.png").convert_alpha()
player_image = pygame.transform.scale(player_image, (100, 100))

trash_images = [pygame.image.load(f"trash{i}.png").convert_alpha() for i in range(1, 4)]
trash_images = [pygame.transform.scale(image, (50, 50)) for image in trash_images]

game_over_image = pygame.image.load("lev2gameover.png").convert_alpha()
game_over_image = pygame.transform.scale(game_over_image, (screen_width, screen_height))

# Load and set up animated GIF using PIL for underwater1 background
underwater1_gif = Image.open("underwater.gif")
underwater1_frames = []
for frame in range(underwater1_gif.n_frames):
    underwater1_gif.seek(frame)
    frame_image = underwater1_gif.convert("RGBA")
    frame_surface = pygame.image.fromstring(frame_image.tobytes(), frame_image.size, frame_image.mode)
    frame_surface = pygame.transform.scale(frame_surface, (screen_width, screen_height))
    underwater1_frames.append(frame_surface)

# Load and set up animated GIF using PIL for underwater2 background
underwater2_gif = Image.open("underwater2.gif")
underwater2_frames = []
for frame in range(underwater2_gif.n_frames):
    underwater2_gif.seek(frame)
    frame_image = underwater2_gif.convert("RGBA")
    frame_surface = pygame.image.fromstring(frame_image.tobytes(), frame_image.size, frame_image.mode)
    frame_surface = pygame.transform.scale(frame_surface, (screen_width, screen_height))
    underwater2_frames.append(frame_surface)

# Load and set up animated GIF using PIL for bubbles
bubbles_gif = Image.open("bubbles.gif")
bubbles_frames = []
for frame in range(bubbles_gif.n_frames):
    bubbles_gif.seek(frame)
    frame_image = bubbles_gif.convert("RGBA")
    frame_surface = pygame.image.fromstring(frame_image.tobytes(), frame_image.size, frame_image.mode)
    frame_surface = pygame.transform.scale(frame_surface, (25, 25))
    bubbles_frames.append(frame_surface)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Load sound effects
trash_collect_sound = pygame.mixer.Sound("trashcollect.wav")

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.center = (screen_width - 100, screen_height // 2)  # Center-right position
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.trash_collected = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[K_w]:
            self.rect.y -= self.speed
        if keys[K_s]:
            self.rect.y += self.speed
        if keys[K_a]:
            self.rect.x -= self.speed
        if keys[K_d]:
            self.rect.x += self.speed

        # Keep the player within the screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height

# Trash class
class Trash(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        if pygame.sprite.collide_rect(self, player):
            player.trash_collected += 1
            trash_collect_sound.play()
            self.kill()

# Bubbles class
class Bubbles(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = bubbles_frames
        self.image = self.images[0]
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

# Create sprite groups
all_sprites = pygame.sprite.Group()
trashes = pygame.sprite.Group()
bubbles_group = pygame.sprite.Group()

# Create player and add to sprite group
player = Player()
all_sprites.add(player)

# Create trashes and add to sprite groups
def create_trash():
    for _ in range(3):
        trash_image = random.choice(trash_images)
        x = random.randint(50, screen_width - 50)
        y = random.randint(50, screen_height - 50)
        trash = Trash(trash_image, x, y)
        all_sprites.add(trash)
        trashes.add(trash)

create_trash()

# Game loop variables
running = True
game_over = False
background_phase = 1
clock = pygame.time.Clock()
start_time = pygame.time.get_ticks()
bubbles_delay = 100  # milliseconds delay between bubbles
bubbles_timer = pygame.time.get_ticks()
phase_transition = False  # New variable for phase transition

# Game loop
frame_index = 0
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    if not game_over:
        if not phase_transition:
            # Update
            all_sprites.update()

            # Emit bubbles periodically
            if pygame.time.get_ticks() - bubbles_timer > bubbles_delay:
                bubbles_timer = pygame.time.get_ticks()
                bubble = Bubbles(player.rect.centerx, player.rect.centery + player.rect.height // 2)
                all_sprites.add(bubble)
                bubbles_group.add(bubble)

            # Check if the player collected all the trash in the current phase
            if player.trash_collected == 3 and background_phase == 1:
                phase_transition = True
                player.trash_collected = 0  # Reset the counter for the next phase

            # Check if the player collected all the trash in the second phase
            if player.trash_collected == 3 and background_phase == 2:
                game_over = True
                game_over_reason = "victory"

            # Check for timer
            elapsed_time = (pygame.time.get_ticks() - start_time) / 1000
            if elapsed_time > 15:
                game_over = True
                game_over_reason = "time"

            # Draw
            if background_phase == 1:
                screen.blit(underwater1_frames[frame_index], (0, 0))
            else:
                screen.blit(underwater2_frames[frame_index], (0, 0))

            frame_index = (frame_index + 1) % len(underwater1_frames)
            all_sprites.draw(screen)

            # Draw trash counter
            font = pygame.font.SysFont("Arial", 24)
            trash_text = font.render(f"Trash: {player.trash_collected + (3 if background_phase == 2 else 0)} / 6", True, WHITE)
            screen.blit(trash_text, (10, 10))

            # Draw timer
            timer_text = font.render(f"Time: {15 - int(elapsed_time)}", True, WHITE)
            screen.blit(timer_text, (screen_width - 150, 10))

        else:
            # Play phase transition video
            clip = mp.VideoFileClip("phase.mp4")
            clip.preview()
            pygame.time.wait(int(clip.duration * 1000))
            phase_transition = False
            background_phase = 2
            player.rect.center = (screen_width - 100, screen_height // 2)  # Reset player position
            trashes.empty()  # Remove old trash
            create_trash()  # Create new trash
            start_time = pygame.time.get_ticks()  # Reset timer for second phase

    else:
        if game_over_reason == "time":
            screen.blit(game_over_image, (0, 0))
            pygame.display.flip()
            pygame.time.wait(5000)
            pygame.quit()
            sys.exit()
        elif game_over_reason == "victory":
            clip = mp.VideoFileClip("lev2victory.mp4")
            clip.preview()
            pygame.time.wait(int(clip.duration * 1000))
            pygame.quit()
            sys.exit()

    pygame.display.flip()
    clock.tick(30)
