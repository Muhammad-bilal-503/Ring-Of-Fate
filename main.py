import pygame
import cv2
import sys
import random

# --- Pygame Initialisation ---
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ring Bounce - Final Version")

# Colors & Fonts
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
font = pygame.font.Font(None, 52)
button_font = pygame.font.Font(None, 60)
zoom_font_large = pygame.font.Font(None, 250)
zoom_font_small = pygame.font.Font(None, 60)

# --- Camera Setup ---
cap = cv2.VideoCapture(0)

# --- GAME STATES ---
game_state = "start_screen"

# --- Game Assets ---
try:
    falling_ring_img = pygame.image.load('falling_ring.png').convert_alpha()
    falling_ring_img = pygame.transform.scale(falling_ring_img, (70, 70))
    left_obstacle_img = pygame.image.load('left_obstacle.png').convert_alpha()
    left_obstacle_img = pygame.transform.scale(left_obstacle_img, (430, 450))
    left_obstacle_rect = left_obstacle_img.get_rect(center=(SCREEN_WIDTH // 4 - 20, SCREEN_HEIGHT // 2 + 100))
    right_obstacle_img = pygame.image.load('right_obstacle.png').convert_alpha()
    right_obstacle_img = pygame.transform.scale(right_obstacle_img, (430, 450))
    right_obstacle_rect = right_obstacle_img.get_rect(center=(3 * SCREEN_WIDTH // 4 + 20, SCREEN_HEIGHT // 2 + 100))
except pygame.error as e:
    print(f"Error loading image: {e}")
    pygame.quit()
    sys.exit()

# Collision Masks
falling_ring_mask = pygame.mask.from_surface(falling_ring_img)
left_obstacle_mask = pygame.mask.from_surface(left_obstacle_img)
right_obstacle_mask = pygame.mask.from_surface(right_obstacle_img)

# Game variables
falling_ring_rect = falling_ring_img.get_rect()
years = 0
gravity = 0.25
velocity_x = 0
velocity_y = 0
bounce_cooldown = 0
game_over_start_time = None
zoom_animation_duration = 600

def reset_game():
    global velocity_x, velocity_y, years, bounce_cooldown, game_over_start_time
    falling_ring_rect.centerx = random.randint(SCREEN_WIDTH // 2 - 50, SCREEN_WIDTH // 2 + 50)
    falling_ring_rect.y = -50
    velocity_x = random.choice([-2, 2])
    velocity_y = 0
    years = 0
    bounce_cooldown = 0
    game_over_start_time = None

reset_game()

# Game Loop
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "start_screen" and start_button.collidepoint(event.pos):
                game_state = "playing"
            elif game_state == "game_over" and again_button.collidepoint(event.pos):
                reset_game()
                game_state = "playing"

    # Camera Background
    ret, frame = cap.read()
    if ret:
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_pygame = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
        screen.blit(pygame.transform.scale(frame_pygame, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
    else:
        screen.fill(BLACK)

    # --- Game States Logic ---

    if game_state == "start_screen":
        start_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 40, 200, 80)
        pygame.draw.rect(screen, GRAY, start_button)
        start_text = button_font.render("START", True, BLACK)
        screen.blit(start_text, (start_button.x + 45, start_button.y + 20))
        screen.blit(left_obstacle_img, left_obstacle_rect)
        screen.blit(right_obstacle_img, right_obstacle_rect)

    elif game_state == "playing":
        if bounce_cooldown > 0: bounce_cooldown -= 1
        velocity_y += gravity
        falling_ring_rect.y += int(velocity_y)
        falling_ring_rect.x += int(velocity_x)
        
        # Collision with Left Obstacle
        offset_x_left = falling_ring_rect.x - left_obstacle_rect.x
        offset_y_left = falling_ring_rect.y - left_obstacle_rect.y
        if left_obstacle_mask.overlap(falling_ring_mask, (offset_x_left, offset_y_left)) and bounce_cooldown == 0:
            years += 1  # <<< MASLA YAHAN THEEK KIYA GAYA HAI
            velocity_y *= -0.6
            velocity_x = random.uniform(2.0, 4.0)
            bounce_cooldown = 10
        
        # Collision with Right Obstacle
        offset_x_right = falling_ring_rect.x - right_obstacle_rect.x
        offset_y_right = falling_ring_rect.y - right_obstacle_rect.y
        if right_obstacle_mask.overlap(falling_ring_mask, (offset_x_right, offset_y_right)) and bounce_cooldown == 0:
            years += 1  # <<< MASLA YAHAN BHI THEEK KIYA GAYA HAI
            velocity_y *= -0.6
            velocity_x = random.uniform(-4.0, -2.0)
            bounce_cooldown = 10
            
        if falling_ring_rect.top > SCREEN_HEIGHT:
            game_state = "game_over"
        
        # Drawing during play
        screen.blit(falling_ring_img, falling_ring_rect)
        screen.blit(left_obstacle_img, left_obstacle_rect)
        screen.blit(right_obstacle_img, right_obstacle_rect)
        text_surface = font.render(f"I have {years} years to get married!", True, WHITE)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(text_surface, text_rect)

    elif game_state == "game_over":
        screen.blit(left_obstacle_img, left_obstacle_rect)
        screen.blit(right_obstacle_img, right_obstacle_rect)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        if game_over_start_time is None:
            game_over_start_time = pygame.time.get_ticks()
        
        elapsed_time = pygame.time.get_ticks() - game_over_start_time
        scale = min(1.0, elapsed_time / zoom_animation_duration)

        years_font_size = int(250 * scale)
        if years_font_size > 0:
            current_zoom_font = pygame.font.Font(None, years_font_size)
            years_text = current_zoom_font.render(str(years), True, WHITE)
            years_rect = years_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(years_text, years_rect)

        if scale >= 1.0:
            top_text = zoom_font_small.render("You have", True, WHITE)
            top_rect = top_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120))
            screen.blit(top_text, top_rect)
            bottom_text = zoom_font_small.render("years to get married!", True, WHITE)
            bottom_rect = bottom_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120))
            screen.blit(bottom_text, bottom_rect)
            again_button = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 120, 300, 80)
            pygame.draw.rect(screen, GRAY, again_button)
            again_text = button_font.render("Play Again", True, BLACK)
            screen.blit(again_text, (again_button.x + 45, again_button.y + 20))

    pygame.display.flip()
    clock.tick(60)

# --- Cleanup ---
cap.release()
pygame.quit()
sys.exit()