import pygame
import random
import math
import json
from enum import Enum
from collections import deque

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Game constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
FPS = 60
GALAXY_SIZE = 50  # Reduced for performance

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Game states
class GameState(Enum):
    MENU = 0
    GALAXY_MAP = 1
    SECTOR = 2
    COMBAT = 3
    UPGRADES = 4
    GAME_OVER = 5

# Ship types
class ShipType(Enum):
    FIGHTER = "Fighter"
    CRUISER = "Cruiser"

# Enemy types
class EnemyType(Enum):
    PIRATE = "Pirate"
    DRONE = "Drone"

# Sector types
class SectorType(Enum):
    NEBULA = "Nebula"
    ASTEROID = "Asteroid Field"
    PLANET = "Planet"
    EMPTY = "Empty Space"

# Player ship class
class PlayerShip:
    def __init__(self, ship_type):
        self.type = ship_type
        self.max_health = 100
        self.health = 100
        self.speed = 3
        self.rotation = 0
        self.position = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        self.weapons = {"laser": {"damage": 10, "cooldown": 0.5, "last_shot": 0}}
        self.active_weapon = "laser"
        self.upgrades = {"engine": 1, "weapons": 1, "shields": 1}
        self.inventory = {"fuel": 100, "minerals": 50, "credits": 200}

    def take_damage(self, amount):
        self.health -= amount
        return amount

# Enemy class
class Enemy:
    def __init__(self, enemy_type, x, y):
        self.type = enemy_type
        self.health = 30 if enemy_type == EnemyType.PIRATE else 20
        self.x = x
        self.y = y
        self.speed = 2 if enemy_type == EnemyType.DRONE else 1

    def draw(self, screen):
        color = RED if self.type == EnemyType.PIRATE else YELLOW
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 15)

# Main game class
class SpaceExplorerGame:
    def __init__(self):
        print("Initializing game...")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Explorer")
        self.clock = pygame.time.Clock()
        self.state = GameState.MENU
        self.running = True
        self.player = None
        self.galaxy = []
        self.current_sector = (0, 0)
        self.message_log = deque(maxlen=5)
        print("Game initialized successfully")

    def generate_galaxy(self):
        print("Generating galaxy...")
        random.seed(42)  # Fixed seed for reproducibility
        self.galaxy = []
        for y in range(GALAXY_SIZE):
            row = []
            for x in range(GALAXY_SIZE):
                # Simple random generation (no Perlin noise)
                val = random.random()
                if val < 0.2:
                    sector_type = SectorType.NEBULA
                elif val < 0.4:
                    sector_type = SectorType.ASTEROID
                elif val < 0.7:
                    sector_type = SectorType.EMPTY
                else:
                    sector_type = SectorType.PLANET

                enemies = []
                if random.random() > 0.7:
                    enemies.append({"type": random.choice(list(EnemyType))})
                
                row.append({
                    "type": sector_type,
                    "explored": False,
                    "enemies": enemies,
                    "resources": {"fuel": random.randint(10, 50)}
                })
            self.galaxy.append(row)
        print("Galaxy generated")

    def new_game(self, ship_type):
        print(f"Starting new game as {ship_type}")
        self.player = PlayerShip(ship_type)
        self.generate_galaxy()
        self.current_sector = (GALAXY_SIZE//2, GALAXY_SIZE//2)
        self.state = GameState.GALAXY_MAP
        self.add_message("New game started!")

    def add_message(self, text):
        self.message_log.append(text)

    def draw_galaxy_map(self):
        self.screen.fill(BLACK)
        cell_size = min(20, 800 // GALAXY_SIZE)
        start_x = (SCREEN_WIDTH - GALAXY_SIZE * cell_size) // 2
        start_y = (SCREEN_HEIGHT - GALAXY_SIZE * cell_size) // 2

        for y in range(GALAXY_SIZE):
            for x in range(GALAXY_SIZE):
                rect = pygame.Rect(start_x + x * cell_size, start_y + y * cell_size, cell_size, cell_size)
                color = {
                    SectorType.NEBULA: PURPLE,
                    SectorType.ASTEROID: (150, 150, 150),
                    SectorType.PLANET: BLUE,
                    SectorType.EMPTY: (50, 50, 50)
                }[self.galaxy[y][x]["type"]]
                
                pygame.draw.rect(self.screen, color, rect)
                if (x, y) == self.current_sector:
                    pygame.draw.rect(self.screen, GREEN, rect, 3)

    def draw_menu(self):
        self.screen.fill(BLACK)
        font = pygame.font.SysFont("Arial", 36)
        title = font.render("SPACE EXPLORER", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))

        options = ["1. New Game (Fighter)", "2. New Game (Cruiser)", "3. Exit"]
        for i, opt in enumerate(options):
            text = font.render(opt, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 200 + i * 50))

    def run(self):
        print("Entering main game loop")
        while self.running:
            current_time = pygame.time.get_ticks() / 1000
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            # Rendering
            if self.state == GameState.MENU:
                self.draw_menu()
            elif self.state == GameState.GALAXY_MAP:
                self.draw_galaxy_map()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        print("Game exited cleanly")

if __name__ == "__main__":
    print("Launching Space Explorer...")
    game = SpaceExplorerGame()
    game.run()