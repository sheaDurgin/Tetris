import copy
import random

TOTAL_ROWS = 20
TOTAL_COLS = 10

START_COL = TOTAL_COLS / 2
START_ROW = TOTAL_ROWS - 1

colors = {
    'i': (200,200,255), 'o': (200,200,255), 't': (200,200,255),
    'l': (255, 0, 0), 'z': (255,0,0),
    'j': (0, 0, 255), 's': (0,0,255)
}

offsets = {
    0: (-2, 2), 1: (-1, 2), 2: (0, 2), 3: (1, 2),
    4: (-2, 1), 5: (-1, 1), 6: (0, 1), 7: (1, 1),
    8: (-2, 0), 9: (-1, 0), 10: (0, 0), 11: (1, 0),
    12: (-2, -1), 13: (-1, -1), 14: (0, -1), 15: (1, -1),
}

shapes = ['i', 'o', 't', 'l', 'j', 's', 'z']

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
        '0000000001100110'
    ],
    't':
    [
        '0000000001110010',
        '0000001001100010',
        '0000001001110000',
        '0000001000110010'
    ],
    'l':
    [
        '0000000001110100',
        '0000011000100010',
        '0000000101110000',
        '0000001000100011'
    ],
    'j':
    [
        '0000000001110001',
        '0000001000100110',
        '0000010001110000',
        '0000001100100010'
    ],
    's':
    [
        '0000000000110110',
        '0000001000110001',
    ],
    'z':
    [
        '0000000001100011',
        '0000000100110010',
    ]
}

def get_new_letter(prev_piece_index):
    new_piece = random.randint(0, 7)
    if new_piece == 7 or shapes[new_piece] == prev_piece_index:
        new_piece = random.randint(0, 6)

    return shapes[new_piece], new_piece

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
        self.spawn_delay = True

    def can_move_down(self, board):
        before_piece = copy.deepcopy(self)
        self.row -= 1
        val = True
        if not self.check_and_update_placement(before_piece, board, False):
            val = False
        self.row += 1
        return val
        
    def move_down(self, board):
        before_piece = copy.deepcopy(self)
        self.row -= 1

        if not self.check_and_update_placement(before_piece, board):
            self.row += 1
            self.can_move = False

    # direction is 1 (right) or -1 (left)
    def move_sideways(self, direction, board):
        before_piece = copy.deepcopy(self)
        self.col += direction
        if not self.check_and_update_placement(before_piece, board):
            self.col -= direction
            return False
        return True
    
    # direction is 1 (clockwise) or -1 (counter clockwise)
    def rotate(self, direction, board):
        before_piece = copy.deepcopy(self)
        original_orientation = self.orientations_index
        
        self.orientations_index = (self.orientations_index + direction) % len(self.orientations)
        self.orientation = self.orientations[self.orientations_index]
        
        if not self.check_and_update_placement(before_piece, board):
            self.orientations_index = original_orientation
            self.orientation = self.orientations[self.orientations_index]

    def update_placement(self, piece, color, board):
        for idx, block in enumerate(piece.orientation):
            if block == '1':
                col_offset, row_offset = offsets[idx]
                spot = (piece.col + col_offset, piece.row + row_offset)
                if spot[1] >= TOTAL_ROWS:
                    continue
                board.blocks[spot] = color

    def check_and_update_placement(self, before_piece, board, update=True):
        seen_spots = []
        for idx, block in enumerate(before_piece.orientation):
            if block == '1':
                col_offset, row_offset = offsets[idx]
                spot = (before_piece.col + col_offset, before_piece.row + row_offset)
                seen_spots.append(spot)

        for idx, block in enumerate(self.orientation):
            if block == '1':
                col_offset, row_offset = offsets[idx]
                spot = (self.col + col_offset, self.row + row_offset)
                if spot[0] >= TOTAL_COLS or spot[0] < 0 or spot[1] < 0:
                    return False
                if spot[1] >= TOTAL_ROWS:
                    continue
                if board.blocks[spot] != (0, 0, 0) and spot not in seen_spots:
                    return False

        if update:
            self.update_placement(before_piece, (0, 0, 0), board)
            self.update_placement(self, self.color, board)

        return True