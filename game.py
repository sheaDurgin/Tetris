import pygame
from piece import Piece
from board import Board
import os
import sys

cell_size = 40
TOTAL_ROWS = 20
TOTAL_COLS = 10

FPS = 60

screen_width = 800
screen_height = 900

NEXT_PIECE_X = 500
NEXT_PIECE_Y = 1065

SHIFT_DELAY = 16  # Initial delay before repeating the sideways move
SHIFT_INTERVAL = 6  # Interval between repeated sideways moves

RIGHT = 1
LEFT = -1
CLOCKWISE = 1
COUNTER_CLOCKWISE = -1

frames = {
    0: 48, 1: 43, 2: 38, 3: 33, 4: 28, 5: 23, 6: 18, 
    7: 13, 8: 8, 9: 6, 10: 5, 13: 4, 16: 3, 19: 2, 29: 1
}  

offsets = {
    0: (-2, 1), 1: (-1, 1), 2: (0, 1), 3: (1, 1),
    4: (-2, 0), 5: (-1, 0), 6: (0, 0), 7: (1, 0),
    8: (-2, -1), 9: (-1, -1), 10: (0, -1), 11: (1, -1),
    12: (-2, -2), 13: (-1, -2), 14: (0, -2), 15: (1, -2),
}

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class Game:
    def __init__(self, high_score, starting_level):
        self.high_score = high_score
        self.done = False
        pygame.init()
        #self.font = pygame.font.Font(resource_path("ShortBaby-Mg2w.ttf"), 36)
        self.font = pygame.font.SysFont("comicsans", 36)
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.screen.fill("black")
        self.first_level = self.select_level(starting_level)
        self.running = True
        if self.first_level < 0:
            self.done = True
            return
        self.board = Board(self.first_level)

        self.top_left_x = (screen_width - (TOTAL_COLS * cell_size)) // 2
        self.top_left_y = screen_height - (TOTAL_ROWS * cell_size)

        self.pause = False

        self.can_move_left = False
        self.can_move_right = False

        self.curr_piece = Piece(-1)
        self.curr_piece.update_placement(self.curr_piece, self.curr_piece.color, self.board)
        self.next_piece = Piece(self.curr_piece.letter_index)
        self.display_next_piece(self.next_piece)

        self.fall_time = 0

        self.clock = pygame.time.Clock()

        self.draw_border()
        self.display_score()
        self.display_lines_cleared()
        self.display_level()

        self.current_shift_delay = 0
        self.current_shift_interval = 0

        self.speedup = False

        self.is_l_pressed = False
        self.is_j_pressed = False
        self.delay = 60
        self.cleared_lines = False

    def run(self):
        pygame.display.update()
        self.draw_board()
        self.draw_border()
        self.display_high_score()

        self.clock.tick(FPS)

        self.key_presses()
        self.handle_das()

        self.fall()
        self.fall_time += 1

        if self.speedup:
            self.fall_time += 1
    
    def fall(self):
        if self.delay == 0 and self.curr_piece.spawn_delay:
            self.delay = 10
            if self.cleared_lines:
                self.delay = 20

        if self.fall_time >= frames[self.board.frames_index] + self.delay: 
            self.fall_time = 0
            self.curr_piece.move_down(self.board)
            self.curr_piece.spawn_delay = False
            self.delay = 0
    
    def handle_das(self):
        if self.current_shift_delay > 0:
            self.current_shift_delay -= 1
        elif self.current_shift_interval <= 0:
            if self.is_j_pressed:
                if self.curr_piece.move_sideways(LEFT, self.board):
                    self.current_shift_interval = SHIFT_INTERVAL
            elif self.is_l_pressed:
                if self.curr_piece.move_sideways(RIGHT, self.board):
                    self.current_shift_interval = SHIFT_INTERVAL
        elif self.current_shift_interval > 0:
            self.current_shift_interval -= 1
    
    def key_presses(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_j:
                    if self.curr_piece.move_sideways(LEFT, self.board):
                        self.current_shift_delay = SHIFT_DELAY
                    else:
                        self.current_shift_delay = 0
                        self.current_shift_interval = 0
                    self.is_j_pressed = True
                elif event.key == pygame.K_l:
                    if self.curr_piece.move_sideways(RIGHT, self.board):
                        self.current_shift_delay = SHIFT_DELAY
                    else:
                        self.current_shift_delay = 0
                        self.current_shift_interval = 0
                    self.is_l_pressed = True
                elif event.key == pygame.K_k:
                    self.speedup = True
                    self.curr_piece.move_down(self.board)
                
                if event.key == pygame.K_x:
                    self.curr_piece.rotate(CLOCKWISE, self.board)
                elif event.key == pygame.K_z:
                    self.curr_piece.rotate(COUNTER_CLOCKWISE, self.board)

                if event.key == pygame.K_SPACE:
                    if not self.is_l_pressed and not self.is_j_pressed:
                        self.pause = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_k:
                    self.speedup = False

                if event.key == pygame.K_j:
                    self.is_j_pressed = False
                elif event.key == pygame.K_l:
                    self.is_l_pressed = False

                # Reset the counters when either "J" or "L" key is released
                if not self.is_j_pressed and not self.is_l_pressed:
                    self.current_shift_delay = 0
                    self.current_shift_interval = 0

        while self.pause:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.pause = False

    def check_loss(self):
        for idx, block in enumerate(self.curr_piece.orientation):
            if block == '1':
                col_offset, row_offset = offsets[idx]
                spot = (self.curr_piece.col + col_offset, self.curr_piece.row + row_offset)
                if self.board.blocks[spot] != (0, 0, 0):
                    return True

    def draw_board(self):
        for row in range(TOTAL_ROWS):
            for col in range(TOTAL_COLS):
                x = self.top_left_x + col * cell_size
                y = self.top_left_y + (TOTAL_ROWS - row - 1) * cell_size  # Adjust the y-coordinate
                color = self.board.blocks[(col, row)]
                pygame.draw.rect(self.screen, color, (x, y, cell_size, cell_size))
    
    def draw_border(self):
        # Define the border rectangle
        border_rect = pygame.Rect(self.top_left_x, self.top_left_y, (TOTAL_COLS * cell_size), (TOTAL_ROWS * cell_size))

        # Draw the border rectangle
        pygame.draw.rect(self.screen, (255, 255, 255), border_rect, 1)
    
    def display_high_score(self):
        self.display_text(f"High Score", 1.15, 150)
        self.display_text(f"{self.high_score}", 1.15, 185)

    def display_score(self):
        self.display_text(f"Score: {self.board.score}", 1.3)

    def display_lines_cleared(self):
        self.display_text(f"Lines: {self.board.lines_cleared}", 4)
    
    def display_text(self, text_string, x_constant, y_constant=0):
        text = self.font.render(text_string, True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.center = (screen_width // x_constant, 50 + y_constant)

        pygame.draw.rect(self.screen, (0, 0, 0), (text_rect.left, text_rect.top, text_rect.width, text_rect.height))

        self.screen.blit(text, text_rect)

    def display_level(self):
        self.display_text(f"Level: {self.board.level}", 2)

    def display_next_piece(self, piece):
        # Clear the area where the next piece will be displayed
        pygame.draw.rect(self.screen, (0, 0, 0), (NEXT_PIECE_X + 110, NEXT_PIECE_Y - 665, 200, 100))
        
        # Draw the next piece
        for idx, block in enumerate(piece.orientation):
            if block == '1':
                col_offset, row_offset = offsets[idx]
                spot = (piece.col + col_offset, piece.row + row_offset)
                pygame.draw.rect(self.screen, piece.color, (NEXT_PIECE_X + spot[0] * cell_size, NEXT_PIECE_Y + 75 - (spot[1] * cell_size), cell_size, cell_size))

    def select_level(self, starting_level):
        pygame.display.set_caption("Select Level")

        selected_level = starting_level
        levels = 30
        text_color = (255, 255, 255)
        background_color = (0, 0, 0)

        key_delay = 125  # Delay in milliseconds between key presses
        key_timer = 0

        clock = pygame.time.Clock()

        while True:
            keys = pygame.key.get_pressed()

            key_timer += clock.tick()

            if key_timer >= key_delay:
                if keys[pygame.K_j]:
                    selected_level = (selected_level - 1) % levels
                    key_timer = 0  # Reset the key timer

                if keys[pygame.K_l]:
                    selected_level = (selected_level + 1) % levels
                    key_timer = 0  # Reset the key timer

            if keys[pygame.K_RETURN]:
                return selected_level

            # Clear the screen
            self.screen.fill(background_color)

            # Display the selected level
            text = self.font.render(f"Selected Level: {selected_level}", True, text_color)
            text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2))
            self.screen.blit(text, text_rect)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
                    pygame.quit()
                    return -1