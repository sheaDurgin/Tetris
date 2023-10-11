import pygame
from piece import Piece
from board import Board

cell_size = 40
TOTAL_ROWS = 20
TOTAL_COLS = 10

screen_width = 800
screen_height = 900

NEXT_PIECE_X = 500
NEXT_PIECE_Y = 1065

SHIFT_DELAY = 16  # Initial delay before repeating the sideways move
SHIFT_INTERVAL = 5  # Interval between repeated sideways moves

RIGHT = 1
LEFT = -1
CLOCKWISE = 1
COUNTER_CLOCKWISE = -1

frames = {
    0: 48, 1: 43, 2: 38, 3: 33, 4: 28, 5: 23, 6: 18, 
    7: 13, 8: 8, 9: 6, 10: 5, 11: 5, 12: 5, 13: 4, 
    14: 4, 15: 4, 16: 3, 17: 3, 18: 3, 19: 2, 29: 1
}  

offsets = {
    0: (-2, 1), 1: (-1, 1), 2: (0, 1), 3: (1, 1),
    4: (-2, 0), 5: (-1, 0), 6: (0, 0), 7: (1, 0),
    8: (-2, -1), 9: (-1, -1), 10: (0, -1), 11: (1, -1),
    12: (-2, -2), 13: (-1, -2), 14: (0, -2), 15: (1, -2),
}

class Game:
    def __init__(self):
        pygame.init()
        self.board = Board(self.select_level())
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.screen.fill("black")

        self.top_left_x = (screen_width - (TOTAL_COLS * cell_size)) // 2
        self.top_left_y = screen_height - (TOTAL_ROWS * cell_size)

        self.running = True

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

        self.current_shift_delay = 0  # Counter for delay
        self.current_shift_interval = 0  # Counter for interval

        self.speedup = False

        self.is_l_pressed = False
        self.is_j_pressed = False

    def run(self):
        self.draw_board()
        self.draw_border()

        # Get the elapsed time in seconds since the last frame
        dt = self.clock.tick(60) / 1000

        self.fall_time += dt
        frames_index = self.board.level
        if frames_index >= 29:
            frames_index = 29
        elif frames_index >= 19:
            frames_index = 19
        if self.fall_time >= (1.0 / 60) * frames[frames_index] * 3:  # 1.0/60 represents 1 frame at 60 FPS
            self.fall_time = 0
            self.curr_piece.move_down(self.board)

        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_j:
                    self.curr_piece.move_sideways(LEFT, self.board)
                    self.current_shift_delay = SHIFT_DELAY
                    self.is_j_pressed = True
                elif event.key == pygame.K_l:
                    self.curr_piece.move_sideways(RIGHT, self.board)
                    self.current_shift_delay = SHIFT_DELAY
                    self.is_l_pressed = True
                elif event.key == pygame.K_k:
                    self.speedup = True
                    self.curr_piece.move_down(self.board)
                
                if event.key == pygame.K_x:
                    self.curr_piece.rotate(CLOCKWISE, self.board)
                elif event.key == pygame.K_z:
                    self.curr_piece.rotate(COUNTER_CLOCKWISE, self.board)

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

        if not self.curr_piece.can_move:
            if self.is_j_pressed:
                self.curr_piece.move_sideways(LEFT, self.board)
            if self.is_l_pressed:
                self.curr_piece.move_sideways(RIGHT, self.board)
            self.board.score += self.board.calculate_points(self.board.clear_lines())

            self.display_score()
            self.display_lines_cleared()
            self.display_level()

            self.speedup = False
            self.curr_piece = self.next_piece
            if self.check_loss():
                self.running = False
            self.curr_piece.update_placement(self.curr_piece, self.curr_piece.color, self.board)
            self.next_piece = Piece(self.curr_piece.letter_index)

            self.display_next_piece(self.next_piece)

        # Handle sideways autoshift
        if self.current_shift_delay > 0:
            self.current_shift_delay -= 1
        elif self.current_shift_interval == 0:
            # If the delay is over and it's time for the next shift
            if keys[pygame.K_j] and self.is_j_pressed:
                self.curr_piece.move_sideways(LEFT, self.board)
            elif keys[pygame.K_l] and self.is_l_pressed:
                self.curr_piece.move_sideways(RIGHT, self.board)
            self.current_shift_interval = SHIFT_INTERVAL
        elif self.current_shift_interval > 0:
            self.current_shift_interval -= 1

        if self.speedup:
            self.fall_time += dt * (100 - self.board.level * 2)
        else:
            self.fall_time += dt

        pygame.display.update()

        return self.running, self.board.score

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

    def display_score(self):
        font = pygame.font.Font(None, 36)
        text = font.render(f"Score: {self.board.score}", True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.center = (screen_width // 1.3, 50)

        pygame.draw.rect(self.screen, (0, 0, 0), (text_rect.left, text_rect.top, text_rect.width, text_rect.height))

        self.screen.blit(text, text_rect)

    def display_lines_cleared(self):
        font = pygame.font.Font(None, 36)
        text = font.render(f"Lines: {self.board.lines_cleared}", True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.center = (screen_width // 4, 50)

        pygame.draw.rect(self.screen, (0, 0, 0), (text_rect.left, text_rect.top, text_rect.width, text_rect.height))

        self.screen.blit(text, text_rect)

    def display_level(self):
        font = pygame.font.Font(None, 36)
        text = font.render(f"Level: {self.board.level}", True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.center = (screen_width // 2, 50)

        pygame.draw.rect(self.screen, (0, 0, 0), (text_rect.left, text_rect.top, text_rect.width, text_rect.height))

        self.screen.blit(text, text_rect)

    def display_next_piece(self, piece):
        # Clear the area where the next piece will be displayed
        pygame.draw.rect(self.screen, (0, 0, 0), (NEXT_PIECE_X + 110, NEXT_PIECE_Y - 665, 200, 100))
        
        # Draw the next piece
        for idx, block in enumerate(piece.orientation):
            if block == '1':
                col_offset, row_offset = offsets[idx]
                spot = (piece.col + col_offset, piece.row + row_offset)
                pygame.draw.rect(self.screen, piece.color, (NEXT_PIECE_X + spot[0] * cell_size, NEXT_PIECE_Y + 100 - (spot[1] * cell_size), cell_size, cell_size))

    def select_level(self):
        pygame.init()
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Select Level")

        selected_level = 0  # Initial selected level
        levels = 30  # Total number of levels
        font = pygame.font.Font(None, 36)  # Font for displaying the level
        text_color = (255, 255, 255)  # White text color
        background_color = (0, 0, 0)  # Black background color

        key_delay = 125  # Delay in milliseconds between key presses
        key_timer = 0

        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

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
            screen.fill(background_color)

            # Display the selected level
            text = font.render(f"Selected Level: {selected_level}", True, text_color)
            text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(text, text_rect)

            pygame.display.update()