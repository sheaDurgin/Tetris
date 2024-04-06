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
        self.curr_piece.delay = 60
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

        self.cleared_lines = False
        self.first_piece_delay = pygame.time.get_ticks()

    def run(self):        
        self.draw_for_run()

        self.key_presses()
        
        self.fall()
        
        self.clock.tick(FPS)

    def piece_landed(self):
        pygame.display.update()
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
            delay += cnt + 17
            self.display_line_clear_animation(rows_cleared, delay)
        else:
            self.cleared_lines = False
            self.delay_after_landing(delay * 16.67)

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
        inc_fall_time = True
        
        if self.speedup:
            self.fall_time += 1

        if self.fall_time >= frames[self.board.frames_index] + self.curr_piece.delay: 
            if self.curr_piece.can_move_down(self.board):
                self.curr_piece.delay = 0
                self.fall_time = 0
                self.curr_piece.move_down(self.board)
            else:
                inc_fall_time = False
                self.piece_landed()

        if inc_fall_time:
            self.fall_time += 1

        pygame.display.update()
    
    def draw_for_run(self):
        self.draw_board()
        self.draw_border()
        self.display_high_score()
        pygame.display.update()

    def sideways(self, key, dir, update):
        if key in KEY_DELAYS:
            curr_time = pygame.time.get_ticks()
            if curr_time >= KEY_DELAYS[key]:
                if self.curr_piece.move_sideways(dir, self.board, update):
                    KEY_DELAYS[key] = curr_time + SHIFT_INTERVAL
        else:
            curr_time = pygame.time.get_ticks()
            if self.curr_piece.move_sideways(dir, self.board, update):
                KEY_DELAYS[key] = curr_time + SHIFT_DELAY
            else: 
                KEY_DELAYS[key] = curr_time
    
    def key_presses(self, update=True):
        keys = pygame.key.get_pressed()
        if keys[LEFT_KEY] and RIGHT_KEY not in KEY_DELAYS:
            self.sideways(LEFT_KEY, LEFT, update)
                
        elif keys[RIGHT_KEY] and LEFT_KEY not in KEY_DELAYS:
            self.sideways(RIGHT_KEY, RIGHT, update)

        elif keys[DOWN_KEY]:
            self.speedup = True

        pygame.display.update()

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
        
        pygame.display.update()

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

    def delay_after_landing(self, delay):
        end_time = pygame.time.get_ticks() + delay
        while pygame.time.get_ticks() < end_time:
            self.key_presses(False)
        pygame.display.update()

    def display_line_clear_animation(self, rows_cleared, delay):
        color = (0, 0, 0)
        delay *= 16.67/6
        for col_tuple in col_tuples:
            lx = self.top_left_x + col_tuple[0] * cell_size
            rx = self.top_left_x + col_tuple[1] * cell_size
            for row, val in enumerate(rows_cleared):
                if val is False:
                    continue
                y = self.top_left_y + (TOTAL_ROWS - row - 1) * cell_size
                pygame.draw.rect(self.screen, color, (lx, y, cell_size, cell_size))
                pygame.draw.rect(self.screen, color, (rx, y, cell_size, cell_size))

            self.delay_after_landing(delay)

        self.delay_after_landing(delay)    
    
    def draw_border(self):
        border_rect = pygame.Rect(self.top_left_x, self.top_left_y, (TOTAL_COLS * cell_size), (TOTAL_ROWS * cell_size))
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
        pygame.draw.rect(self.screen, (0, 0, 0), (NEXT_PIECE_X + 110, NEXT_PIECE_Y - 665, 200, 100))
        
        for idx, block in enumerate(piece.orientation):
            if block == '1':
                col_offset, row_offset = offsets[idx]
                spot = (piece.col + col_offset, piece.row + row_offset)
                pygame.draw.rect(self.screen, piece.color, (NEXT_PIECE_X + spot[0] * cell_size, NEXT_PIECE_Y + 75 - (spot[1] * cell_size), cell_size, cell_size))

        pygame.display.update()

    def select_level(self, starting_level):
        pygame.display.set_caption("Select Level With Enter Key")

        selected_level = starting_level
        levels = 30
        text_color = (255, 255, 255)
        background_color = (0, 0, 0)

        key_timer = pygame.time.get_ticks()
        key_delay = key_timer + 100

        while True:
            keys = pygame.key.get_pressed()

            key_timer = pygame.time.get_ticks()

            if key_timer >= key_delay:
                key_timer = pygame.time.get_ticks()
                key_delay = key_timer + 100
                if keys[LEFT_KEY]:
                    selected_level = (selected_level - 1) % levels
                elif keys[RIGHT_KEY]:
                    selected_level = (selected_level + 1) % levels

            if keys[pygame.K_RETURN]:
                return selected_level

            self.screen.fill(background_color)

            text = self.font.render(f"Selected Level: {selected_level}", True, text_color)
            text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2))
            self.screen.blit(text, text_rect)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
                    pygame.quit()
                    return -1