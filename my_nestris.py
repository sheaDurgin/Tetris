import random
import copy
import pygame

START_COL = 5
START_ROW = 19

# 0 -> 9
TOTAL_COLS = 10
# 0 -> 19
TOTAL_ROWS = 20

CLOCKWISE = 1
RIGHT = 1
COUNTER_CLOCKWISE = -1
LEFT = -1

shapes = ['i', 'o', 't', 'l', 'j', 's', 'z']

offsets = {
    0: (-2, 1),
    1: (-1, 1),
    2: (0, 1),
    3: (1, 1),
    4: (-2, 0),
    5: (-1, 0),
    6: (0, 0),
    7: (1, 0),
    8: (-2, -1),
    9: (-1, -1),
    10: (0, -1),
    11: (1, -1),
    12: (-2, -2),
    13: (-1, -2),
    14: (0, -2),
    15: (1, -2),
}

# 0  1  2  3
# 4  5  6  7
# 8  9  10 11
# 12 13 14 15
shape_orientations = {
    'i':
    [
        '0000000011110000',
        '0010001000100010'
    ],
    'o': 
    [
        '0000011001100000'
    ],
    't':
    [
        '0000011100100000',
        '0010011000100000',
        '0010011100000000',
        '0010001100100000'
    ],
    'l':
    [
        '0000011101000000',
        '0110001000100000',
        '0001011100000000',
        '0010001000110000'
    ],
    'j':
    [
        '0000011100010000',
        '0010001001100000',
        '0100011100000000',
        '0011001000100000'
    ],
    's':
    [
        '0000001101100000',
        '0000001000110001',
    ],
    'z':
    [
        '0000011000110000',
        '0000000100110010',
    ]
}

colors = {
    'i': (200,200,255),
    'o': (200,200,255),
    't': (200,200,255),
    'l': (255, 0, 0),
    'j': (0, 0, 255),
    's': (0,0,255),
    'z': (255,0,0),
}

frames = {
    0: 48,
    1: 43,
    2: 38,
    3: 33,
    4: 28,
    5: 23,
    6: 18,
    7: 13,
    8: 8,
    9: 6,
    10: 5,
    11: 5,
    12: 5,
    13: 4,
    14: 4,
    15: 4,
    16: 3,
    17: 3,
    18: 3,
    19: 2,
    29: 1
}

level_delay = {
    0: 10,
    1: 20,
    2: 30,
    3: 40,
    4: 50,
    5: 60,
    6: 70,
    7: 80,
    8: 90,
    9: 100,
    10: 100,
    11: 100,
    12: 100,
    13: 100,
    14: 100,
    15: 100,
    16: 110,
    17: 120,
    18: 130,
    19: 140,
    20: 150,
    21: 160,
    22: 170,
    23: 180,
    24: 190,
    25: 200,
    26: 200,
    27: 200,
    28: 200,
    29: 200
}

def get_new_letter(prev_piece_index):
    new_piece = random.randint(0, 7)
    if new_piece == 7 or shapes[new_piece] == prev_piece_index:
        new_piece = random.randint(0, 6)

    return shapes[new_piece], new_piece

def update_placement(piece, color):
    for idx, block in enumerate(piece.orientation):
        if block == '1':
            col_offset, row_offset = offsets[idx]
            spot = (piece.col + col_offset, piece.row + row_offset)
            if spot[1] >= TOTAL_ROWS:
                continue
            board.blocks[spot] = color

def check_and_update_placement(piece, before_piece):
    seen_spots = []
    for idx, block in enumerate(before_piece.orientation):
        if block == '1':
            col_offset, row_offset = offsets[idx]
            spot = (before_piece.col + col_offset, before_piece.row + row_offset)
            seen_spots.append(spot)

    for idx, block in enumerate(piece.orientation):
        if block == '1':
            col_offset, row_offset = offsets[idx]
            spot = (piece.col + col_offset, piece.row + row_offset)
            
            if spot[0] >= TOTAL_COLS or spot[0] < 0 or spot[1] < 0:
                return False
            if spot[1] >= TOTAL_ROWS:
                continue
            if board.blocks[spot] != (0, 0, 0) and spot not in seen_spots:
                return False
            
    update_placement(before_piece, (0, 0, 0))
    update_placement(piece, piece.color)

    return True

def check_loss(piece):
    for idx, block in enumerate(piece.orientation):
        if block == '1':
            col_offset, row_offset = offsets[idx]
            spot = (piece.col + col_offset, piece.row + row_offset)
            
            if board.blocks[spot] != (0, 0, 0):
                return True

class Piece:
    def __init__(self, prev_piece_index):
        self.col = START_COL
        self.row = START_ROW
        self.letter, self.letter_index = get_new_letter(prev_piece_index)
        self.color = colors[self.letter]
        self.can_move = True
        # list of binary represenations
        self.orientations = shape_orientations[self.letter]
        # index for current orientation of piece
        self.orientations_index = 0
        # binary represenation of current piece orientation
        self.orientation = self.orientations[self.orientations_index]
        
    def move_down(self):
        if not self.can_move:
            return
        
        before_piece = copy.deepcopy(self)
        self.row -= 1

        if not check_and_update_placement(self, before_piece):
            self.row += 1
            self.can_move = False
  
    # direction is 1 (right) or -1 (left)
    def move_sideways(self, direction):
        if not self.can_move:
            return
        before_piece = copy.deepcopy(self)
        self.col += direction
        if not check_and_update_placement(self, before_piece):
            self.col -= direction
    
    # direction is 1 (clockwise) or -1 (counter clockwise)
    def rotate(self, direction):
        before_piece = copy.deepcopy(self)
        original_orientation = self.orientations_index
        
        self.orientations_index = (self.orientations_index + direction) % len(self.orientations)
        self.orientation = self.orientations[self.orientations_index]
        
        if not check_and_update_placement(self, before_piece):
            self.orientations_index = original_orientation
            self.orientation = self.orientations[self.orientations_index]


class Board:
    def __init__(self, level):
        self.blocks = {(col, row): (0, 0, 0) for col in range(10) for row in range(20)}
        self.score = 0
        self.level = level
        self.lines_cleared = 0
        self.lines_until_level_change = level_delay[self.level]
        
    def clear_lines(self):
        rows_cleared = [False for _ in range(TOTAL_ROWS)]
        for row in range(TOTAL_ROWS):
            clear = True
            for col in range(TOTAL_COLS):
                if self.blocks[(col, row)] == (0, 0, 0):
                    clear = False
                    break

            rows_cleared[row] = clear
        
        # Move lines down
        offset = 0
        for row in range(TOTAL_ROWS):
            if rows_cleared[row]:
                offset += 1
                continue
            elif offset == 0:
                continue

            for col in range(TOTAL_COLS):
                self.blocks[(col, row - offset)] = self.blocks[(col, row)]
                self.blocks[(col, row)] = (0, 0, 0)
        
        return offset

# pygame setup
pygame.init()

screen_width = 800
screen_height = 900
screen = pygame.display.set_mode((screen_width, screen_height))

grid_length = 400
grid_height = 800

top_left_x = (screen_width - grid_length) // 2
top_left_y = screen_height - grid_height

cell_size = 40

def draw_board():
    for row in range(TOTAL_ROWS):
        for col in range(TOTAL_COLS):
            x = top_left_x + col * cell_size
            y = top_left_y + (TOTAL_ROWS - row - 1) * cell_size  # Adjust the y-coordinate
            color = board.blocks[(col, row)]
            pygame.draw.rect(screen, color, (x, y, cell_size, cell_size))

def draw_border():
    # Define the border rectangle
    border_rect = pygame.Rect(top_left_x, top_left_y, grid_length, grid_height)

    # Draw the border rectangle
    pygame.draw.rect(screen, (255, 255, 255), border_rect, 1)

NEXT_PIECE_X = 500
NEXT_PIECE_Y = 1065

def display_next_piece(piece):
    # Clear the area where the next piece will be displayed
    pygame.draw.rect(screen, (0, 0, 0), (NEXT_PIECE_X + 110, NEXT_PIECE_Y - 665, 200, 100))
    
    # Draw the next piece
    for idx, block in enumerate(piece.orientation):
        if block == '1':
            col_offset, row_offset = offsets[idx]
            spot = (piece.col + col_offset, piece.row + row_offset)
            pygame.draw.rect(screen, piece.color, (NEXT_PIECE_X + spot[0] * cell_size, NEXT_PIECE_Y + 100 - (spot[1] * cell_size), cell_size, cell_size))

def display_lines_cleared():
    font = pygame.font.Font(None, 36)
    text = font.render(f"Lines: {board.lines_cleared}", True, (255, 255, 255))
    text_rect = text.get_rect()
    text_rect.center = (screen_width // 4, 50)

    pygame.draw.rect(screen, (0, 0, 0), (text_rect.left, text_rect.top, text_rect.width, text_rect.height))

    screen.blit(text, text_rect)

def display_level():
    font = pygame.font.Font(None, 36)
    text = font.render(f"Level: {board.level}", True, (255, 255, 255))
    text_rect = text.get_rect()
    text_rect.center = (screen_width // 2, 50)

    pygame.draw.rect(screen, (0, 0, 0), (text_rect.left, text_rect.top, text_rect.width, text_rect.height))

    screen.blit(text, text_rect)

def display_score():
    font = pygame.font.Font(None, 36)
    text = font.render(f"Score: {board.score}", True, (255, 255, 255))
    text_rect = text.get_rect()
    text_rect.center = (screen_width // 1.3, 50)

    pygame.draw.rect(screen, (0, 0, 0), (text_rect.left, text_rect.top, text_rect.width, text_rect.height))

    screen.blit(text, text_rect)

score_per_line_cleared = [40, 100, 300, 1200, 0]

def calculate_points(lines_cleared):
    board.lines_cleared += lines_cleared

    if board.lines_until_level_change <= board.lines_cleared:
        board.lines_until_level_change += 10
        board.level += 1

    return score_per_line_cleared[lines_cleared - 1] * (board.level + 1)

def select_level():
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

board = Board(select_level())

def main():
    screen.fill("black")

    running = True

    curr_piece = Piece(-1)
    update_placement(curr_piece, curr_piece.color)
    next_piece = Piece(curr_piece.letter_index)
    display_next_piece(next_piece)

    fall_time = 0

    clock = pygame.time.Clock()
    dt = 0

    draw_border()
    display_score()
    display_lines_cleared()
    display_level()

    SHIFT_DELAY = 16  # Initial delay before repeating the sideways move
    SHIFT_INTERVAL = 5  # Interval between repeated sideways moves
    current_shift_delay = 0  # Counter for delay
    current_shift_interval = 0  # Counter for interval

    speedup = False

    is_l_pressed = False
    is_j_pressed = False

    while running:
        draw_board()
        draw_border()

        # Get the elapsed time in seconds since the last frame
        dt = clock.tick(60) / 1000

        fall_time += dt
        frames_index = board.level
        if frames_index >= 29:
            frames_index = 29
        elif frames_index >= 19:
            frames_index = 19
        if fall_time >= (1.0 / 60) * frames[frames_index] * 3:  # 1.0/60 represents 1 frame at 60 FPS
            fall_time = 0
            curr_piece.move_down()

        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.display.quit()
                print("QUIT")
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_j:
                    curr_piece.move_sideways(LEFT)
                    current_shift_delay = SHIFT_DELAY
                    is_j_pressed = True
                elif event.key == pygame.K_l:
                    curr_piece.move_sideways(RIGHT)
                    current_shift_delay = SHIFT_DELAY
                    is_l_pressed = True
                elif event.key == pygame.K_k:
                    speedup = True
                    curr_piece.move_down()
                
                if event.key == pygame.K_x:
                    curr_piece.rotate(CLOCKWISE)
                elif event.key == pygame.K_z:
                    curr_piece.rotate(COUNTER_CLOCKWISE)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_k:
                    speedup = False

                if event.key == pygame.K_j:
                    is_j_pressed = False
                elif event.key == pygame.K_l:
                    is_l_pressed = False
                # Reset the counters when either "J" or "L" key is released
                if not is_j_pressed and not is_l_pressed:
                    current_shift_delay = 0
                    current_shift_interval = 0

        if not curr_piece.can_move:
            if is_j_pressed:
                curr_piece.move_sideways(LEFT)
            if is_l_pressed:
                curr_piece.move_sideways(RIGHT)
            board.score += calculate_points(board.clear_lines())

            display_score()
            display_lines_cleared()
            display_level()

            speedup = False
            curr_piece = next_piece
            if check_loss(curr_piece):
                running = False
            update_placement(curr_piece, curr_piece.color)
            next_piece = Piece(curr_piece.letter_index)
            # IMPLEMENT NEXT PIECE SCREEN
            display_next_piece(next_piece)

        # Handle sideways autoshift
        if current_shift_delay > 0:
            current_shift_delay -= 1
        elif current_shift_interval == 0:
            # If the delay is over and it's time for the next shift
            if keys[pygame.K_j] and is_j_pressed:
                curr_piece.move_sideways(LEFT)
            elif keys[pygame.K_l] and is_l_pressed:
                curr_piece.move_sideways(RIGHT)
            current_shift_interval = SHIFT_INTERVAL
        elif current_shift_interval > 0:
            current_shift_interval -= 1

        if speedup:
            fall_time += dt * (100 - board.level * 2)
        else:
            fall_time += dt

        pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.display.quit()
                print("QUIT")
                quit()

main()