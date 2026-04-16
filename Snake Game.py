import pygame
import time
import random
import math

# Initialize pygame
pygame.init()

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Set display dimensions
DIS_WIDTH = 800
DIS_HEIGHT = 600

# Initialize game display
dis = pygame.display.set_mode((DIS_WIDTH, DIS_HEIGHT))
pygame.display.set_caption('Smooth Snake Game')

# Initialize game clock - THIS FIXES THE ERROR
clock = pygame.time.Clock()

# Game parameters
SNAKE_BLOCK = 20
BASE_SPEED = 10
MAX_SPEED = 20
current_speed = BASE_SPEED
speed_boost_active = False
boost_end_time = 0

def your_score(score):
    font = pygame.font.SysFont("comicsansms", 35)
    value = font.render(f"Score: {score}", True, BLACK)
    dis.blit(value, [10, 10])
    if speed_boost_active:
        boost_font = pygame.font.SysFont("bahnschrift", 25)
        boost_text = boost_font.render("SPEED BOOST!", True, YELLOW)
        dis.blit(boost_text, [DIS_WIDTH - 150, 10])

def draw_snake(snake_list):
    for i, segment in enumerate(snake_list):
        if i == len(snake_list) - 1:  # Head
            pygame.draw.rect(dis, GREEN, [segment[0], segment[1], SNAKE_BLOCK, SNAKE_BLOCK], border_radius=5)
        else:  # Body
            pygame.draw.rect(dis, (0, 200, 0), [segment[0], segment[1], SNAKE_BLOCK, SNAKE_BLOCK])

def message(msg, color):
    font = pygame.font.SysFont("bahnschrift", 25)
    mesg = font.render(msg, True, color)
    dis.blit(mesg, [DIS_WIDTH/3, DIS_HEIGHT/3])

def gameLoop():
    global current_speed, speed_boost_active, boost_end_time
    
    game_over = False
    game_close = False

    # Snake starting position
    x1 = DIS_WIDTH // 2
    y1 = DIS_HEIGHT // 2
    x1 = (x1 // SNAKE_BLOCK) * SNAKE_BLOCK
    y1 = (y1 // SNAKE_BLOCK) * SNAKE_BLOCK
    
    # Movement variables
    x1_change = 0
    y1_change = 0
    moving = False

    snake_List = []
    Length_of_snake = 1
    current_speed = BASE_SPEED
    speed_boost_active = False

    # Food position
    foodx = round(random.randrange(0, DIS_WIDTH - SNAKE_BLOCK) / SNAKE_BLOCK) * SNAKE_BLOCK
    foody = round(random.randrange(0, DIS_HEIGHT - SNAKE_BLOCK) / SNAKE_BLOCK) * SNAKE_BLOCK
    boost_foodx = -1
    boost_foody = -1
    boost_active = False

    # Timing variables
    last_update = 0
    move_interval = 1000 // BASE_SPEED  # milliseconds per move

    while not game_over:
        current_time = pygame.time.get_ticks()

        # Handle game over screen
        while game_close:
            dis.fill(WHITE)
            message("Game Over! Press Q-Quit or C-Play Again", RED)
            your_score(Length_of_snake - 1)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x1_change <= 0:
                    x1_change = -SNAKE_BLOCK
                    y1_change = 0
                    moving = True
                elif event.key == pygame.K_RIGHT and x1_change >= 0:
                    x1_change = SNAKE_BLOCK
                    y1_change = 0
                    moving = True
                elif event.key == pygame.K_UP and y1_change <= 0:
                    y1_change = -SNAKE_BLOCK
                    x1_change = 0
                    moving = True
                elif event.key == pygame.K_DOWN and y1_change >= 0:
                    y1_change = SNAKE_BLOCK
                    x1_change = 0
                    moving = True

        # Movement logic
        if moving and current_time - last_update > move_interval:
            last_update = current_time
            
            # Update position
            x1 += x1_change
            y1 += y1_change
            
            # Check collisions
            if x1 >= DIS_WIDTH or x1 < 0 or y1 >= DIS_HEIGHT or y1 < 0:
                game_close = True
            
            snake_Head = [x1, y1]
            snake_List.append(snake_Head)
            
            if len(snake_List) > Length_of_snake:
                del snake_List[0]
            
            for segment in snake_List[:-1]:
                if segment == snake_Head:
                    game_close = True
            
            # Food collision
            if x1 == foodx and y1 == foody:
                Length_of_snake += 1
                foodx = round(random.randrange(0, DIS_WIDTH - SNAKE_BLOCK) / SNAKE_BLOCK) * SNAKE_BLOCK
                foody = round(random.randrange(0, DIS_HEIGHT - SNAKE_BLOCK) / SNAKE_BLOCK) * SNAKE_BLOCK
                
                if random.random() < 0.3 and not boost_active:
                    boost_foodx = round(random.randrange(0, DIS_WIDTH - SNAKE_BLOCK) / SNAKE_BLOCK) * SNAKE_BLOCK
                    boost_foody = round(random.randrange(0, DIS_HEIGHT - SNAKE_BLOCK) / SNAKE_BLOCK) * SNAKE_BLOCK
                    boost_active = True
            
            # Boost food collision
            if boost_active and x1 == boost_foodx and y1 == boost_foody:
                current_speed = MAX_SPEED
                speed_boost_active = True
                boost_end_time = current_time + 5000
                boost_active = False
                move_interval = 1000 // current_speed
            
            if speed_boost_active and current_time > boost_end_time:
                current_speed = BASE_SPEED
                speed_boost_active = False
                move_interval = 1000 // current_speed

        # Drawing
        dis.fill(WHITE)
        pygame.draw.rect(dis, RED, [foodx, foody, SNAKE_BLOCK, SNAKE_BLOCK], border_radius=5)
        
        if boost_active:
            pygame.draw.rect(dis, YELLOW, [boost_foodx, boost_foody, SNAKE_BLOCK, SNAKE_BLOCK], border_radius=5)
        
        draw_snake(snake_List)
        your_score(Length_of_snake - 1)
        pygame.display.update()

        # This uses the now properly defined clock
        clock.tick(60)

    pygame.quit()
    quit()

gameLoop()