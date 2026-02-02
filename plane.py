#=============================================================================
#--------------- CodersJaunt Game: Girls On Target ----------------------
#-- A simple 2D shooting game where you control a plane to shoot down Girls👧🏼 --
#----------- Designed with passion and ❤️ by @mit ---------------------
#=============================================================================
import pygame
import random
import os

pygame.init()

# -----------------------------
# Screen setup
# -----------------------------
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Girls On Target")
clock = pygame.time.Clock()

# -----------------------------
# Colors
# -----------------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PINK = (255, 105, 180)
RED_GLOW = (255, 0, 0) # Color for the hit effect

# -----------------------------------------------------------
# Asset Path Dir containing the images
# -----------------------------------------------------------
ASSET_PATH = "assets"

# -----------------------------
# Load Images
# -----------------------------
# (Using try/except to prevent crash if folders are missing during copy/paste)
try:
    background_img = pygame.image.load(os.path.join(ASSET_PATH, "background.png"))
    player_img = pygame.image.load(os.path.join(ASSET_PATH, "plane-animated.png"))
    bullet_img = pygame.image.load(os.path.join(ASSET_PATH, "Bullet.png"))
    blast_img = pygame.image.load(os.path.join(ASSET_PATH, "blast.png"))

    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
    player_img = pygame.transform.scale(player_img, (49, 49))
    bullet_img = pygame.transform.scale(bullet_img, (10, 20))
    blast_img = pygame.transform.scale(blast_img, (40, 40))

    enemy_images = []
    for file in sorted(os.listdir(ASSET_PATH)):
        if file.startswith("envy") and file.endswith(".png"):
            img = pygame.image.load(os.path.join(ASSET_PATH, file))
            img = pygame.transform.scale(img, (40, 40))
            enemy_images.append(img)
            
    if not enemy_images:
        # Fallback if no enemy images found, create a red square
        fallback_surf = pygame.Surface((40,40))
        fallback_surf.fill((255,0,0))
        enemy_images.append(fallback_surf)

except Exception as e:
    print(f"Warning: Issue loading images. Make sure 'assets' folder exists. Error: {e}")
    pygame.quit()
    exit()

# -----------------------------
# Fonts
# -----------------------------
font = pygame.font.SysFont(None, 24)
big_font = pygame.font.SysFont(None, 48)
title_font = pygame.font.SysFont(None, 52)
funny_font = pygame.font.SysFont("comicsansms", 20) # Comic font for the funny msg

# -----------------------------
# Game Objects
# -----------------------------
player = pygame.Rect(WIDTH // 2, HEIGHT - 50, 40, 40)
bullets = []
pagli = []
explosions = []

# -----------------------------
# Game Variables Setup
# -----------------------------
score = 0
lives = 3
missed_girls = 0
max_misses = 5
bullet_cooldown = 0
hit_timer = 0  # <--- NEW VARIABLE: Tracks how long the "Ouch" effect lasts

running = True
paused = False
game_over = False
intro = True

# -----------------------------
# Helper Functions
# -----------------------------
def draw_glowing_enemy(enemy):
    rect = enemy["rect"]
    img = enemy["img"]
    glow = pygame.Surface((60, 60), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (255, 255, 0, 120), glow.get_rect())
    screen.blit(glow, (rect.x - 10, rect.y - 10))
    screen.blit(img, rect)

# -----------------------------
# Intro animation
# -----------------------------
intro_alpha = 0

# -----------------------------
# Main Loop
# -----------------------------
while running:
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if intro and event.key == pygame.K_RETURN:
                intro = False

            if not intro and not game_over and event.key == pygame.K_ESCAPE:
                paused = not paused

            if paused:
                if event.key == pygame.K_c:
                    paused = False
                if event.key == pygame.K_q:
                    running = False

            if game_over and event.key == pygame.K_r:
                game_over = False
                score = 0
                lives = 3
                missed_girls = 0
                hit_timer = 0 # Reset timer
                bullets.clear()
                pagli.clear()
                explosions.clear()
                player.center = (WIDTH // 2, HEIGHT - 50)

    # =====================================================
    # INTRO SCREEN
    # =====================================================
    if intro:
        screen.fill(BLACK)
        intro_alpha = min(255, intro_alpha + 3)
        title = title_font.render("Girls On Target", True, PINK)
        subtitle = font.render("CodersJaunt Game", True, WHITE)
        credit = font.render("Designed with passion and Love by @mit", True, WHITE)
        start = font.render("Press ENTER to Start", True, WHITE)

        for s in (title, subtitle, credit, start): s.set_alpha(intro_alpha)

        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 170))
        screen.blit(credit, (WIDTH // 2 - credit.get_width() // 2, 200))
        screen.blit(start, (WIDTH // 2 - start.get_width() // 2, 260))

        pygame.display.flip()
        clock.tick(30)
        continue

    # =====================================================
    # PAUSE MENU
    # =====================================================
    if paused:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        screen.blit(big_font.render("PAUSED", True, WHITE), (WIDTH // 2 - 80, HEIGHT // 2 - 60))
        screen.blit(font.render("Press C to Continue", True, WHITE), (WIDTH // 2 - 90, HEIGHT // 2))
        screen.blit(font.render("Press Q to Exit", True, WHITE), (WIDTH // 2 - 90, HEIGHT // 2 + 30))
        pygame.display.flip()
        clock.tick(10)
        continue

    # =====================================================
    # GAME OVER
    # =====================================================
    if game_over:
        screen.fill(BLACK)
        screen.blit(big_font.render("GAME OVER!", True, WHITE), (WIDTH // 2 - 110, HEIGHT // 2 - 40))
        screen.blit(font.render("Press R to Restart", True, WHITE), (WIDTH // 2 - 90, HEIGHT // 2 + 10))
        pygame.display.flip()
        clock.tick(10)
        continue

    # =====================================================
    # GAME LOGIC
    # =====================================================
    screen.blit(background_img, (0, 0))

    # Player movement
    if keys[pygame.K_LEFT] and player.x > 0: player.x -= 5
    if keys[pygame.K_RIGHT] and player.x < WIDTH - 40: player.x += 5
    if keys[pygame.K_UP] and player.y > 0: player.y -= 5
    if keys[pygame.K_DOWN] and player.y < HEIGHT - 40: player.y += 5

    # Shooting
    if keys[pygame.K_SPACE] and bullet_cooldown == 0:
        bullets.append(pygame.Rect(player.x + 15, player.y, 10, 20))
        bullet_cooldown = 10
    if bullet_cooldown > 0: bullet_cooldown -= 1

    for bullet in bullets[:]:
        bullet.y -= 7
        if bullet.y < 0: bullets.remove(bullet)
        else: screen.blit(bullet_img, bullet)

    # Enemy spawn
    if len(pagli) == 0 and random.randint(1, 50) == 1:
        rect = pygame.Rect(random.randint(0, WIDTH - 40), 0, 40, 40)
        img = random.choice(enemy_images)
        pagli.append({"rect": rect, "img": img})

    for enemy in pagli[:]:
        enemy["rect"].y += 3
        if enemy["rect"].y > HEIGHT:
            pagli.remove(enemy)
            missed_girls += 1
            if missed_girls >= max_misses: game_over = True
            continue

        draw_glowing_enemy(enemy)

        # Bullet Collision
        for bullet in bullets[:]:
            if enemy["rect"].colliderect(bullet):
                bullets.remove(bullet)
                explosions.append([enemy["rect"].x, enemy["rect"].y, 10])
                pagli.remove(enemy)
                score += 1
                break

        # -------------------------------------------------
        # PLAYER COLLISION & HIT EFFECT LOGIC 🔥
        # -------------------------------------------------
        if enemy["rect"].colliderect(player):
            pagli.remove(enemy)
            lives -= 1
            
            # Start the visual effect timer (45 frames = 1.5 seconds)
            hit_timer = 45 

            if lives <= 0:
                game_over = True

    # Explosion Animation
    for blast in explosions[:]:
        screen.blit(blast_img, (blast[0], blast[1]))
        blast[2] -= 1
        if blast[2] <= 0: explosions.remove(blast)

    # -------------------------------------------------
    # UI DRAWING (With Hit Effect)
    # -------------------------------------------------
    screen.blit(player_img, player)

    # 1. If hit_timer is active, draw the RED GLOW behind score/lives
    if hit_timer > 0:
        # Create a red transparent surface
        damage_overlay = pygame.Surface((150, 60), pygame.SRCALPHA)
        damage_overlay.fill((255, 0, 0, 128)) # Red with 50% transparency
        screen.blit(damage_overlay, (0, 0)) # Position at top left
        
        # Draw the Funny Message on pagli hits
        msg = funny_font.render("Tu to gaya Beta!!", True, (255, 50, 50))
        # Center the text above the player
        screen.blit(msg, (player.x - 40, player.y - 40))
        
        # Decrease timer
        hit_timer -= 1

    # Draw Score and Lives on top
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Lives: {lives}", True, WHITE), (10, 30))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()