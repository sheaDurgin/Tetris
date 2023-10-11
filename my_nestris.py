import pygame
from board import Board
from piece import Piece

# 0 -> 9
TOTAL_COLS = 10
# 0 -> 19
TOTAL_ROWS = 20

CLOCKWISE = 1
RIGHT = 1
COUNTER_CLOCKWISE = -1
LEFT = -1

offsets = {
    0: (-2, 1), 1: (-1, 1), 2: (0, 1), 3: (1, 1),
    4: (-2, 0), 5: (-1, 0), 6: (0, 0), 7: (1, 0),
    8: (-2, -1), 9: (-1, -1), 10: (0, -1), 11: (1, -1),
    12: (-2, -2), 13: (-1, -2), 14: (0, -2), 15: (1, -2),
}

frames = {
    0: 48, 1: 43, 2: 38, 3: 33, 4: 28, 5: 23, 6: 18, 
    7: 13, 8: 8, 9: 6, 10: 5, 11: 5, 12: 5, 13: 4, 
    14: 4, 15: 4, 16: 3, 17: 3, 18: 3, 19: 2, 29: 1
}  

def update_placement(piece, color):
    for idx, block in enumerate(piece.orientation):
        if block == '1':
            col_offset, row_offset = offsets[idx]
            spot = (piece.col + col_offset, piece.row + row_offset)
            if spot[1] >= TOTAL_ROWS:
                continue
            board.blocks[spot] = color

def check_loss(piece):
    for idx, block in enumerate(piece.orientation):
        if block == '1':
            col_offset, row_offset = offsets[idx]
            spot = (piece.col + col_offset, piece.row + row_offset)
            
            if board.blocks[spot] != (0, 0, 0):
                return True

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
            curr_piece.move_down(board)

        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.display.quit()
                print("QUIT")
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_j:
                    curr_piece.move_sideways(LEFT, board)
                    current_shift_delay = SHIFT_DELAY
                    is_j_pressed = True
                elif event.key == pygame.K_l:
                    curr_piece.move_sideways(RIGHT, board)
                    current_shift_delay = SHIFT_DELAY
                    is_l_pressed = True
                elif event.key == pygame.K_k:
                    speedup = True
                    curr_piece.move_down(board)
                
                if event.key == pygame.K_x:
                    curr_piece.rotate(CLOCKWISE, board)
                elif event.key == pygame.K_z:
                    curr_piece.rotate(COUNTER_CLOCKWISE, board)

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
                curr_piece.move_sideways(LEFT, board)
            if is_l_pressed:
                curr_piece.move_sideways(RIGHT, board)
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
                curr_piece.move_sideways(LEFT, board)
            elif keys[pygame.K_l] and is_l_pressed:
                curr_piece.move_sideways(RIGHT, board)
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