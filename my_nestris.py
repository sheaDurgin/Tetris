from game import Game
from piece import Piece
import os
import pygame

def main(starting_level):
    # Read scores from scores.txt and keep them sorted in descending order
    scores = read_scores()
    scores.sort(reverse=True)
    game = Game(scores[0], starting_level)
    if game.done:
        return -1
    while game.running:
        game.run()
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

    while starting_level != -1:
        starting_level = main(starting_level)
