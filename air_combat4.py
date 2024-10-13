import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions and settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Air Combat")

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
EXPLOSION_COLOR = (255, 69, 0)

# Fonts
font = pygame.font.Font(None, 36)

# Game variables
PLAYER_SPEED = 5
PROJECTILE_SPEED = 10
ENEMY_PROJECTILE_SPEED = 4
ENEMY_SPEED = 2
SCORE_TO_ADVANCE = 100
BOSS_SCORE = 50
ENEMY_FIRE_INTERVAL = 1000  # 1 second between shots
PLAYER_FIRE_DELAY = 200
EXPLOSION_DURATION = 30
ENEMY_SPAWN_INTERVAL = 3000  # 3 seconds between enemy spawns

# Initialize game state
current_level = 1
boss_spawned = False
player_combo = 0
projectile_power = 1
boss = None  # Reference to the boss object
last_enemy_fire_time = pygame.time.get_ticks()
last_enemy_spawn_time = pygame.time.get_ticks()

# Player class
class PlayerPlane(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, BLUE, [(25, 0), (0, 50), (50, 50)])
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.health = 100
        self.lives = 3
        self.score = 0
        self.last_shot_time = pygame.time.get_ticks()

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += PLAYER_SPEED

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= PLAYER_FIRE_DELAY:
            projectile = Projectile(self.rect.centerx, self.rect.top, -1, projectile_power)
            all_sprites.add(projectile)
            player_projectiles.add(projectile)
            self.last_shot_time = current_time

    def take_damage(self, amount):
        # Reduce player health by the given amount
        self.health -= amount
        if self.health <= 0:
            self.lives -= 1
            self.health = 100
            if self.lives <= 0:
                game_over_prompt()

# Projectile class
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, power):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(YELLOW if direction == -1 else RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.speed = PROJECTILE_SPEED
        self.power = power

    def update(self):
        self.rect.y += self.speed * self.direction
        if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
            self.kill()

# Enemy class
class EnemyPlane(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, RED, [(25, 50), (0, 0), (50, 0)])
        self.rect = self.image.get_rect(center=(x, -40))
        self.health = 3
        self.exploding = False
        self.explosion_time = 0

    def update(self):
        if not self.exploding:
            self.rect.y += ENEMY_SPEED
            if self.rect.top > SCREEN_HEIGHT:
                self.reappear()
        else:
            self.explosion_time += 1
            self.image.fill(EXPLOSION_COLOR)
            if self.explosion_time > EXPLOSION_DURATION:
                self.kill()

    def reappear(self):
        self.rect.centerx = random.randint(50, SCREEN_WIDTH - 50)
        self.rect.y = -40

    def shoot(self):
        projectile = Projectile(self.rect.centerx, self.rect.bottom, 1, 1)
        all_sprites.add(projectile)
        enemy_projectiles.add(projectile)

    def take_damage(self, power):
        self.health -= power
        if self.health <= 0:
            self.exploding = True
            increase_combo()
            player.score += 10
            check_level_progression()

# Boss class
class BossPlane(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, (128, 0, 0), [(50, 100), (0, 0), (100, 0)])
        self.rect = self.image.get_rect(center=(x, 50))
        self.health = 100
        self.speed_x = random.choice([-3, 3])
        self.speed_y = random.choice([-2, 2])
        self.last_shot_time = pygame.time.get_ticks()

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Boss fires projectiles at a rate of 0.5 seconds per projectile
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= 500:
                boss_projectile = Projectile(self.rect.centerx, self.rect.bottom, 1, 2)
                all_sprites.add(boss_projectile)
                enemy_projectiles.add(boss_projectile)
                self.last_shot_time = current_time

        # Boss moves left to right at random
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
                self.speed_x *= -1
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT / 2:
                self.speed_y *= -1

        # Boss moves left to right at random
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
                self.speed_x *= -1

        # Boss fires projectiles at a rate of 0.5 seconds per projectile
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= 500:
                boss_projectile = Projectile(self.rect.centerx, self.rect.bottom, 1, 2)
                all_sprites.add(boss_projectile)
                enemy_projectiles.add(boss_projectile)
                self.last_shot_time = current_time
        self.rect.y += self.speed_y

        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.speed_x *= -1
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT / 2:
            self.speed_y *= -1

    def take_damage(self, power):
        self.health -= power
        if self.health <= 0:
            self.kill()
            print("Boss defeated!")

# Game logic functions
def increase_combo():
    global player_combo, projectile_power
    player_combo += 1
    if player_combo >= 5:
        projectile_power = 3
    elif player_combo >= 3:
        projectile_power = 2

def reset_combo():
    global player_combo, projectile_power
    player_combo = 0
    projectile_power = 1

def check_level_progression():
    global current_level, boss_spawned, boss
    if boss_spawned:
        return
    if player.score >= SCORE_TO_ADVANCE and current_level < 3:
        current_level += 1
        player.health = 100
    if current_level == 3 and player.score >= BOSS_SCORE and not boss_spawned:
        boss = BossPlane(SCREEN_WIDTH // 2)
        all_sprites.add(boss)
        enemies.add(boss)
        boss_spawned = True

def game_over_prompt():
    global boss_spawned
    screen.fill(BLACK)
    game_over_text = font.render("Game Over! Play Again? (Y/N)", True, YELLOW)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    restart_game()
                    waiting = False
                elif event.key == pygame.K_n:
                    pygame.quit()
                    sys.exit()

def restart_game():
    global player, all_sprites, enemies, player_projectiles, enemy_projectiles, current_level, boss_spawned, boss
    player = PlayerPlane()
    all_sprites.empty()
    enemies.empty()
    player_projectiles.empty()
    enemy_projectiles.empty()
    boss = None
    all_sprites.add(player)
    current_level = 1
    boss_spawned = False
    spawn_more_enemies(3)
    reset_combo()

def spawn_more_enemies(count=1):
    if len(enemies) >= 30:
        return
    for _ in range(count):
        x = random.randint(50, SCREEN_WIDTH - 50)
        enemy = EnemyPlane(x)
        all_sprites.add(enemy)
        enemies.add(enemy)

# Initialize game objects
player = PlayerPlane()
all_sprites = pygame.sprite.Group(player)
enemies = pygame.sprite.Group()
player_projectiles = pygame.sprite.Group()
enemy_projectiles = pygame.sprite.Group()

spawn_more_enemies(3)

clock = pygame.time.Clock()
running = True

while running:
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            player.shoot()

    if current_time - last_enemy_fire_time >= ENEMY_FIRE_INTERVAL and enemies and not boss_spawned:
        random.choice(enemies.sprites()).shoot()
        last_enemy_fire_time = current_time

    if current_time - last_enemy_spawn_time >= ENEMY_SPAWN_INTERVAL and not boss_spawned:
        spawn_more_enemies(1)
        last_enemy_spawn_time = current_time

    hits = pygame.sprite.groupcollide(enemies, player_projectiles, False, True)
    for enemy, projectiles in hits.items():
        enemy.take_damage(projectile_power)

    # Check if enemy projectiles hit the player
    player_hits = pygame.sprite.spritecollide(player, enemy_projectiles, True)
    for _ in player_hits:
        player.take_damage(10)

    if boss_spawned and boss:
        boss_hits = pygame.sprite.spritecollide(boss, player_projectiles, True)
        for _ in boss_hits:
                boss.take_damage(projectile_power)
        if not boss.alive():
                boss_spawned = False
                player.score += 50  # Award points for defeating the boss
                congratulations_text = font.render("Congratulations!", True, YELLOW)
                screen.blit(congratulations_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
                pygame.display.flip()
                pygame.time.delay(3000)
                game_over_prompt()  # Ask player if they want to play again after boss is defeated

    all_sprites.update()
    screen.fill(BLACK)
    all_sprites.draw(screen)

    health_text = font.render(f"Health: {player.health}", True, YELLOW)
    score_text = font.render(f"Score: {player.score}", True, YELLOW)
    combo_text = font.render(f"Combo: {player_combo}", True, YELLOW)
    level_text = font.render(f"Level: {current_level}", True, YELLOW)

    screen.blit(health_text, (10, 10))
    screen.blit(score_text, (10, 50))
    screen.blit(combo_text, (10, 90))
    screen.blit(level_text, (10, 130))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()


#https://github.com/Hit137Student/Hit137-Assignment3.git