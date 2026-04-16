import pygame
import random
import sys
from pygame.locals import *

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
CARD_WIDTH = 71
CARD_HEIGHT = 96
MARGIN = 20
TOP_MARGIN = 50
STOCK_POSITION = (MARGIN, TOP_MARGIN)
TABLEAU_START_X = MARGIN
TABLEAU_START_Y = TOP_MARGIN + CARD_HEIGHT + 20

# Color Constants
RED = (255, 0, 0)
CARD_BACK_COLOR = (0, 100, 0)
BACKGROUND_COLOR = (0, 128, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (70, 70, 70)
BUTTON_HOVER = (100, 100, 100)

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Spider Solitaire')

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.face_up = False
        self.rect = pygame.Rect(0, 0, CARD_WIDTH, CARD_HEIGHT)
        self.drag_pos = None
        
    def draw(self, x, y):
        self.rect.topleft = (x, y)
        if self.face_up:
            pygame.draw.rect(screen, WHITE, self.rect)
            pygame.draw.rect(screen, BLACK, self.rect, 2)
            color = RED if self.suit in ['hearts', 'diamonds'] else BLACK
            font = pygame.font.SysFont('arial', 20)
            rank_text = font.render(self.get_rank_symbol(), True, color)
            suit_text = font.render(self.get_suit_symbol(), True, color)
            screen.blit(rank_text, (x + 5, y + 5))
            screen.blit(suit_text, (x + 5, y + 25))
        else:
            pygame.draw.rect(screen, CARD_BACK_COLOR, self.rect)
            pygame.draw.rect(screen, BLACK, self.rect, 2)
            pygame.draw.rect(screen, (0, 80, 0), self.rect.inflate(-10, -10), 2)
    
    def get_rank_symbol(self):
        if self.rank == 1: return 'A'
        elif self.rank == 11: return 'J'
        elif self.rank == 12: return 'Q'
        elif self.rank == 13: return 'K'
        else: return str(self.rank)
    
    def get_suit_symbol(self):
        return {'hearts': '♥', 'diamonds': '♦', 'spades': '♠', 'clubs': '♣'}[self.suit]

class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hover = False
    
    def draw(self):
        color = BUTTON_HOVER if self.hover else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        font = pygame.font.SysFont('arial', 24)
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def check_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)
        return self.hover
    
    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1 and self.hover:
            if self.action:
                return self.action()
        return None

class SpiderSolitaire:
    def __init__(self):
        self.mode = None  # Will be 'single' or 'multi'
        self.buttons = [
            Button(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 60, 300, 50, "Single Suit (Easy)", self.set_single_suit),
            Button(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 10, 300, 50, "Four Suits (Hard)", self.set_multi_suit)
        ]
        self.reset_game()
    
    def set_single_suit(self):
        self.mode = 'single'
        self.reset_game()
        return True
    
    def set_multi_suit(self):
        self.mode = 'multi'
        self.reset_game()
        return True
    
    def reset_game(self):
        if not self.mode:
            return  # Don't reset until mode is selected
        
        # Create deck based on selected mode
        if self.mode == 'single':
            SUITS = ['spades'] * 8  # 8 decks of just spades
        else:
            SUITS = ['hearts', 'diamonds', 'spades', 'clubs'] * 2  # 2 of each suit
        
        RANKS = list(range(1, 14))
        self.deck = [Card(suit, rank) for suit in SUITS for rank in RANKS]
        random.shuffle(self.deck)
        
        # Set up tableau
        self.tableau = [[] for _ in range(10)]
        for i in range(4):
            for j in range(6):
                self.tableau[i].append(self.deck.pop())
        for i in range(4, 10):
            for j in range(5):
                self.tableau[i].append(self.deck.pop())
        
        for pile in self.tableau:
            if pile:
                pile[-1].face_up = True
        
        self.stock = self.deck
        self.stock_pos = STOCK_POSITION
        self.selected_cards = []
        self.selected_pile = None
        self.dragging = False
        self.drag_offset = (0, 0)
        self.completed_sequences = 0
    
    def show_menu(self):
        screen.fill(BACKGROUND_COLOR)
        font = pygame.font.SysFont('arial', 50)
        title = font.render("Spider Solitaire", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//3))
        
        font = pygame.font.SysFont('arial', 30)
        subtitle = font.render("Choose your difficulty:", True, WHITE)
        screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, SCREEN_HEIGHT//2 - 100))
        
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.check_hover(mouse_pos)
            button.draw()
        
        pygame.display.flip()
    
    def deal_from_stock(self):
        if len(self.stock) >= 10:
            for i in range(10):
                card = self.stock.pop()
                card.face_up = True
                self.tableau[i].append(card)
            return True
        return False
    
    def can_stack(self, card1, card2):
        """Check if card1 can be placed on card2 (one rank higher, same suit)"""
        return card1.rank == card2.rank - 1 and card1.suit == card2.suit
    
    def check_sequence(self, pile_index):
        """Check if a complete sequence (King to Ace) exists at top of pile"""
        pile = self.tableau[pile_index]
        if len(pile) < 13:
            return False
            
        # Check if last 13 cards form a sequence
        for i in range(len(pile) - 13, len(pile) - 1):
            if not self.can_stack(pile[i+1], pile[i]):
                return False
        return True
    
    def remove_sequence(self, pile_index):
        """Remove a complete sequence from the pile"""
        if self.check_sequence(pile_index):
            self.tableau[pile_index] = self.tableau[pile_index][:-13]
            self.completed_sequences += 1
            # Turn new top card face up if pile not empty
            if self.tableau[pile_index]:
                self.tableau[pile_index][-1].face_up = True
            return True
        return False
    
    def draw(self):
        if not self.mode:
            self.show_menu()
            return
        
        screen.fill(BACKGROUND_COLOR)
        
        # Draw mode indicator
        font = pygame.font.SysFont('arial', 24)
        mode_text = font.render(f"Mode: {'Single Suit' if self.mode == 'single' else 'Four Suits'}", True, WHITE)
        screen.blit(mode_text, (20, 20))
        
        # Draw restart button
        restart_button = Button(SCREEN_WIDTH - 150, 20, 130, 40, "Restart", self.reset_game)
        restart_button.check_hover(pygame.mouse.get_pos())
        restart_button.draw()
        
        # Draw stock
        if self.stock:
            pygame.draw.rect(screen, CARD_BACK_COLOR, (*self.stock_pos, CARD_WIDTH, CARD_HEIGHT))
            pygame.draw.rect(screen, BLACK, (*self.stock_pos, CARD_WIDTH, CARD_HEIGHT), 2)
            font = pygame.font.SysFont('arial', 20)
            text = font.render(str(len(self.stock)), True, WHITE)
            screen.blit(text, (self.stock_pos[0] + 5, self.stock_pos[1] + 5))
        
        # Draw tableau
        for i, pile in enumerate(self.tableau):
            x = TABLEAU_START_X + i * (CARD_WIDTH + 5)
            if not pile:
                # Draw empty pile outline
                pygame.draw.rect(screen, (0, 100, 0), (x, TABLEAU_START_Y, CARD_WIDTH, CARD_HEIGHT), 2)
            else:
                # Draw cards in pile with vertical offset
                for j, card in enumerate(pile):
                    if self.dragging and i == self.selected_pile and j >= len(pile) - len(self.selected_cards):
                        # Don't draw dragged cards here (they're drawn separately)
                        continue
                    y_offset = j * 20
                    card.draw(x, TABLEAU_START_Y + y_offset)
        
        # Draw dragged cards on top of everything
        if self.dragging and self.selected_cards:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            for i, card in enumerate(self.selected_cards):
                card.draw(mouse_x - self.drag_offset[0], 
                         mouse_y - self.drag_offset[1] + i * 20)
        
        # Draw completed sequences count
        font = pygame.font.SysFont('arial', 30)
        text = font.render(f"Completed Sequences: {self.completed_sequences}/8", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH - 300, 20))
        
        pygame.display.flip()
    
    def handle_click(self, pos):
        # Check if restart button was clicked
        if SCREEN_WIDTH - 150 <= pos[0] <= SCREEN_WIDTH - 20 and 20 <= pos[1] <= 60:
            return
        
        # Check if stock was clicked
        stock_rect = pygame.Rect(*self.stock_pos, CARD_WIDTH, CARD_HEIGHT)
        if stock_rect.collidepoint(pos) and self.stock:
            self.deal_from_stock()
            return
        
        # Check tableau piles
        for i, pile in enumerate(self.tableau):
            if not pile:
                # Check empty pile
                pile_rect = pygame.Rect(
                    TABLEAU_START_X + i * (CARD_WIDTH + 5),
                    TABLEAU_START_Y,
                    CARD_WIDTH,
                    CARD_HEIGHT
                )
                if pile_rect.collidepoint(pos) and self.selected_cards:
                    self.move_cards(self.selected_pile, i)
                    return
            else:
                # Check cards in pile (only top face-up cards can be selected)
                for j in range(len(pile) - 1, -1, -1):
                    if pile[j].face_up:
                        card_rect = pygame.Rect(
                            TABLEAU_START_X + i * (CARD_WIDTH + 5),
                            TABLEAU_START_Y + j * 20,
                            CARD_WIDTH,
                            CARD_HEIGHT
                        )
                        if card_rect.collidepoint(pos):
                            if self.selected_cards:
                                # Try to move cards if we already have a selection
                                self.move_cards(self.selected_pile, i)
                            else:
                                # Select this card and all cards below it in the pile
                                self.selected_pile = i
                                self.selected_cards = pile[j:]
                                self.dragging = True
                                self.drag_offset = (
                                    pos[0] - card_rect.x,
                                    pos[1] - card_rect.y
                                )
                            return
    
    def move_cards(self, from_pile, to_pile):
        if from_pile == to_pile or not self.selected_cards:
            self.dragging = False
            self.selected_cards = []
            self.selected_pile = None
            return
            
        pile = self.tableau[from_pile]
        if not pile:
            self.dragging = False
            self.selected_cards = []
            self.selected_pile = None
            return
            
        # Find index of first selected card in pile
        try:
            index = len(pile) - len(self.selected_cards)
        except ValueError:
            self.dragging = False
            self.selected_cards = []
            self.selected_pile = None
            return
            
        # Check if the move is valid
        target_pile = self.tableau[to_pile]
        if target_pile:
            if not self.can_stack(self.selected_cards[0], target_pile[-1]):
                self.dragging = False
                self.selected_cards = []
                self.selected_pile = None
                return
        elif self.selected_cards[0].rank != 13:  # Only Kings can be placed on empty piles
            self.dragging = False
            self.selected_cards = []
            self.selected_pile = None
            return
            
        # Move the cards
        cards_to_move = pile[index:]
        self.tableau[from_pile] = pile[:index]
        self.tableau[to_pile].extend(cards_to_move)
        
        # Turn new top card face up if pile not empty
        if self.tableau[from_pile]:
            self.tableau[from_pile][-1].face_up = True
        
        # Check for completed sequences
        self.remove_sequence(to_pile)
        
        self.dragging = False
        self.selected_cards = []
        self.selected_pile = None
    
    def check_win(self):
        return self.completed_sequences == 8

def main():
    game = SpiderSolitaire()
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            if not game.mode:
                # Menu screen event handling
                for button in game.buttons:
                    result = button.handle_event(event)
                    if result:
                        break
            else:
                # Game screen event handling
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    game.handle_click(event.pos)
                elif event.type == MOUSEBUTTONUP and event.button == 1:
                    if game.dragging:
                        mouse_pos = pygame.mouse.get_pos()
                        for i in range(10):
                            pile_x = TABLEAU_START_X + i * (CARD_WIDTH + 5)
                            pile_rect = pygame.Rect(
                                pile_x,
                                TABLEAU_START_Y,
                                CARD_WIDTH,
                                SCREEN_HEIGHT - TABLEAU_START_Y
                            )
                            if pile_rect.collidepoint(mouse_pos):
                                game.move_cards(game.selected_pile, i)
                                break
                        else:
                            game.dragging = False
                            game.selected_cards = []
                            game.selected_pile = None
                elif event.type == KEYDOWN:
                    if event.key == K_r:
                        game.reset_game()
                    elif event.key == K_ESCAPE:
                        game.mode = None  # Return to menu
        
        game.draw()
        clock.tick(60)

if __name__ == "__main__":
    main()