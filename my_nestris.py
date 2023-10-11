from game import Game
import os

def main():
    game = Game()
    while True:
        game_on, score = game.run()
        if not game_on:
            break
    
    # Read scores from scores.txt and keep them sorted in descending order
    scores = read_scores()

    # Add the new score to the list
    scores.append(score)
    scores.sort(reverse=True)  # Sort scores in descending order

    # Write the updated scores back to scores.txt
    write_scores(scores)

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
            file.write("")

    while True:
        main()
