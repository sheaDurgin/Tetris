import pygame
from piece import Piece
from board import Board

cell_size = 40
TOTAL_ROWS = 20
TOTAL_COLS = 10

FPS = 60

screen_width = 800
screen_height = 900

NEXT_PIECE_X = 500
NEXT_PIECE_Y = 1065

SHIFT_DELAY = int(16 * 16.67)  # Initial delay before repeating the sideways move
SHIFT_INTERVAL = int(6 * 16.67)   # Interval between repeated sideways moves

# PIECE_LAND_DELAY = int(9 * 16.67)
# CLEARED_LINES_DELAY = int(19 * 16.67) / 5
# PIECE_LAND_DELAY = 
# CLEARED_LINES_DELAY = PIECE_L

RIGHT = 1
LEFT = -1
CLOCKWISE = 1
COUNTER_CLOCKWISE = -1

KEY_DELAYS = {}

RIGHT_KEY = pygame.K_k
LEFT_KEY = pygame.K_j
DOWN_KEY = pygame.K_l
ROTATE_CLOCKWISE_KEY = pygame.K_x
ROTATE_COUNTER_CLOCKWISE_KEY = pygame.K_z
PAUSE_KEY = pygame.K_SPACE

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

col_tuples = [(4,5),(3,6),(2,7),(1,8),(0,9)]

class Game:
    def __init__(self, high_score, starting_level):
        self.high_score = high_score
        self.done = False
        pygame.init()

        self.clock = pygame.time.Clock()

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

        self.draw_border()
        self.display_score()
        self.display_lines_cleared()
        self.display_level()

        self.current_shift_delay = 0
        self.current_shift_interval = 0

        self.speedup = False

        self.delay = 60
        self.lock_delay = 0
        self.cleared_lines = False

    def run(self):
        if not self.curr_piece.can_move_down(self.board) and self.lock_delay >= 3:
            self.piece_landed()
        else:
            self.lock_delay += 1
        
        self.draw_board()
        self.draw_border()
        self.display_high_score()

        self.key_presses()

        self.fall()
        self.fall_time += 1
        pygame.display.update()

        if self.speedup:
            self.fall_time += 1
        self.clock.tick(FPS)

    def piece_landed(self):
        lines_cleared, rows_cleared = self.board.clear_lines()
        self.curr_piece.get_lowest_row()
        delay = 10
        cnt = 0
        while self.curr_piece.lowest_row > 1:
            cnt += 1
            delay += 2
            self.curr_piece.lowest_row -= 4
        if lines_cleared > 0:
            self.cleared_lines = True
            delay += cnt
            self.display_line_clear_animation(rows_cleared, delay)
        else:
            self.cleared_lines = False
            timer = 0
            while timer < delay * 16.67:
                self.key_presses(False)
                timer += self.clock.tick()

        self.board.score += self.board.calculate_points(lines_cleared)

        self.display_score()
        self.display_lines_cleared()
        self.display_level()
        pygame.display.update()

        self.speedup = False
        self.curr_piece = self.next_piece
        
        if self.check_loss():
            self.running = False

        self.curr_piece.update_placement(self.curr_piece, self.curr_piece.color, self.board)
        self.next_piece = Piece(self.curr_piece.letter_index)

        self.display_next_piece(self.next_piece)
    
    def fall(self):
        if self.delay == 0 and self.curr_piece.spawn_delay:
            self.delay = 10
            if self.cleared_lines:
                self.delay = 20

        if self.fall_time >= frames[self.board.frames_index] + self.delay and self.curr_piece.can_move_down(self.board): 
            self.fall_time = 0
            self.curr_piece.move_down(self.board)
            if not self.curr_piece.can_move_down(self.board):
                self.lock_delay = 0
            self.curr_piece.spawn_delay = False
            self.delay = 0
    
    def key_presses(self, update=True):
        keys = pygame.key.get_pressed()
        if keys[LEFT_KEY] and RIGHT_KEY not in KEY_DELAYS:
            if LEFT_KEY in KEY_DELAYS:
                curr_time = pygame.time.get_ticks()
                if curr_time >= KEY_DELAYS[LEFT_KEY]:
                    if self.curr_piece.move_sideways(LEFT, self.board, update):
                        self.lock_delay = 0
                        KEY_DELAYS[LEFT_KEY] = curr_time + SHIFT_INTERVAL
            else:
                curr_time = pygame.time.get_ticks()
                if self.curr_piece.move_sideways(LEFT, self.board, update):
                    self.lock_delay = 0
                    KEY_DELAYS[LEFT_KEY] = curr_time + SHIFT_DELAY
                else: 
                    KEY_DELAYS[LEFT_KEY] = curr_time
                
        elif keys[RIGHT_KEY] and LEFT_KEY not in KEY_DELAYS:
            if RIGHT_KEY in KEY_DELAYS:
                curr_time = pygame.time.get_ticks()
                if curr_time >= KEY_DELAYS[RIGHT_KEY]:
                    if self.curr_piece.move_sideways(RIGHT, self.board, update):
                        self.lock_delay = 0
                        KEY_DELAYS[RIGHT_KEY] = curr_time + SHIFT_INTERVAL
            else:
                curr_time = pygame.time.get_ticks()
                if self.curr_piece.move_sideways(RIGHT, self.board, update):
                    self.lock_delay = 0  
                    KEY_DELAYS[RIGHT_KEY] = curr_time + SHIFT_DELAY
                else:
                    KEY_DELAYS[RIGHT_KEY] = curr_time

        elif keys[DOWN_KEY]:
            self.speedup = True
            self.curr_piece.move_down(self.board, update)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == ROTATE_CLOCKWISE_KEY:
                    self.curr_piece.rotate(CLOCKWISE, self.board, update)
                elif event.key == ROTATE_COUNTER_CLOCKWISE_KEY:
                    self.curr_piece.rotate(COUNTER_CLOCKWISE, self.board, update)
                elif event.key == PAUSE_KEY:
                    self.pause = True
            
            if event.type == pygame.KEYUP:
                if event.key == LEFT_KEY:
                    KEY_DELAYS.pop(LEFT_KEY, None)
                elif event.key == RIGHT_KEY:
                    KEY_DELAYS.pop(RIGHT_KEY, None)
                elif event.key == DOWN_KEY:
                    self.speedup = False

        while self.pause:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == PAUSE_KEY:
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
                y = self.top_left_y + (TOTAL_ROWS - row - 1) * cell_size
                color = self.board.blocks[(col, row)]
                pygame.draw.rect(self.screen, color, (x, y, cell_size, cell_size))

    def display_line_clear_animation(self, rows_cleared, delay):
        color = (0, 0, 0)
        delay *= 16.67/5
        for col_tuple in col_tuples:
            lx = self.top_left_x + col_tuple[0] * cell_size
            rx = self.top_left_x + col_tuple[1] * cell_size
            for row, val in enumerate(rows_cleared):
                if val is False:
                    continue
                y = self.top_left_y + (TOTAL_ROWS - row - 1) * cell_size
                pygame.draw.rect(self.screen, color, (lx, y, cell_size, cell_size))
                pygame.draw.rect(self.screen, color, (rx, y, cell_size, cell_size))
            pygame.display.update()

            timer = 0
            while timer < delay:
                self.key_presses(False)
                timer += self.clock.tick()
    
    def draw_border(self):
        # Define the border rectangle
        border_rect = pygame.Rect(self.top_left_x, self.top_left_y, (TOTAL_COLS * cell_size), (TOTAL_ROWS * cell_size))

        # Draw the border rectangle
        pygame.draw.rect(self.screen, (255, 255, 255), border_rect, 1)
    
    def display_high_score(self):
        self.display_text(f"High Score", 1.15, 125)
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

        pygame.display.update()

    def select_level(self, starting_level):
        pygame.display.set_caption("Select Level")

        selected_level = starting_level
        levels = 30
        text_color = (255, 255, 255)
        background_color = (0, 0, 0)

        key_delay = 125  # Delay in milliseconds between key presses
        key_timer = 0

        while True:
            keys = pygame.key.get_pressed()

            key_timer += self.clock.tick()

            if key_timer >= key_delay:
                if keys[LEFT_KEY]:
                    selected_level = (selected_level - 1) % levels
                    key_timer = 0  # Reset the key timer

                if keys[RIGHT_KEY]:
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