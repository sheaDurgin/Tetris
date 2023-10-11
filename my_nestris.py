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
        '0100011000100000',
    ],
    'z':
    [
        '0000011000110000',
        '0010011001000000',
    ]
}

colors = {
    'i': (255,255,255),
    'o': (0, 0, 255),
    't': (255, 0, 0),
    'l': (0, 0, 255),
    'j': (255, 0, 0),
    's': (255,255,255),
    'z': (255,255,255),
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
            
            if spot[0] >= TOTAL_COLS or spot[0] < 0 or spot[1] < 0 or spot[1] >= TOTAL_ROWS or (board.blocks[spot] != (0, 0, 0) and spot not in seen_spots):
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
    def __init__(self):
        self.blocks = {(col, row): (0, 0, 0) for col in range(10) for row in range(20)}
        
        # time in seconds that a piece falls one block
        self.gravity = 0.2
    
    def increase_gravity(self):
        if self.gravity >= 0.02:
            self.gravity -= 0.01
        else:
            self.gravity /= 2

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

board = Board()

# pygame setup
pygame.init()

screen_length = 800
screen_height = 900
screen = pygame.display.set_mode((screen_length, screen_height))

grid_length = 400
grid_height = 800

top_left_x = (screen_length - grid_length) // 2
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

def calculate_points(level, lines_cleared):
    

def main():
    screen.fill("black")

    running = True

    curr_piece = Piece(-1)
    update_placement(curr_piece, curr_piece.color)
    next_piece = Piece(curr_piece.letter_index)

    fall_time = 0

    clock = pygame.time.Clock()
    dt = 0

    draw_border()

    score = 0

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

        # PIECE FALLING CODE
        fall_time += dt  # Use dt to control the falling speed
        if fall_time >= board.gravity:
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
            board.clear_lines()
            speedup = False
            curr_piece = next_piece
            if check_loss(curr_piece):
                running = False
            update_placement(curr_piece, curr_piece.color)
            next_piece = Piece(curr_piece.letter_index)

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
            fall_time += dt * 4  # Increase falling speed when "K" key is held down
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