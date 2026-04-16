import pygame
import random
import json
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Game constants
WIDTH = 800
HEIGHT = 600
FPS = 60
PLAYER_SPEED = 5
BULLET_SPEED = 7
ENEMY_SPEED = 2
MAX_ENEMIES = 15  # Limit number of enemies
MAX_ASTEROIDS = 10  # Limit number of asteroids

# Game state
current_level = 1
max_level = 5
boss_active = False
boss_health = 0
boss_defeated = False
sector_completed = False
game_state = "menu"  # menu, playing, game_over, sector_complete, ship_select, upgrade_shop, encounter, power_management

# Ship system
total_points = 0  # Points earned from all gameplay
selected_ship = 0  # Currently selected ship index
owned_ships = [True, False, False, False, False]  # Which ships are owned (first one is always owned)

# Ship definitions: [name, cost, health_bonus, speed_bonus, damage_bonus]
SHIP_DATA = [
    ["Rookie Fighter", 0, 0, 0, 0],           # Starting ship
    ["Interceptor", 500, 10, 2, 0],           # Fast ship
    ["Battlecruiser", 1000, 50, -1, 1],       # Tank ship
    ["Stealth Bomber", 1500, 0, 1, 2],        # High damage
    ["Mothership", 2500, 100, 0, 3]           # Ultimate ship
]

# Ship upgrade system
ship_upgrades = {
    'weapons': {'level': 1, 'max_level': 4, 'cost': [100, 200, 300], 'description': 'Weapon Systems'},
    'shields': {'level': 1, 'max_level': 4, 'cost': [150, 250, 350], 'description': 'Shield Systems'},
    'engines': {'level': 1, 'max_level': 3, 'cost': [120, 200], 'description': 'Engine Systems'},
    'oxygen': {'level': 1, 'max_level': 3, 'cost': [80, 150], 'description': 'Life Support'},
    'medical': {'level': 1, 'max_level': 3, 'cost': [100, 180], 'description': 'Medical Bay'},
    'sensors': {'level': 1, 'max_level': 3, 'cost': [90, 160], 'description': 'Sensor Array'}
}

# Crew system
crew_members = [
    {'name': 'Captain', 'type': 'human', 'health': 100, 'station': 'bridge', 'skills': {'pilot': 3, 'weapons': 2, 'repair': 2}},
    {'name': 'Engineer', 'type': 'engi', 'health': 80, 'station': 'engines', 'skills': {'repair': 4, 'pilot': 1, 'weapons': 1}},
    {'name': 'Gunner', 'type': 'mantis', 'health': 120, 'station': 'weapons', 'skills': {'weapons': 4, 'pilot': 1, 'repair': 2}}
]

# Power management system
power_system = {
    'total_power': 8,
    'allocation': {'weapons': 2, 'shields': 2, 'engines': 2, 'oxygen': 1, 'medical': 1, 'sensors': 0},
    'max_allocation': {'weapons': 4, 'shields': 4, 'engines': 3, 'oxygen': 2, 'medical': 2, 'sensors': 2}
}

# Event system
current_event = None
encounter_active = False
pause_game = False

# Power-up constants
POWERUP_TYPES = ['speed', 'health', 'rapid_fire', 'shield', 'double_shot']
POWERUP_DURATION = 5000  # 5 seconds

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
PINK = (255, 192, 203)

# Initialize screen and clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter - Enhanced Edition")
clock = pygame.time.Clock()

# Initialize sound effects (create simple tones if no files exist)
def create_sound_effects():
    try:
        # Try to load sound files if they exist
        shoot_sound = pygame.mixer.Sound("shoot.wav")
        explosion_sound = pygame.mixer.Sound("explosion.wav")
        powerup_sound = pygame.mixer.Sound("powerup.wav")
        boss_music = pygame.mixer.Sound("boss.wav")
    except:
        # Create simple programmatic sounds if files don't exist
        shoot_sound = pygame.mixer.Sound(buffer=b'\x00' * 4410)  # Simple beep
        explosion_sound = pygame.mixer.Sound(buffer=b'\x00' * 8820)
        powerup_sound = pygame.mixer.Sound(buffer=b'\x00' * 4410)
        boss_music = pygame.mixer.Sound(buffer=b'\x00' * 22050)
    return shoot_sound, explosion_sound, powerup_sound, boss_music

shoot_sound, explosion_sound, powerup_sound, boss_music = create_sound_effects()

# Try to load background music
try:
    pygame.mixer.music.load("background.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)  # Loop indefinitely
except:
    pass  # No background music file found

# Create space-like sprites
def create_player(ship_type=0):
    surf = pygame.Surface((50, 50), pygame.SRCALPHA)
    
    if ship_type == 0:  # Rookie Fighter
        # Main body
        pygame.draw.polygon(surf, BLUE, [(25,0), (40,40), (25,30), (10,40)])
        # Wings
        pygame.draw.polygon(surf, GRAY, [(10,25), (0,45), (10,40)])
        pygame.draw.polygon(surf, GRAY, [(40,25), (50,45), (40,40)])
        # Cockpit
        pygame.draw.circle(surf, CYAN, (25, 15), 5)
        # Engine glow
        pygame.draw.rect(surf, YELLOW, (22, 45, 6, 5))
        
    elif ship_type == 1:  # Interceptor
        # Sleek body
        pygame.draw.polygon(surf, GREEN, [(25,0), (35,35), (25,25), (15,35)])
        # Side thrusters
        pygame.draw.polygon(surf, GRAY, [(5,20), (15,30), (15,35), (5,40)])
        pygame.draw.polygon(surf, GRAY, [(45,20), (35,30), (35,35), (45,40)])
        # Cockpit
        pygame.draw.circle(surf, WHITE, (25, 12), 4)
        # Twin engines
        pygame.draw.rect(surf, ORANGE, (20, 40, 4, 6))
        pygame.draw.rect(surf, ORANGE, (26, 40, 4, 6))
        
    elif ship_type == 2:  # Battlecruiser
        # Heavy body
        pygame.draw.rect(surf, PURPLE, (15, 10, 20, 35))
        # Armor plating
        pygame.draw.rect(surf, GRAY, (10, 15, 30, 25))
        # Weapon pods
        pygame.draw.rect(surf, RED, (5, 20, 8, 15))
        pygame.draw.rect(surf, RED, (37, 20, 8, 15))
        # Bridge
        pygame.draw.rect(surf, CYAN, (20, 5, 10, 10))
        # Main engine
        pygame.draw.rect(surf, YELLOW, (18, 45, 14, 5))
        
    elif ship_type == 3:  # Stealth Bomber
        # Angular stealth body
        pygame.draw.polygon(surf, (64, 64, 64), [(25,0), (45,20), (35,45), (15,45), (5,20)])
        # Stealth coating
        pygame.draw.polygon(surf, (32, 32, 32), [(25,5), (40,18), (30,40), (20,40), (10,18)])
        # Weapon bay
        pygame.draw.rect(surf, RED, (20, 20, 10, 15))
        # Stealth engine
        pygame.draw.rect(surf, BLUE, (22, 40, 6, 8))
        
    elif ship_type == 4:  # Mothership
        # Massive body
        pygame.draw.ellipse(surf, (128, 128, 128), (5, 5, 40, 40))
        # Central core
        pygame.draw.circle(surf, YELLOW, (25, 25), 15)
        # Outer ring
        pygame.draw.circle(surf, BLUE, (25, 25), 20, 3)
        # Weapon arrays
        pygame.draw.rect(surf, RED, (2, 20, 6, 10))
        pygame.draw.rect(surf, RED, (42, 20, 6, 10))
        pygame.draw.rect(surf, RED, (20, 2, 10, 6))
        # Engine cluster
        pygame.draw.rect(surf, ORANGE, (20, 45, 10, 5))
        
    return surf

def create_enemy():
    surf = pygame.Surface((40, 40), pygame.SRCALPHA)
    # Enemy ship body
    pygame.draw.polygon(surf, RED, [(20,0), (35,30), (20,25), (5,30)])
    # Wings
    pygame.draw.polygon(surf, (128, 0, 0), [(5,15), (0,25), (5,30)])
    pygame.draw.polygon(surf, (128, 0, 0), [(35,15), (40,25), (35,30)])
    # Cockpit
    pygame.draw.circle(surf, ORANGE, (20, 10), 3)
    # Engine
    pygame.draw.rect(surf, YELLOW, (18, 35, 4, 5))
    return surf

def create_bullet():
    surf = pygame.Surface((6, 15), pygame.SRCALPHA)
    # Plasma bolt
    pygame.draw.ellipse(surf, CYAN, (0, 0, 6, 15))
    pygame.draw.ellipse(surf, WHITE, (1, 2, 4, 11))
    return surf

def create_asteroid():
    surf = pygame.Surface((40, 40), pygame.SRCALPHA)
    # Irregular asteroid shape
    points = [(20,0), (35,5), (40,15), (38,25), (35,35), (25,40), (15,38), (5,30), (0,20), (5,10), (15,5)]
    pygame.draw.polygon(surf, GRAY, points)
    # Surface details
    pygame.draw.circle(surf, (80, 80, 80), (15, 15), 3)
    pygame.draw.circle(surf, (80, 80, 80), (25, 25), 2)
    pygame.draw.circle(surf, (80, 80, 80), (30, 12), 2)
    return surf

def create_powerup(ptype):
    surf = pygame.Surface((25, 25), pygame.SRCALPHA)
    if ptype == 'speed':
        # Speed booster
        pygame.draw.polygon(surf, GREEN, [(12,0), (25,12), (12,25), (0,12)])
        pygame.draw.polygon(surf, WHITE, [(12,5), (20,12), (12,20), (5,12)])
        pygame.draw.polygon(surf, GREEN, [(10,8), (15,12), (10,16), (5,12)])
    elif ptype == 'health':
        # Medical kit
        pygame.draw.rect(surf, WHITE, (5, 5, 15, 15))
        pygame.draw.rect(surf, RED, (8, 10, 9, 5))
        pygame.draw.rect(surf, RED, (10, 8, 5, 9))
    elif ptype == 'rapid_fire':
        # Weapon upgrade
        pygame.draw.polygon(surf, YELLOW, [(12,0), (20,8), (12,16), (4,8)])
        pygame.draw.rect(surf, ORANGE, (10, 6, 4, 4))
        pygame.draw.rect(surf, RED, (11, 7, 2, 2))
    elif ptype == 'shield':
        # Shield generator
        pygame.draw.circle(surf, CYAN, (12, 12), 10)
        pygame.draw.circle(surf, BLUE, (12, 12), 8, 2)
        pygame.draw.circle(surf, WHITE, (12, 12), 6, 1)
    elif ptype == 'double_shot':
        # Twin cannon
        pygame.draw.rect(surf, PURPLE, (5, 10, 15, 5))
        pygame.draw.circle(surf, ORANGE, (8, 12), 2)
        pygame.draw.circle(surf, ORANGE, (17, 12), 2)
    return surf

def create_fast_enemy():
    surf = pygame.Surface((30, 30), pygame.SRCALPHA)
    # Fast scout ship
    pygame.draw.polygon(surf, ORANGE, [(15,0), (25,20), (15,15), (5,20)])
    # Engines
    pygame.draw.rect(surf, YELLOW, (12, 25, 6, 5))
    # Cockpit
    pygame.draw.circle(surf, RED, (15, 8), 2)
    return surf

def create_tank_enemy():
    surf = pygame.Surface((50, 50), pygame.SRCALPHA)
    # Heavy assault ship
    pygame.draw.rect(surf, PURPLE, (10, 10, 30, 30))
    # Armor plating
    pygame.draw.rect(surf, GRAY, (5, 15, 40, 20))
    # Weapon turrets
    pygame.draw.circle(surf, RED, (15, 25), 5)
    pygame.draw.circle(surf, RED, (35, 25), 5)
    # Bridge
    pygame.draw.rect(surf, CYAN, (20, 5, 10, 10))
    # Engines
    pygame.draw.rect(surf, YELLOW, (15, 40, 20, 8))
    return surf

def create_boss():
    surf = pygame.Surface((100, 100), pygame.SRCALPHA)
    # Main hull
    pygame.draw.ellipse(surf, RED, (10, 20, 80, 60))
    # Command bridge
    pygame.draw.rect(surf, YELLOW, (30, 10, 40, 20))
    # Weapon arrays
    pygame.draw.rect(surf, GRAY, (5, 35, 15, 10))
    pygame.draw.rect(surf, GRAY, (80, 35, 15, 10))
    pygame.draw.rect(surf, GRAY, (40, 5, 20, 10))
    # Engine cluster
    pygame.draw.rect(surf, ORANGE, (20, 85, 60, 10))
    # Armor details
    pygame.draw.circle(surf, (128, 0, 0), (30, 50), 8)
    pygame.draw.circle(surf, (128, 0, 0), (50, 50), 12)
    pygame.draw.circle(surf, (128, 0, 0), (70, 50), 8)
    # Weapon ports
    pygame.draw.circle(surf, BLACK, (25, 50), 3)
    pygame.draw.circle(surf, BLACK, (50, 50), 4)
    pygame.draw.circle(surf, BLACK, (75, 50), 3)
    return surf

def create_enemy_bullet():
    surf = pygame.Surface((4, 12), pygame.SRCALPHA)
    # Enemy plasma
    pygame.draw.ellipse(surf, RED, (0, 0, 4, 12))
    pygame.draw.ellipse(surf, ORANGE, (1, 2, 2, 8))
    return surf

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.update_ship()
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 50)
        self.base_health = 100
        self.health = self.base_health + SHIP_DATA[selected_ship][2]
        self.max_health = self.base_health + SHIP_DATA[selected_ship][2]
        self.score = 0
        self.last_shot = 0
        self.base_speed = PLAYER_SPEED
        self.speed = self.base_speed + SHIP_DATA[selected_ship][3]
        self.shoot_delay = 200
        self.shield = False
        self.shield_time = 0
        self.double_shot = False
        self.double_shot_time = 0
        self.power_up_timers = {}
        self.damage_bonus = SHIP_DATA[selected_ship][4]

    def update_ship(self):
        """Update the player's ship sprite based on selected ship"""
        self.image = create_player(selected_ship)

    def update(self):
        # Handle power-up timers
        current_time = pygame.time.get_ticks()
        for power_type in list(self.power_up_timers.keys()):
            if current_time - self.power_up_timers[power_type] > POWERUP_DURATION:
                self.remove_power_up(power_type)
        
        # Engine power affects speed
        effective_speed = self.speed + power_system['allocation']['engines']
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= effective_speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += effective_speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= effective_speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += effective_speed
        
        # Continuous firing (only if weapon power > 0) - Use different key for firing
        if keys[pygame.K_LCTRL] and power_system['allocation']['weapons'] > 0:
            self.shoot()

    def apply_power_up(self, power_type):
        current_time = pygame.time.get_ticks()
        self.power_up_timers[power_type] = current_time
        
        if power_type == 'speed':
            self.speed = (self.base_speed + SHIP_DATA[selected_ship][3]) * 2
        elif power_type == 'health':
            self.health = min(self.max_health, self.health + 30)
        elif power_type == 'rapid_fire':
            self.shoot_delay = 50
        elif power_type == 'shield':
            self.shield = True
            self.shield_time = current_time
        elif power_type == 'double_shot':
            self.double_shot = True
            self.double_shot_time = current_time

    def remove_power_up(self, power_type):
        if power_type in self.power_up_timers:
            del self.power_up_timers[power_type]
        
        if power_type == 'speed':
            self.speed = self.base_speed + SHIP_DATA[selected_ship][3]
        elif power_type == 'rapid_fire':
            self.shoot_delay = 200
        elif power_type == 'shield':
            self.shield = False
        elif power_type == 'double_shot':
            self.double_shot = False

    def shoot(self):
        now = pygame.time.get_ticks()
        # Fire rate affected by weapon power
        effective_delay = max(50, self.shoot_delay - (power_system['allocation']['weapons'] * 30))
        
        if now - self.last_shot > effective_delay:
            self.last_shot = now
            try:
                shoot_sound.play()
            except:
                pass
            
            # Number of shots affected by weapon power
            shots = 1 + (power_system['allocation']['weapons'] // 2)
            
            if self.double_shot:
                for i in range(shots):
                    bullet1 = Bullet(self.rect.centerx - 15 - i*5, self.rect.top)
                    bullet2 = Bullet(self.rect.centerx + 15 + i*5, self.rect.top)
                    all_sprites.add(bullet1, bullet2)
                    bullets.add(bullet1, bullet2)
            else:
                for i in range(shots):
                    bullet = Bullet(self.rect.centerx + (i-shots//2)*10, self.rect.top)
                    all_sprites.add(bullet)
                    bullets.add(bullet)

    def take_damage(self, damage):
        if not self.shield:
            self.health -= damage
            return True
        return False

    def reset_for_new_game(self):
        """Reset player stats for a new game"""
        self.update_ship()
        self.rect.center = (WIDTH // 2, HEIGHT - 50)
        self.health = self.base_health + SHIP_DATA[selected_ship][2]
        self.max_health = self.base_health + SHIP_DATA[selected_ship][2]
        self.score = 0
        self.speed = self.base_speed + SHIP_DATA[selected_ship][3]
        self.shoot_delay = 200
        self.shield = False
        self.double_shot = False
        self.power_up_timers = {}
        self.damage_bonus = SHIP_DATA[selected_ship][4]

class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type='basic'):
        super().__init__()
        self.enemy_type = enemy_type
        self.last_shot = 0
        self.shoot_delay = 1000
        
        if enemy_type == 'basic':
            self.image = create_enemy()
            self.health = 1
            self.speed = random.randrange(1, ENEMY_SPEED + 1)
            self.score_value = 10
        elif enemy_type == 'fast':
            self.image = create_fast_enemy()
            self.health = 1
            self.speed = random.randrange(3, 6)
            self.score_value = 15
        elif enemy_type == 'tank':
            self.image = create_tank_enemy()
            self.health = 3
            self.speed = random.randrange(1, 2)
            self.score_value = 25
            self.shoot_delay = 800
        
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)

    def update(self):
        self.rect.y += self.speed
        
        # Tank enemies can shoot
        if self.enemy_type == 'tank':
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shoot_delay and self.rect.y > 0:
                self.last_shot = now
                self.shoot()
        
        if self.rect.top > HEIGHT + 10:
            self.kill()

    def shoot(self):
        bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
        all_sprites.add(bullet)
        enemy_bullets.add(bullet)

    def take_damage(self):
        self.health -= 1
        if self.health <= 0:
            try:
                explosion_sound.play()
            except:
                pass
            return True
        return False

class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = create_asteroid()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 3)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            self.image = pygame.transform.rotate(create_asteroid(), self.rot)
            self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10:
            self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = create_bullet()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y

    def update(self):
        self.rect.y -= BULLET_SPEED
        if self.rect.bottom < 0:
            self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = create_enemy_bullet()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.power_type = random.choice(POWERUP_TYPES)
        self.image = create_powerup(self.power_type)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = create_boss()
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.y = -120
        self.health = 50
        self.max_health = 50
        self.speed = 1
        self.direction = 1
        self.last_shot = 0
        self.shoot_delay = 500
        self.phase = 1

    def update(self):
        # Boss movement pattern
        if self.rect.y < 50:
            self.rect.y += self.speed
        else:
            self.rect.x += self.direction * 2
            if self.rect.right >= WIDTH or self.rect.left <= 0:
                self.direction *= -1
        
        # Boss shooting
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            self.shoot()

    def shoot(self):
        # Boss shoots multiple bullets
        for i in range(3):
            angle = -90 + (i - 1) * 30  # Spread shots
            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)

    def take_damage(self):
        self.health -= 1
        if self.health <= 0:
            try:
                explosion_sound.play()
            except:
                pass
            return True
        return False

# Sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
asteroids = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()
bosses = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# Game loop
running = True
game_over = False
level_complete = False
show_level_text = False
level_text_timer = 0

# Create starfield background
def create_starfield():
    """Create a starfield background"""
    stars = []
    for _ in range(100):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        brightness = random.randint(100, 255)
        stars.append([x, y, brightness])
    return stars

def draw_starfield(stars):
    """Draw and animate the starfield"""
    for star in stars:
        pygame.draw.circle(screen, (star[2], star[2], star[2]), (int(star[0]), int(star[1])), 1)
        # Move stars down slowly
        star[1] += 0.5
        if star[1] > HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, WIDTH)

starfield = create_starfield()

# Save/Load System
SAVE_FILE = "space_game_save.json"

def save_game():
    """Save game progress to file"""
    save_data = {
        'total_points': total_points,
        'current_level': current_level,
        'selected_ship': selected_ship,
        'owned_ships': owned_ships,
        'ship_upgrades': ship_upgrades,
        'power_system': power_system,
        'crew_members': crew_members
    }
    
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(save_data, f, indent=2)
        print(f"Game saved successfully to {SAVE_FILE}")
    except Exception as e:
        print(f"Error saving game: {e}")

def load_game():
    """Load game progress from file"""
    global total_points, current_level, selected_ship, owned_ships, ship_upgrades, power_system, crew_members
    
    if not os.path.exists(SAVE_FILE):
        print("No save file found. Starting new game.")
        return False
    
    try:
        with open(SAVE_FILE, 'r') as f:
            save_data = json.load(f)
        
        total_points = save_data.get('total_points', 0)
        current_level = save_data.get('current_level', 1)
        selected_ship = save_data.get('selected_ship', 0)
        owned_ships = save_data.get('owned_ships', [True, False, False, False, False])
        ship_upgrades = save_data.get('ship_upgrades', ship_upgrades)
        power_system = save_data.get('power_system', power_system)
        crew_members = save_data.get('crew_members', crew_members)
        
        print(f"Game loaded successfully from {SAVE_FILE}")
        return True
    except Exception as e:
        print(f"Error loading game: {e}")
        return False

def reset_save():
    """Reset save file to default values"""
    global total_points, current_level, selected_ship, owned_ships, ship_upgrades, power_system, crew_members
    
    total_points = 0
    current_level = 1
    selected_ship = 0
    owned_ships = [True, False, False, False, False]
    
    # Reset ship upgrades
    ship_upgrades = {
        'weapons': {'level': 1, 'max_level': 4, 'cost': [100, 200, 300], 'description': 'Weapon Systems'},
        'shields': {'level': 1, 'max_level': 4, 'cost': [150, 250, 350], 'description': 'Shield Systems'},
        'engines': {'level': 1, 'max_level': 3, 'cost': [120, 200], 'description': 'Engine Systems'},
        'oxygen': {'level': 1, 'max_level': 3, 'cost': [80, 150], 'description': 'Life Support'},
        'medical': {'level': 1, 'max_level': 3, 'cost': [100, 180], 'description': 'Medical Bay'},
        'sensors': {'level': 1, 'max_level': 3, 'cost': [90, 160], 'description': 'Sensor Array'}
    }
    
    # Reset power system
    power_system = {
        'total_power': 8,
        'allocation': {'weapons': 2, 'shields': 2, 'engines': 2, 'oxygen': 1, 'medical': 1, 'sensors': 0},
        'max_allocation': {'weapons': 4, 'shields': 4, 'engines': 3, 'oxygen': 2, 'medical': 2, 'sensors': 2}
    }
    
    # Reset crew
    crew_members = [
        {'name': 'Captain', 'type': 'human', 'health': 100, 'station': 'bridge', 'skills': {'pilot': 3, 'weapons': 2, 'repair': 2}},
        {'name': 'Engineer', 'type': 'engi', 'health': 80, 'station': 'engines', 'skills': {'repair': 4, 'pilot': 1, 'weapons': 1}},
        {'name': 'Gunner', 'type': 'mantis', 'health': 120, 'station': 'weapons', 'skills': {'weapons': 4, 'pilot': 1, 'repair': 2}}
    ]
    
    save_game()
    print("Save file reset to default values.")

# Load game on startup
load_game()

def generate_encounter():
    """Generate a random encounter with meaningful consequences"""
    encounters = [
        {
            'description': [
                "CRITICAL: Pirate fleet detected on intercept course!",
                "Three heavily armed ships approaching fast.",
                "Your shields are at full power, but they outnumber you."
            ],
            'options': [
                {'text': 'Engage in combat', 'type': 'combat', 'reward': 100, 'risk': 'heavy_damage'},
                {'text': 'Attempt to outrun them', 'type': 'escape', 'reward': 0, 'risk': 'engine_damage'},
                {'text': 'Surrender cargo', 'type': 'surrender', 'reward': -50, 'risk': 'crew_morale'}
            ]
        },
        {
            'description': [
                "ANOMALY: Massive energy signature detected!",
                "A derelict alien mothership drifts in the void.",
                "Scans show advanced technology but unstable reactors."
            ],
            'options': [
                {'text': 'Board and salvage', 'type': 'explore', 'reward': 200, 'risk': 'crew_injury'},
                {'text': 'Scan from safe distance', 'type': 'scan', 'reward': 50, 'risk': 'none'},
                {'text': 'Mark location and continue', 'type': 'ignore', 'reward': 20, 'risk': 'none'}
            ]
        },
        {
            'description': [
                "DISTRESS: Civilian transport under attack!",
                "A merchant vessel is being overwhelmed by raiders.",
                "They're broadcasting SOS on all frequencies."
            ],
            'options': [
                {'text': 'Rescue the civilians', 'type': 'rescue', 'reward': 80, 'risk': 'combat'},
                {'text': 'Create a distraction', 'type': 'distract', 'reward': 40, 'risk': 'light_damage'},
                {'text': 'Call for backup', 'type': 'backup', 'reward': 30, 'risk': 'delay'}
            ]
        },
        {
            'description': [
                "SYSTEM FAILURE: Critical malfunction detected!",
                "Your ship's life support is failing rapidly.",
                "Oxygen levels dropping, crew health at risk."
            ],
            'options': [
                {'text': 'Emergency repairs', 'type': 'repair', 'reward': 0, 'risk': 'power_loss'},
                {'text': 'Reroute power systems', 'type': 'power_reroute', 'reward': 10, 'risk': 'system_damage'},
                {'text': 'Find nearest station', 'type': 'emergency_dock', 'reward': 0, 'risk': 'time_loss'}
            ]
        }
    ]
    return random.choice(encounters)

def resolve_encounter(choice_index):
    """Resolve the encounter based on player choice with meaningful consequences"""
    global total_points, current_event, encounter_active, game_state, player
    
    if current_event and choice_index < len(current_event['options']):
        option = current_event['options'][choice_index]
        
        # Award points based on choice
        points_gained = option['reward']
        
        # Enhanced outcomes based on choice type and ship systems
        if option['type'] == 'combat':
            # Combat success depends on weapon power
            weapon_power = power_system['allocation']['weapons']
            if weapon_power >= 3:
                points_gained += 50
                # Add message: "Superior firepower overwhelms the enemy!"
            elif weapon_power >= 2:
                points_gained += 20
            else:
                points_gained = max(0, points_gained - 30)
                # Take damage if underpowered
                player.health = max(1, player.health - 20)
                
        elif option['type'] == 'escape':
            # Escape success depends on engine power
            engine_power = power_system['allocation']['engines']
            if engine_power >= 2:
                points_gained += 30
            else:
                points_gained = max(0, points_gained - 20)
                # Take damage if can't escape
                player.health = max(1, player.health - 15)
                
        elif option['type'] == 'explore':
            # Exploration success depends on sensors
            sensor_power = power_system['allocation']['sensors']
            if sensor_power >= 2:
                points_gained += 100  # Big bonus for high sensors
            elif sensor_power >= 1:
                points_gained += 50
            else:
                # Risk without good sensors
                if random.random() < 0.4:
                    points_gained = max(0, points_gained - 50)
                    player.health = max(1, player.health - 25)
                    
        elif option['type'] == 'scan':
            # Scanning always works better with sensors
            sensor_power = power_system['allocation']['sensors']
            points_gained += sensor_power * 20
            
        elif option['type'] == 'repair':
            # Repair success depends on medical bay
            medical_power = power_system['allocation']['medical']
            if medical_power >= 2:
                # Successful repair
                points_gained += 20
                # Heal crew
                for crew in crew_members:
                    crew['health'] = min(100, crew['health'] + 20)
            else:
                # Partial repair only
                points_gained = max(0, points_gained - 10)
        
        total_points += points_gained
        save_game()  # Save encounter rewards
        
        # Handle major risks with real consequences
        if option['risk'] == 'heavy_damage':
            if random.random() < 0.5:  # 50% chance
                player.health = max(1, player.health - 30)
                # Damage random crew
                damaged_crew = random.choice(crew_members)
                damaged_crew['health'] = max(0, damaged_crew['health'] - 40)
                
        elif option['risk'] == 'crew_injury':
            if random.random() < 0.3:  # 30% chance
                injured_crew = random.choice(crew_members)
                injured_crew['health'] = max(0, injured_crew['health'] - 30)
                
        elif option['risk'] == 'power_loss':
            # Temporarily reduce power
            power_system['total_power'] = max(6, power_system['total_power'] - 1)
            # Rebalance power allocation
            total_allocated = sum(power_system['allocation'].values())
            if total_allocated > power_system['total_power']:
                # Reduce power from random system
                systems = list(power_system['allocation'].keys())
                random_system = random.choice(systems)
                if power_system['allocation'][random_system] > 0:
                    power_system['allocation'][random_system] -= 1
                    
        elif option['risk'] == 'system_damage':
            # Reduce max power for random system
            systems = list(power_system['max_allocation'].keys())
            random_system = random.choice(systems)
            if power_system['max_allocation'][random_system] > 1:
                power_system['max_allocation'][random_system] -= 1
                # Adjust current allocation if needed
                if power_system['allocation'][random_system] > power_system['max_allocation'][random_system]:
                    power_system['allocation'][random_system] = power_system['max_allocation'][random_system]
        
        current_event = None
        encounter_active = False
        game_state = "playing"

def draw_galaxy_map():
    """Draw the galaxy map with colored sectors"""
    screen.fill(BLACK)
    
    # Title
    title_font = pygame.font.Font(None, 64)
    title_text = title_font.render("SPACE SHOOTER", True, WHITE)
    screen.blit(title_text, (WIDTH//2 - 180, 20))
    
    # Subtitle
    subtitle_font = pygame.font.Font(None, 28)
    subtitle_text = subtitle_font.render("Enhanced Edition", True, YELLOW)
    screen.blit(subtitle_text, (WIDTH//2 - 85, 60))
    
    # Left column - Status Information
    status_font = pygame.font.Font(None, 24)
    y_offset = 100
    
    # Points display
    points_text = status_font.render(f"Total Points: {total_points}", True, CYAN)
    screen.blit(points_text, (20, y_offset))
    y_offset += 25
    
    # Current ship display
    ship_text = status_font.render(f"Ship: {SHIP_DATA[selected_ship][0]}", True, CYAN)
    screen.blit(ship_text, (20, y_offset))
    y_offset += 25
    
    # Upgrade levels display
    upgrade_text = status_font.render(f"Upgrades: W{ship_upgrades['weapons']['level']} S{ship_upgrades['shields']['level']} E{ship_upgrades['engines']['level']}", True, CYAN)
    screen.blit(upgrade_text, (20, y_offset))
    y_offset += 25
    
    # Power allocation display
    power_text = status_font.render(f"Power: {sum(power_system['allocation'].values())}/{power_system['total_power']}", True, CYAN)
    screen.blit(power_text, (20, y_offset))
    y_offset += 25
    
    # Current level display
    level_text = status_font.render(f"Current Sector: {current_level}", True, CYAN)
    screen.blit(level_text, (20, y_offset))
    
    # Galaxy map sectors (centered)
    sector_size = 70
    start_x = WIDTH//2 - (max_level * sector_size)//2
    start_y = 150
    
    for i in range(max_level):
        sector_x = start_x + i * sector_size
        sector_y = start_y
        
        # Choose color based on level completion
        if i + 1 < current_level:
            color = GREEN  # Completed
        elif i + 1 == current_level:
            color = YELLOW  # Available to play
        else:
            color = RED  # Locked
        
        # Draw sector
        pygame.draw.rect(screen, color, (sector_x, sector_y, sector_size - 5, sector_size - 5))
        pygame.draw.rect(screen, WHITE, (sector_x, sector_y, sector_size - 5, sector_size - 5), 2)
        
        # Draw level number
        level_font = pygame.font.Font(None, 40)
        level_text = level_font.render(str(i + 1), True, BLACK)
        text_rect = level_text.get_rect(center=(sector_x + sector_size//2 - 2, sector_y + sector_size//2 - 2))
        screen.blit(level_text, text_rect)
    
    # Instructions section (bottom)
    instruction_font = pygame.font.Font(None, 22)
    instruction_y = 280
    
    if current_level <= max_level:
        instruction_text = instruction_font.render(f"Press {current_level} to play Sector {current_level}", True, WHITE)
        screen.blit(instruction_text, (WIDTH//2 - 100, instruction_y))
        instruction_y += 25
    else:
        instruction_text = instruction_font.render("All sectors completed! Congratulations!", True, GREEN)
        screen.blit(instruction_text, (WIDTH//2 - 160, instruction_y))
        instruction_y += 25
    
    # Menu options
    menu_options = [
        "S - Ship Selection",
        "U - Upgrades",
        "P - Power Management",
        "R - Reset Progress"
    ]
    
    for i, option in enumerate(menu_options):
        option_text = instruction_font.render(option, True, WHITE)
        screen.blit(option_text, (WIDTH//2 - 80, instruction_y + i * 25))
    
    # Legend (bottom left)
    legend_font = pygame.font.Font(None, 18)
    legend_y = HEIGHT - 80
    legend_text = legend_font.render("Sector Legend:", True, WHITE)
    screen.blit(legend_text, (20, legend_y))
    legend_y += 20
    
    pygame.draw.rect(screen, GREEN, (20, legend_y, 15, 15))
    screen.blit(legend_font.render("Completed", True, WHITE), (40, legend_y + 2))
    legend_y += 20
    
    pygame.draw.rect(screen, YELLOW, (20, legend_y, 15, 15))
    screen.blit(legend_font.render("Available", True, WHITE), (40, legend_y + 2))
    legend_y += 20
    
    pygame.draw.rect(screen, RED, (20, legend_y, 15, 15))
    screen.blit(legend_font.render("Locked", True, WHITE), (40, legend_y + 2))
    
    # Save file status (bottom right)
    save_status_font = pygame.font.Font(None, 18)
    if os.path.exists(SAVE_FILE):
        save_status = save_status_font.render("Save file: Found", True, GREEN)
    else:
        save_status = save_status_font.render("Save file: Not found", True, RED)
    screen.blit(save_status, (WIDTH - 120, HEIGHT - 25))

def draw_ship_selection():
    """Draw the ship selection screen"""
    screen.fill(BLACK)
    
    # Title
    title_font = pygame.font.Font(None, 48)
    title_text = title_font.render("SHIP SELECTION", True, WHITE)
    screen.blit(title_text, (WIDTH//2 - 120, 20))
    
    # Points display
    points_font = pygame.font.Font(None, 28)
    points_text = points_font.render(f"Available Points: {total_points}", True, CYAN)
    screen.blit(points_text, (WIDTH//2 - 80, 55))
    
    # Ship display
    ship_y = 90
    ship_spacing = 85
    
    for i, (name, cost, health_bonus, speed_bonus, damage_bonus) in enumerate(SHIP_DATA):
        y_pos = ship_y + i * ship_spacing
        
        # Ship preview
        ship_image = create_player(i)
        ship_rect = ship_image.get_rect(center=(80, y_pos + 30))
        screen.blit(ship_image, ship_rect)
        
        # Ship info
        info_font = pygame.font.Font(None, 22)
        
        # Ship name
        name_color = GREEN if owned_ships[i] else (YELLOW if i == selected_ship else WHITE)
        name_text = info_font.render(name, True, name_color)
        screen.blit(name_text, (130, y_pos))
        
        # Ship stats
        stats_text = f"Health: +{health_bonus}  Speed: +{speed_bonus}  Damage: +{damage_bonus}"
        stats_surface = info_font.render(stats_text, True, WHITE)
        screen.blit(stats_surface, (130, y_pos + 20))
        
        # Cost/Status
        if owned_ships[i]:
            if i == selected_ship:
                status_text = info_font.render("★ SELECTED ★", True, YELLOW)
            else:
                status_text = info_font.render(f"OWNED - Press {i+1} to select", True, GREEN)
        else:
            if total_points >= cost:
                status_text = info_font.render(f"Cost: {cost} points - Press {i+1} to buy", True, CYAN)
            else:
                status_text = info_font.render(f"Cost: {cost} points - Need {cost - total_points} more", True, RED)
        
        screen.blit(status_text, (130, y_pos + 40))
        
        # Add visual separator
        if i < len(SHIP_DATA) - 1:
            pygame.draw.line(screen, GRAY, (20, y_pos + 65), (WIDTH - 20, y_pos + 65), 1)
    
    # Instructions
    instruction_font = pygame.font.Font(None, 24)
    instruction_text = instruction_font.render("Press B to go Back to Galaxy Map", True, WHITE)
    screen.blit(instruction_text, (WIDTH//2 - 130, HEIGHT - 30))

def draw_upgrade_shop():
    """Draw the upgrade shop screen"""
    screen.fill(BLACK)
    
    # Title
    title_font = pygame.font.Font(None, 48)
    title_text = title_font.render("SHIP UPGRADES", True, WHITE)
    screen.blit(title_text, (WIDTH//2 - 120, 20))
    
    # Points display
    points_font = pygame.font.Font(None, 28)
    points_text = points_font.render(f"Available Points: {total_points}", True, CYAN)
    screen.blit(points_text, (WIDTH//2 - 80, 55))
    
    # Instructions header
    header_font = pygame.font.Font(None, 20)
    header_text = header_font.render("System Levels (Green = Owned, Gray = Available)", True, WHITE)
    screen.blit(header_text, (50, 85))
    
    # Upgrade display
    upgrade_y = 110
    upgrade_spacing = 65
    
    for i, (system, data) in enumerate(ship_upgrades.items()):
        y_pos = upgrade_y + i * upgrade_spacing
        
        # System name
        name_font = pygame.font.Font(None, 24)
        name_text = name_font.render(f"{i+1}. {data['description']}", True, WHITE)
        screen.blit(name_text, (50, y_pos))
        
        # Current level indicator
        level_font = pygame.font.Font(None, 18)
        level_text = level_font.render(f"Level {data['level']}/{data['max_level']}", True, CYAN)
        screen.blit(level_text, (50, y_pos + 20))
        
        # Level bars
        for level in range(1, data['max_level'] + 1):
            level_x = 200 + (level - 1) * 35
            color = GREEN if level <= data['level'] else GRAY
            pygame.draw.rect(screen, color, (level_x, y_pos + 5, 30, 25))
            pygame.draw.rect(screen, WHITE, (level_x, y_pos + 5, 30, 25), 2)
            
            # Level number
            level_num_text = level_font.render(str(level), True, BLACK if level <= data['level'] else WHITE)
            screen.blit(level_num_text, (level_x + 12, y_pos + 10))
        
        # Upgrade cost and button
        if data['level'] < data['max_level']:
            cost = data['cost'][data['level'] - 1]
            if total_points >= cost:
                cost_text = level_font.render(f"Upgrade: {cost} pts - Press {i+1}", True, CYAN)
            else:
                cost_text = level_font.render(f"Upgrade: {cost} pts - Need {cost - total_points} more", True, RED)
        else:
            cost_text = level_font.render("★ MAX LEVEL ★", True, YELLOW)
        
        screen.blit(cost_text, (400, y_pos + 10))
        
        # Add visual separator
        if i < len(ship_upgrades) - 1:
            pygame.draw.line(screen, GRAY, (50, y_pos + 45), (WIDTH - 50, y_pos + 45), 1)
    
    # Instructions
    instruction_font = pygame.font.Font(None, 22)
    instruction_text = instruction_font.render("Press B to go Back | Press P for Power Management", True, WHITE)
    screen.blit(instruction_text, (WIDTH//2 - 170, HEIGHT - 30))

def draw_power_management():
    """Draw the power management screen"""
    screen.fill(BLACK)
    
    # Title
    title_font = pygame.font.Font(None, 48)
    title_text = title_font.render("POWER MANAGEMENT", True, WHITE)
    screen.blit(title_text, (WIDTH//2 - 140, 20))
    
    # Total power display
    power_font = pygame.font.Font(None, 28)
    used_power = sum(power_system['allocation'].values())
    power_text = power_font.render(f"Power Usage: {used_power}/{power_system['total_power']}", True, CYAN)
    screen.blit(power_text, (WIDTH//2 - 80, 55))
    
    # Power bar (visual representation)
    power_bar_y = 85
    bar_width = 300
    bar_height = 20
    bar_x = WIDTH//2 - bar_width//2
    
    # Background bar
    pygame.draw.rect(screen, GRAY, (bar_x, power_bar_y, bar_width, bar_height))
    
    # Used power bar
    used_width = int((used_power / power_system['total_power']) * bar_width)
    color = GREEN if used_power <= power_system['total_power'] else RED
    pygame.draw.rect(screen, color, (bar_x, power_bar_y, used_width, bar_height))
    
    # Power bar border
    pygame.draw.rect(screen, WHITE, (bar_x, power_bar_y, bar_width, bar_height), 2)
    
    # Instructions header
    header_font = pygame.font.Font(None, 20)
    header_text = header_font.render("System Power Allocation (Green = Active, Gray = Available)", True, WHITE)
    screen.blit(header_text, (50, 120))
    
    # System power allocation
    system_y = 145
    system_spacing = 60
    
    system_keys = [
        ('A/Q', 'weapons', 'Weapons'),
        ('B/V', 'shields', 'Shields'),
        ('C/X', 'engines', 'Engines'),
        ('D/Z', 'oxygen', 'Life Support'),
        ('E/R', 'medical', 'Medical Bay'),
        ('F/T', 'sensors', 'Sensors')
    ]
    
    for i, (keys, system, display_name) in enumerate(system_keys):
        y_pos = system_y + i * system_spacing
        power = power_system['allocation'][system]
        max_power = power_system['max_allocation'][system]
        
        # System name and current level
        name_font = pygame.font.Font(None, 24)
        name_text = name_font.render(f"{display_name} (Level {ship_upgrades[system]['level']})", True, WHITE)
        screen.blit(name_text, (50, y_pos))
        
        # Power allocation display
        power_text = name_font.render(f"Power: {power}/{max_power}", True, CYAN)
        screen.blit(power_text, (50, y_pos + 20))
        
        # Power bars
        for bar in range(max_power):
            bar_x = 250 + bar * 45
            color = GREEN if bar < power else GRAY
            pygame.draw.rect(screen, color, (bar_x, y_pos + 5, 40, 30))
            pygame.draw.rect(screen, WHITE, (bar_x, y_pos + 5, 40, 30), 2)
            
            # Power unit number
            unit_font = pygame.font.Font(None, 20)
            unit_text = unit_font.render(str(bar + 1), True, BLACK if bar < power else WHITE)
            screen.blit(unit_text, (bar_x + 17, y_pos + 15))
        
        # Controls
        control_font = pygame.font.Font(None, 20)
        control_y = y_pos + 15
        
        # Decrease power button
        if power > 0:
            minus_text = control_font.render(f"- ({keys.split('/')[0]})", True, RED)
            screen.blit(minus_text, (500, control_y))
        
        # Increase power button
        if power < max_power and used_power < power_system['total_power']:
            plus_text = control_font.render(f"+ ({keys.split('/')[1]})", True, GREEN)
            screen.blit(plus_text, (580, control_y))
        
        # Add visual separator
        if i < len(system_keys) - 1:
            pygame.draw.line(screen, GRAY, (50, y_pos + 45), (WIDTH - 50, y_pos + 45), 1)
    
    # Instructions
    instruction_font = pygame.font.Font(None, 18)
    instruction_text = instruction_font.render("Press M to go Back | Use letter keys to adjust power (A/Q=Weapons, B/V=Shields, etc.)", True, WHITE)
    screen.blit(instruction_text, (WIDTH//2 - 350, HEIGHT - 30))

def draw_encounter():
    """Draw encounter/event screen"""
    screen.fill(BLACK)
    
    if current_event:
        # Title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("ENCOUNTER", True, WHITE)
        screen.blit(title_text, (WIDTH//2 - 100, 30))
        
        # Status display
        status_font = pygame.font.Font(None, 20)
        status_text = status_font.render(f"Points: {total_points} | Ship: {SHIP_DATA[selected_ship][0]}", True, CYAN)
        screen.blit(status_text, (WIDTH//2 - 150, 70))
        
        # Event description box
        desc_box_y = 100
        desc_box_height = 120
        pygame.draw.rect(screen, GRAY, (30, desc_box_y, WIDTH - 60, desc_box_height))
        pygame.draw.rect(screen, WHITE, (30, desc_box_y, WIDTH - 60, desc_box_height), 2)
        
        # Event description
        desc_font = pygame.font.Font(None, 22)
        y_offset = desc_box_y + 15
        for line in current_event['description']:
            line_text = desc_font.render(line, True, WHITE)
            screen.blit(line_text, (40, y_offset))
            y_offset += 25
        
        # Options section
        options_title_font = pygame.font.Font(None, 32)
        options_title = options_title_font.render("Choose your action:", True, WHITE)
        screen.blit(options_title, (50, 250))
        
        # Options
        option_font = pygame.font.Font(None, 24)
        option_y = 290
        for i, option in enumerate(current_event['options']):
            # Option box
            option_height = 50
            option_box_y = option_y + i * (option_height + 10)
            
            # Highlight based on relevance to ship systems
            box_color = GRAY
            if option['type'] == 'combat' and power_system['allocation']['weapons'] >= 3:
                box_color = (0, 64, 0)  # Dark green for good weapons
            elif option['type'] == 'escape' and power_system['allocation']['engines'] >= 2:
                box_color = (0, 0, 64)  # Dark blue for good engines
            elif option['type'] == 'explore' and power_system['allocation']['sensors'] >= 2:
                box_color = (64, 64, 0)  # Dark yellow for good sensors
            
            pygame.draw.rect(screen, box_color, (50, option_box_y, WIDTH - 100, option_height))
            pygame.draw.rect(screen, WHITE, (50, option_box_y, WIDTH - 100, option_height), 2)
            
            # Option text
            option_text = option_font.render(f"{i+1}. {option['text']}", True, WHITE)
            screen.blit(option_text, (60, option_box_y + 5))
            
            # Reward/risk info
            risk_font = pygame.font.Font(None, 18)
            reward_text = f"Reward: {option['reward']} pts"
            if option['risk'] != 'none':
                risk_text = f"Risk: {option['risk'].replace('_', ' ').title()}"
                combined_text = f"{reward_text} | {risk_text}"
            else:
                combined_text = reward_text
            
            risk_surface = risk_font.render(combined_text, True, YELLOW)
            screen.blit(risk_surface, (60, option_box_y + 25))
    
    # Instructions
    instruction_font = pygame.font.Font(None, 24)
    instruction_text = instruction_font.render("Press 1-3 to choose your action", True, WHITE)
    screen.blit(instruction_text, (WIDTH//2 - 120, HEIGHT - 30))

def get_level_enemy_types():
    if current_level == 1:
        return ['basic']
    elif current_level == 2:
        return ['basic', 'fast']
    elif current_level == 3:
        return ['basic', 'fast', 'tank']
    else:
        return ['basic', 'fast', 'tank']

def spawn_enemy():
    if len(enemies) < MAX_ENEMIES and not boss_active:
        enemy_types = get_level_enemy_types()
        enemy_type = random.choice(enemy_types)
        enemy = Enemy(enemy_type)
        all_sprites.add(enemy)
        enemies.add(enemy)

def spawn_asteroid():
    if len(asteroids) < MAX_ASTEROIDS and not boss_active:
        asteroid = Asteroid()
        all_sprites.add(asteroid)
        asteroids.add(asteroid)

def spawn_powerup(x, y):
    if random.random() < 0.3:  # 30% chance to drop power-up
        powerup = PowerUp(x, y)
        all_sprites.add(powerup)
        powerups.add(powerup)

def spawn_boss():
    global boss_active, boss_health
    boss = Boss()
    all_sprites.add(boss)
    bosses.add(boss)
    boss_active = True
    boss_health = boss.health
    try:
        boss_music.play(-1)
    except:
        pass

def check_level_progression():
    global current_level, level_complete, show_level_text, level_text_timer, boss_active, boss_defeated, sector_completed, game_state
    
    # Restore power gradually over time
    if power_system['total_power'] < 8 and random.random() < 0.001:  # 0.1% chance per frame
        power_system['total_power'] = min(8, power_system['total_power'] + 1)
    
    # Check if it's time for boss fight (only once per sector)
    if player.score >= current_level * 200 and not boss_active and not boss_defeated and not sector_completed and len(bosses) == 0:
        spawn_boss()
    
    # Check if boss is defeated
    if boss_active and len(bosses) == 0 and not boss_defeated:
        boss_defeated = True
        boss_active = False
        sector_completed = True
        level_complete = True
        show_level_text = True
        level_text_timer = pygame.time.get_ticks()
        
        # Clear all remaining enemies and enemy bullets when sector is completed
        enemies.empty()
        enemy_bullets.empty()
        
        if current_level >= max_level:
            # Game completed - all sectors finished
            return True
    
    return False

while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game_state == "menu":
                # Ship selection
                if event.key == pygame.K_s:
                    game_state = "ship_select"
                # Upgrade shop
                elif event.key == pygame.K_u:
                    game_state = "upgrade_shop"
                # Power management
                elif event.key == pygame.K_p:
                    game_state = "power_management"
                # Reset progress
                elif event.key == pygame.K_r:
                    reset_save()
                # Allow playing only the current available sector
                elif event.key == pygame.K_1 and current_level == 1:
                    game_state = "playing"
                elif event.key == pygame.K_2 and current_level == 2:
                    game_state = "playing"
                elif event.key == pygame.K_3 and current_level == 3:
                    game_state = "playing"
                elif event.key == pygame.K_4 and current_level == 4:
                    game_state = "playing"
                elif event.key == pygame.K_5 and current_level == 5:
                    game_state = "playing"
                
                # Start the sector if valid key pressed
                if game_state == "playing":
                    game_over = False
                    level_complete = False
                    show_level_text = False
                    boss_active = False
                    boss_health = 0
                    boss_defeated = False
                    sector_completed = False
                    encounter_active = False
                    current_event = None
                    pause_game = False
                    player.reset_for_new_game()
                    
                    # Clear all sprites except player
                    enemies.empty()
                    asteroids.empty()
                    bullets.empty()
                    enemy_bullets.empty()
                    powerups.empty()
                    bosses.empty()
                    all_sprites.empty()
                    all_sprites.add(player)
                    
            elif game_state == "ship_select":
                # Back to menu
                if event.key == pygame.K_b:
                    game_state = "menu"
                # Ship selection/purchase
                elif event.key == pygame.K_1:
                    if owned_ships[0]:
                        selected_ship = 0
                elif event.key == pygame.K_2:
                    if owned_ships[1]:
                        selected_ship = 1
                        save_game()  # Save when ship is selected
                    elif total_points >= SHIP_DATA[1][1]:
                        total_points -= SHIP_DATA[1][1]
                        owned_ships[1] = True
                        selected_ship = 1
                        save_game()  # Save when ship is purchased
                elif event.key == pygame.K_3:
                    if owned_ships[2]:
                        selected_ship = 2
                        save_game()
                    elif total_points >= SHIP_DATA[2][1]:
                        total_points -= SHIP_DATA[2][1]
                        owned_ships[2] = True
                        selected_ship = 2
                        save_game()
                elif event.key == pygame.K_4:
                    if owned_ships[3]:
                        selected_ship = 3
                        save_game()
                    elif total_points >= SHIP_DATA[3][1]:
                        total_points -= SHIP_DATA[3][1]
                        owned_ships[3] = True
                        selected_ship = 3
                        save_game()
                elif event.key == pygame.K_5:
                    if owned_ships[4]:
                        selected_ship = 4
                        save_game()
                    elif total_points >= SHIP_DATA[4][1]:
                        total_points -= SHIP_DATA[4][1]
                        owned_ships[4] = True
                        selected_ship = 4
                        save_game()
                        
            elif game_state == "upgrade_shop":
                # Back to menu
                if event.key == pygame.K_b:
                    game_state = "menu"
                elif event.key == pygame.K_p:
                    game_state = "power_management"
                # Upgrade systems
                elif event.key == pygame.K_1:
                    system = 'weapons'
                    if ship_upgrades[system]['level'] < ship_upgrades[system]['max_level']:
                        cost = ship_upgrades[system]['cost'][ship_upgrades[system]['level'] - 1]
                        if total_points >= cost:
                            total_points -= cost
                            ship_upgrades[system]['level'] += 1
                            power_system['max_allocation'][system] = ship_upgrades[system]['level']
                            save_game()  # Save when upgrade is purchased
                elif event.key == pygame.K_2:
                    system = 'shields'
                    if ship_upgrades[system]['level'] < ship_upgrades[system]['max_level']:
                        cost = ship_upgrades[system]['cost'][ship_upgrades[system]['level'] - 1]
                        if total_points >= cost:
                            total_points -= cost
                            ship_upgrades[system]['level'] += 1
                            power_system['max_allocation'][system] = ship_upgrades[system]['level']
                            save_game()  # Save when upgrade is purchased
                elif event.key == pygame.K_3:
                    system = 'engines'
                    if ship_upgrades[system]['level'] < ship_upgrades[system]['max_level']:
                        cost = ship_upgrades[system]['cost'][ship_upgrades[system]['level'] - 1]
                        if total_points >= cost:
                            total_points -= cost
                            ship_upgrades[system]['level'] += 1
                            power_system['max_allocation'][system] = ship_upgrades[system]['level']
                            save_game()
                elif event.key == pygame.K_4:
                    system = 'oxygen'
                    if ship_upgrades[system]['level'] < ship_upgrades[system]['max_level']:
                        cost = ship_upgrades[system]['cost'][ship_upgrades[system]['level'] - 1]
                        if total_points >= cost:
                            total_points -= cost
                            ship_upgrades[system]['level'] += 1
                            power_system['max_allocation'][system] = ship_upgrades[system]['level']
                            save_game()
                elif event.key == pygame.K_5:
                    system = 'medical'
                    if ship_upgrades[system]['level'] < ship_upgrades[system]['max_level']:
                        cost = ship_upgrades[system]['cost'][ship_upgrades[system]['level'] - 1]
                        if total_points >= cost:
                            total_points -= cost
                            ship_upgrades[system]['level'] += 1
                            power_system['max_allocation'][system] = ship_upgrades[system]['level']
                            save_game()
                elif event.key == pygame.K_6:
                    system = 'sensors'
                    if ship_upgrades[system]['level'] < ship_upgrades[system]['max_level']:
                        cost = ship_upgrades[system]['cost'][ship_upgrades[system]['level'] - 1]
                        if total_points >= cost:
                            total_points -= cost
                            ship_upgrades[system]['level'] += 1
                            power_system['max_allocation'][system] = ship_upgrades[system]['level']
                            save_game()
                        
            elif game_state == "power_management":
                # Back to previous screen
                if event.key == pygame.K_m:
                    game_state = "upgrade_shop"
                # Power allocation controls - Capital letters for decrease, lowercase for increase
                elif event.key == pygame.K_a:  # Weapons -
                    if power_system['allocation']['weapons'] > 0:
                        power_system['allocation']['weapons'] -= 1
                        save_game()  # Save power allocation changes
                elif event.key == pygame.K_q:  # Weapons +
                    if (power_system['allocation']['weapons'] < power_system['max_allocation']['weapons'] and 
                        sum(power_system['allocation'].values()) < power_system['total_power']):
                        power_system['allocation']['weapons'] += 1
                        save_game()  # Save power allocation changes
                elif event.key == pygame.K_b:  # Shields -
                    if power_system['allocation']['shields'] > 0:
                        power_system['allocation']['shields'] -= 1
                        save_game()
                elif event.key == pygame.K_v:  # Shields +
                    if (power_system['allocation']['shields'] < power_system['max_allocation']['shields'] and 
                        sum(power_system['allocation'].values()) < power_system['total_power']):
                        power_system['allocation']['shields'] += 1
                        save_game()
                elif event.key == pygame.K_c:  # Engines -
                    if power_system['allocation']['engines'] > 0:
                        power_system['allocation']['engines'] -= 1
                        save_game()
                elif event.key == pygame.K_x:  # Engines +
                    if (power_system['allocation']['engines'] < power_system['max_allocation']['engines'] and 
                        sum(power_system['allocation'].values()) < power_system['total_power']):
                        power_system['allocation']['engines'] += 1
                        save_game()
                elif event.key == pygame.K_d:  # Oxygen -
                    if power_system['allocation']['oxygen'] > 0:
                        power_system['allocation']['oxygen'] -= 1
                        save_game()
                elif event.key == pygame.K_z:  # Oxygen +
                    if (power_system['allocation']['oxygen'] < power_system['max_allocation']['oxygen'] and 
                        sum(power_system['allocation'].values()) < power_system['total_power']):
                        power_system['allocation']['oxygen'] += 1
                        save_game()
                elif event.key == pygame.K_e:  # Medical -
                    if power_system['allocation']['medical'] > 0:
                        power_system['allocation']['medical'] -= 1
                        save_game()
                elif event.key == pygame.K_r:  # Medical +
                    if (power_system['allocation']['medical'] < power_system['max_allocation']['medical'] and 
                        sum(power_system['allocation'].values()) < power_system['total_power']):
                        power_system['allocation']['medical'] += 1
                        save_game()
                elif event.key == pygame.K_f:  # Sensors -
                    if power_system['allocation']['sensors'] > 0:
                        power_system['allocation']['sensors'] -= 1
                        save_game()
                elif event.key == pygame.K_t:  # Sensors +
                    if (power_system['allocation']['sensors'] < power_system['max_allocation']['sensors'] and 
                        sum(power_system['allocation'].values()) < power_system['total_power']):
                        power_system['allocation']['sensors'] += 1
                        save_game()
                        
            elif game_state == "encounter":
                # Handle encounter choices
                if event.key == pygame.K_1:
                    resolve_encounter(0)
                elif event.key == pygame.K_2:
                    resolve_encounter(1)
                elif event.key == pygame.K_3:
                    resolve_encounter(2)
                    
            elif game_state == "playing":
                # Pause game only for major events
                if event.key == pygame.K_SPACE:
                    pause_game = not pause_game
                # Power management during gameplay
                elif event.key == pygame.K_p:
                    game_state = "power_management"
                # Manual encounter trigger for testing
                elif event.key == pygame.K_e:
                    if not encounter_active:
                        current_event = generate_encounter()
                        encounter_active = True
                        game_state = "encounter"
                        
            if game_over and event.key == pygame.K_r:
                # Add points based on performance before reset
                total_points += player.score // 10  # 1 point per 10 score
                save_game()  # Save points gained
                
                # Reset to menu
                game_state = "menu"
                game_over = False
                level_complete = False
                show_level_text = False
                boss_active = False
                boss_health = 0
                boss_defeated = False
                sector_completed = False
                player.reset_for_new_game()
                
                # Clear all sprites except player
                enemies.empty()
                asteroids.empty()
                bullets.empty()
                enemy_bullets.empty()
                powerups.empty()
                bosses.empty()
                all_sprites.empty()
                all_sprites.add(player)

    if game_state == "menu":
        draw_galaxy_map()
        
    elif game_state == "ship_select":
        draw_ship_selection()
        
    elif game_state == "upgrade_shop":
        draw_upgrade_shop()
        
    elif game_state == "power_management":
        draw_power_management()
        
    elif game_state == "encounter":
        draw_encounter()
        
    elif game_state == "playing" and not game_over:
        # Random encounter chance - Much less frequent, more meaningful
        if not encounter_active and random.random() < 0.0001:  # 0.01% chance per frame (100x less frequent)
            current_event = generate_encounter()
            encounter_active = True
            game_state = "encounter"
        
        # Only update if not paused
        if not pause_game:
            # Check level progression
            if check_level_progression():
                # Game completed
                game_over = True
            
            # Hide level text after 3 seconds and return to menu
            if show_level_text and pygame.time.get_ticks() - level_text_timer > 3000:
                show_level_text = False
                level_complete = False
                if sector_completed:
                    # Award points for completing sector
                    sector_bonus = current_level * 100  # Bonus points for completing sector
                    total_points += player.score // 10 + sector_bonus
                    save_game()  # Save sector completion rewards
                    
                    # Sector completed, advance to next sector and return to menu
                    current_level += 1
                    sector_completed = False
                    boss_defeated = False
                    game_state = "menu"
                    save_game()  # Save level progression
                    try:
                        pygame.mixer.music.unpause()
                    except:
                        pass
                else:
                    boss_defeated = False  # Reset for next level after showing level text
                    try:
                        pygame.mixer.music.unpause()
                    except:
                        pass

            # Reduced spawn rates for less cluttered gameplay
            if not boss_active and not sector_completed:
                spawn_rate = 0.005 + (current_level - 1) * 0.002  # Much reduced spawn rate
                if random.random() < spawn_rate:
                    spawn_enemy()
                if random.random() < 0.003:  # Reduced asteroid spawn
                    spawn_asteroid()

            # Update
            all_sprites.update()

            # Enhanced collision detection with power system effects
            if not sector_completed:
                hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
                for enemy in hits:
                    # Weapon power affects damage
                    damage = 1 + player.damage_bonus + power_system['allocation']['weapons']
                    enemy.health -= damage
                    if enemy.health <= 0:
                        player.score += enemy.score_value
                        spawn_powerup(enemy.rect.centerx, enemy.rect.centery)
                        try:
                            explosion_sound.play()
                        except:
                            pass
                        enemy.kill()
                        if random.random() < 0.3:  # 30% chance to spawn replacement
                            spawn_enemy()

            # Boss collision with power effects
            boss_hits = pygame.sprite.groupcollide(bosses, bullets, False, True)
            for boss in boss_hits:
                damage = 1 + player.damage_bonus + power_system['allocation']['weapons']
                boss.health -= damage
                if boss.health <= 0:
                    player.score += 100
                    try:
                        explosion_sound.play()
                    except:
                        pass
                    boss.kill()
                    boss_active = False
                    boss_defeated = True
                    sector_completed = True
                    level_complete = True
                    show_level_text = True
                    level_text_timer = pygame.time.get_ticks()
                    
                    # Clear all remaining enemies and enemy bullets when sector is completed
                    enemies.empty()
                    enemy_bullets.empty()
                    
                    try:
                        pygame.mixer.music.unpause()
                    except:
                        pass

            # Player collision with shield effects
            if not sector_completed:
                # Shield power reduces damage
                shield_effectiveness = power_system['allocation']['shields']
                
                enemy_collisions = pygame.sprite.spritecollide(player, enemies, True)
                for enemy in enemy_collisions:
                    damage = max(1, 10 - shield_effectiveness * 2)
                    if player.take_damage(damage):
                        try:
                            explosion_sound.play()
                        except:
                            pass
                    if random.random() < 0.3:
                        spawn_enemy()

                asteroid_collisions = pygame.sprite.spritecollide(player, asteroids, True)
                for asteroid in asteroid_collisions:
                    damage = max(1, 15 - shield_effectiveness * 3)
                    if player.take_damage(damage):
                        try:
                            explosion_sound.play()
                        except:
                            pass

            # Boss collisions
            boss_collisions = pygame.sprite.spritecollide(player, bosses, False)
            for boss in boss_collisions:
                damage = max(1, 20 - power_system['allocation']['shields'] * 4)
                if player.take_damage(damage):
                    try:
                        explosion_sound.play()
                    except:
                        pass

            # Enemy bullet collisions
            if not sector_completed:
                bullet_hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
                for bullet in bullet_hits:
                    damage = max(1, 5 - power_system['allocation']['shields'])
                    if player.take_damage(damage):
                        try:
                            explosion_sound.play()
                        except:
                            pass

            # Power-up collisions
            powerup_hits = pygame.sprite.spritecollide(player, powerups, True)
            for powerup in powerup_hits:
                player.apply_power_up(powerup.power_type)
                try:
                    powerup_sound.play()
                except:
                    pass

            # Check if player is dead
            if player.health <= 0 and not sector_completed:
                game_over = True

    # Drawing
    if game_state == "playing":
        screen.fill(BLACK)
        
        # Draw starfield background
        draw_starfield(starfield)
        
        all_sprites.draw(screen)

        # Draw UI
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)
        
        # Health bar
        health_bar_width = 200
        health_bar_height = 20
        health_ratio = player.health / player.max_health
        pygame.draw.rect(screen, RED, (10, 10, health_bar_width, health_bar_height))
        pygame.draw.rect(screen, GREEN, (10, 10, health_bar_width * health_ratio, health_bar_height))
        pygame.draw.rect(screen, WHITE, (10, 10, health_bar_width, health_bar_height), 2)
        
        # Score and level
        score_text = font.render(f"Score: {player.score}", True, WHITE)
        level_text = font.render(f"Level: {current_level}", True, WHITE)
        screen.blit(score_text, (10, 35))
        screen.blit(level_text, (10, 65))
        
        # System status
        system_font = pygame.font.Font(None, 20)
        system_y = 90
        screen.blit(system_font.render(f"Weapons: {power_system['allocation']['weapons']}/{power_system['max_allocation']['weapons']}", True, CYAN), (10, system_y))
        screen.blit(system_font.render(f"Shields: {power_system['allocation']['shields']}/{power_system['max_allocation']['shields']}", True, CYAN), (10, system_y + 20))
        screen.blit(system_font.render(f"Engines: {power_system['allocation']['engines']}/{power_system['max_allocation']['engines']}", True, CYAN), (10, system_y + 40))
        
        # Crew status
        crew_y = 170
        screen.blit(system_font.render("Crew Status:", True, WHITE), (10, crew_y))
        for i, crew in enumerate(crew_members):
            health_color = GREEN if crew['health'] > 70 else (YELLOW if crew['health'] > 30 else RED)
            crew_text = f"{crew['name']}: {crew['health']}%"
            screen.blit(system_font.render(crew_text, True, health_color), (10, crew_y + 20 + i * 20))
        
        # Pause indicator
        if pause_game:
            pause_font = pygame.font.Font(None, 48)
            pause_text = pause_font.render("PAUSED - Press SPACE to resume", True, YELLOW)
            screen.blit(pause_text, (WIDTH//2 - 200, HEIGHT//2 - 100))
            
        # Controls help
        help_font = pygame.font.Font(None, 18)
        screen.blit(help_font.render("SPACE: Pause/Resume  Left Ctrl: Fire  P: Power Management  E: Manual Encounter", True, WHITE), (WIDTH - 420, HEIGHT - 40))
        
        # Active power-ups
        y_offset = 95
        for power_type in player.power_up_timers:
            remaining = POWERUP_DURATION - (pygame.time.get_ticks() - player.power_up_timers[power_type])
            if remaining > 0:
                power_text = small_font.render(f"{power_type.replace('_', ' ').title()}: {remaining//1000}s", True, YELLOW)
                screen.blit(power_text, (10, y_offset))
                y_offset += 20
        
        # Boss health bar
        if boss_active and len(bosses) > 0:
            boss = bosses.sprites()[0]
            boss_health_ratio = boss.health / boss.max_health
            boss_bar_width = 400
            boss_bar_height = 30
            boss_bar_x = (WIDTH - boss_bar_width) // 2
            boss_bar_y = 50
            
            pygame.draw.rect(screen, RED, (boss_bar_x, boss_bar_y, boss_bar_width, boss_bar_height))
            pygame.draw.rect(screen, YELLOW, (boss_bar_x, boss_bar_y, boss_bar_width * boss_health_ratio, boss_bar_height))
            pygame.draw.rect(screen, WHITE, (boss_bar_x, boss_bar_y, boss_bar_width, boss_bar_height), 3)
            
            boss_text = font.render("BOSS", True, WHITE)
            screen.blit(boss_text, (boss_bar_x + boss_bar_width//2 - 30, boss_bar_y + 5))
        
        # Level transition text
        if show_level_text:
            if sector_completed:
                sector_text = font.render("You have completed this sector!", True, GREEN)
                screen.blit(sector_text, (WIDTH//2 - 160, HEIGHT//2 - 50))
                return_text = font.render("Returning to Galaxy Map...", True, YELLOW)
                screen.blit(return_text, (WIDTH//2 - 130, HEIGHT//2 - 10))
            elif current_level <= max_level:
                level_up_text = font.render(f"LEVEL {current_level}!", True, YELLOW)
                screen.blit(level_up_text, (WIDTH//2 - 80, HEIGHT//2 - 50))
            else:
                victory_text = font.render("VICTORY! You completed all sectors!", True, GREEN)
                screen.blit(victory_text, (WIDTH//2 - 200, HEIGHT//2 - 50))
        
        # Shield indicator
        if player.shield:
            shield_surf = pygame.Surface((player.rect.width + 20, player.rect.height + 20), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, CYAN, (shield_surf.get_width()//2, shield_surf.get_height()//2), 
                              shield_surf.get_width()//2, 3)
            screen.blit(shield_surf, (player.rect.x - 10, player.rect.y - 10))

        if game_over:
            game_over_text = font.render("GAME OVER - Press R to return to menu", True, RED)
            screen.blit(game_over_text, (WIDTH//2 - 250, HEIGHT//2))
            
            if current_level > max_level:
                final_text = font.render("Congratulations! You completed all sectors!", True, GREEN)
                screen.blit(final_text, (WIDTH//2 - 200, HEIGHT//2 + 50))

    pygame.display.flip()

pygame.quit()