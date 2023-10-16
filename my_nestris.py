from game import Game
from piece import Piece
import os
import pygame

def piece_landed(game):
    lines_cleared = game.board.clear_lines()
    if lines_cleared > 0:
        game.cleared_lines = True
    else:
        game.cleared_lines = False
    game.board.score += game.board.calculate_points(lines_cleared)

    game.display_score()
    game.display_lines_cleared()
    game.display_level()
    pygame.display.update()

    game.speedup = False
    game.curr_piece = game.next_piece
    
    if game.check_loss():
        game.running = False

    game.curr_piece.update_placement(game.curr_piece, game.curr_piece.color, game.board)
    game.next_piece = Piece(game.curr_piece.letter_index)

    game.display_next_piece(game.next_piece)

def main(starting_level):
    # Read scores from scores.txt and keep them sorted in descending order
    scores = read_scores()
    scores.sort(reverse=True)
    game = Game(scores[0], starting_level)
    if game.done:
            return -1
    while game.running:
        game.run()
        if not game.curr_piece.can_move:
            piece_landed(game)
        if game.done:
            return -1

    # Add the new score to the list
    scores.append(game.board.score)
    scores.sort(reverse=True)  # Sort scores in descending order

    # Write the updated scores back to scores.txt
    write_scores(scores)
    
    return game.first_level

def read_scores():
    scores = []
    if os.path.exists("scores.txt"):
        with open("scores.txt", "r") as file:
            for line in file:
                score = int(line)
                scores.append(score)
    return scores

def write_scores(scores):
    with open("scores.txt", "w") as file:
        for score in scores:
            file.write(str(score) + "\n")

if __name__ == "__main__":
    # Create "scores.txt" if it doesn't exist
    if not os.path.exists("scores.txt"):
        with open("scores.txt", "w") as file:
            file.write("0")
        
    starting_level = 18

    while True:
        starting_level = main(starting_level)
        if starting_level == -1:
            break